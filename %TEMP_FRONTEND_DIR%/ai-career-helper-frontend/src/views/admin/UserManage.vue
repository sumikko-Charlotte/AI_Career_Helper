<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Search, Delete, Edit, UserFilled, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchQuery = ref('')
const tableData = ref([])
const SERVER_API = import.meta.env.VITE_USER_SERVER || 'http://127.0.0.1:3000' // 新增：真实用户服务

// 搜索 / 过滤
import { computed } from 'vue'
const filteredData = computed(() => {
  const q = (searchQuery.value || '').toLowerCase().trim()
  if (!q) return tableData.value
  return tableData.value.filter(u => (
    String(u.id).includes(q) ||
    (u.username || '').toLowerCase().includes(q) ||
    (u.intent || u.role || '').toLowerCase().includes(q)
  ))
})

// 本 Demo 使用 localStorage 保存并管理用户数据，key: competition_user_list
// 同时用 competition_banned_user_ids 存储被禁用的用户 ID 列表

const DEFAULT_USERS = [
  { id: 1001, username: '张三', grade: '大三', school: '清华大学', major: '计算机', intent: '算法', register_time: '2026-01-12 09:23', last_login: '2026-01-25 09:15', status: '正常', avatar: '张' },
  { id: 1002, username: '李四', grade: '研一', school: '北京大学', major: '软件工程', intent: 'Java后端', register_time: '2026-01-14 10:12', last_login: '2026-01-24 17:02', status: '正常', avatar: '李' },
  { id: 1003, username: '王五', grade: '大二', school: '复旦大学', major: '前端', intent: '前端', register_time: '2026-01-10 11:48', last_login: '2026-01-23 14:05', status: '正常', avatar: '王' },
  { id: 1004, username: '赵六', grade: '博士', school: '上海交大', major: '人工智能', intent: '算法', register_time: '2026-01-08 13:33', last_login: '2026-01-22 12:45', status: '正常', avatar: '赵' },
  { id: 1005, username: '钱七', grade: '大四', school: '浙江大学', major: '产品', intent: '产品', register_time: '2026-01-11 08:20', last_login: '2026-01-21 19:10', status: '正常', avatar: '钱' },
  { id: 1006, username: '孙八', grade: '大一', school: '华中科技大学', major: '软件工程', intent: '前端', register_time: '2026-01-18 16:45', last_login: '2026-01-25 11:03', status: '正常', avatar: '孙' },
  { id: 1007, username: '周九', grade: '研二', school: '南京大学', major: '计算机科学', intent: '后端', register_time: '2026-01-19 09:59', last_login: '2026-01-25 09:40', status: '正常', avatar: '周' },
  { id: 1008, username: '吴十', grade: '大四', school: '同济大学', major: '测试', intent: '测试', register_time: '2026-01-16 07:30', last_login: '2026-01-24 21:15', status: '正常', avatar: '吴' },
  { id: 1009, username: '郑十一', grade: '大三', school: '四川大学', major: '运维', intent: '运维', register_time: '2026-01-13 15:00', last_login: '2026-01-23 10:20', status: '正常', avatar: '郑' },
  { id: 1010, username: '何十二', grade: '研一', school: '重庆大学', major: '数据科学', intent: '算法', register_time: '2026-01-15 12:12', last_login: '2026-01-22 08:44', status: '正常', avatar: '何' },
  { id: 1011, username: '曹十三', grade: '大二', school: '华东师范大学', major: '信息管理', intent: '产品', register_time: '2026-01-17 09:05', last_login: '2026-01-25 10:20', status: '正常', avatar: '曹' },
  { id: 1012, username: '穆十四', grade: '大三', school: '北京邮电大学', major: '网络工程', intent: '后端', register_time: '2026-01-09 11:11', last_login: '2026-01-23 18:55', status: '正常', avatar: '穆' },
  { id: 1013, username: '丁十五', grade: '大四', school: '东南大学', major: '计算机', intent: '前端', register_time: '2026-01-06 10:30', last_login: '2026-01-24 09:12', status: '正常', avatar: '丁' },
]

const USER_KEY = 'competition_user_list'
const BANNED_KEY = 'competition_banned_user_ids'

const fetchUsers = async () => {
  loading.value = true
  try {
    // 请求真实用户列表（CSV 持久化）
    const res = await axios.get(`${SERVER_API}/api/users`)
    if (res.data && res.data.code === 200) {
      const real = res.data.data || []
      // 转换为页面期望的字段并标记为真实用户
      const realTrans = real.map((u, idx) => ({
        id: 2000 + idx,
        username: u.username,
        grade: u.grade || '',
        intent: u.target_role || '',
        register_time: u.register_time || '',
        last_login: u.last_login || '',
        status: (u.status === 'normal') ? '正常' : (u.status || '禁用'),
        isReal: true,
        raw: u
      }))

      // 合并：真实用户在前，虚拟样板在后，避免重复用户名
      const merged = [...realTrans]
      DEFAULT_USERS.forEach(v => { if (!merged.find(r => r.username === v.username)) merged.push({ ...v, isVirtual: true }) })
      tableData.value = merged
    } else {
      // 回退：仅使用本地虚拟数据
      const raw = localStorage.getItem(USER_KEY)
      tableData.value = raw ? JSON.parse(raw) : DEFAULT_USERS
    }
  } catch (e) {
    console.warn('获取真实用户失败，使用本地虚拟数据', e)
    const raw = localStorage.getItem(USER_KEY)
    tableData.value = raw ? JSON.parse(raw) : DEFAULT_USERS
  } finally {
    loading.value = false
  }
}

// 封禁/解封用户（同步到 localStorage: competition_banned_user_ids）
const toggleStatus = (row) => {
  const isBan = row.status === '正常'
  const actionText = isBan ? '禁用' : '启用'

  ElMessageBox.confirm(
    `确定要${actionText}用户 "${row.username}" 吗？${isBan ? '禁用后该用户将无法使用平台功能。' : '启用后该用户可正常使用。'}`,
    '权限变更确认',
    { confirmButtonText: '确定执行', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    // 若是真实用户 -> 调用后端接口
    if (row.isReal) {
      try {
        const newStatus = isBan ? 'disabled' : 'normal'
        const r = await axios.post(`${SERVER_API}/api/user/updateStatus`, { username: row.username, status: newStatus })
        if (r.data && r.data.code === 200) {
          ElMessage.success(`用户已${actionText}`)
          await fetchUsers()
        } else {
          ElMessage.error(r.data?.msg || '更新失败')
        }
      } catch (e) { ElMessage.error('网络请求失败') }
    } else {
      // 虚拟用户依然使用本地逻辑
      row.status = isBan ? '禁用' : '正常'

      const current = JSON.parse(localStorage.getItem(USER_KEY) || '[]')
      const idx = current.findIndex(u => u.id === row.id)
      if (idx > -1) { current[idx].status = row.status; localStorage.setItem(USER_KEY, JSON.stringify(current)) }

      let banned = JSON.parse(localStorage.getItem(BANNED_KEY) || '[]')
      if (isBan) {
        if (!banned.includes(row.id)) banned.push(row.id)
      } else {
        banned = banned.filter(id => id !== row.id)
      }
      localStorage.setItem(BANNED_KEY, JSON.stringify(banned))

      ElMessage.success(`用户已${actionText}`)
      window.dispatchEvent(new Event('competitionDataChanged'))
    }
  }).catch(() => {})
}

// 删除用户（真实用户通过后端接口删除；虚拟用户本地删除）
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '此操作将永久删除该用户及其所有数据（简历、历史记录等）, 是否继续?',
    '高风险操作警告',
    { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error' }
  ).then(async () => {
    if (row.isReal) {
      try {
        const r = await axios.post(`${SERVER_API}/api/user/delete`, { username: row.username })
        if (r.data && r.data.code === 200) {
          ElMessage.success('用户已删除')
          await fetchUsers()
        } else {
          ElMessage.error(r.data?.msg || '删除失败')
        }
      } catch (e) { ElMessage.error('网络请求失败') }
    } else {
      // 虚拟用户本地删除
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      const current = JSON.parse(localStorage.getItem(USER_KEY) || '[]').filter(u => u.id !== row.id)
      localStorage.setItem(USER_KEY, JSON.stringify(current))
      let banned = JSON.parse(localStorage.getItem(BANNED_KEY) || '[]')
      banned = banned.filter(id => id !== row.id)
      localStorage.setItem(BANNED_KEY, JSON.stringify(banned))
      ElMessage.success('用户已删除')
      window.dispatchEvent(new Event('competitionDataChanged'))
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="page-container animate-fade-in">
    <div class="header-section">
      <div class="title-group">
        <div class="icon-box"><el-icon><UserFilled /></el-icon></div>
        <div>
          <h2 class="page-title">用户管理中心</h2>
          <p class="page-subtitle">管理平台注册学生信息及账号权限状态</p>
        </div>
      </div>
      
      <div class="action-group">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名、UID或专业..."
          class="custom-search"
          :prefix-icon="Search"
          clearable
        />
        <el-button type="primary" color="#101C4D" class="add-btn">
          <el-icon style="margin-right: 5px"><UserFilled /></el-icon> 新增用户
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="table-card">
      <el-table 
        :data="filteredData" 
        style="width: 100%" 
        v-loading="loading"
        :header-cell-style="{ background: '#f8fafc', color: '#101C4D', fontWeight: 'bold', height: '50px' }"
        :row-style="{ height: '60px' }"
      >
        <el-table-column prop="id" label="UID" width="100" align="center">
          <template #default="scope">
            <span class="uid-tag">#{{ scope.row.id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="用户信息" min-width="180">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="36" class="user-avatar">{{ scope.row.avatar }}</el-avatar>
              <span class="username">{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="年级 / 意向岗位" min-width="180">
           <template #default="scope">
             <div style="display:flex; gap:8px; align-items:center;">
               <el-tag size="small" effect="plain" type="info" round>{{ scope.row.grade }}</el-tag>
               <el-tag size="small" effect="light" type="primary" round>{{ scope.row.intent }}</el-tag>
             </div>
           </template>
        </el-table-column>

        <el-table-column label="账号状态" width="140" align="center">
          <template #default="scope">
            <div class="status-badge" :class="scope.row.status === '正常' ? 'active' : 'banned'">
              <div class="dot"></div>
              {{ scope.row.status }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="register_time" label="注册时间" width="180" align="center" sortable />

        <el-table-column prop="last_login" label="最后登录" width="180" align="center">
          <template #default="scope">
            <span>{{ scope.row.last_login }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              :type="scope.row.status === '正常' ? 'warning' : 'success'" 
              plain 
              :icon="scope.row.status === '正常' ? CircleClose : CircleCheck"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === '正常' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              plain 
              :icon="Delete" 
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination 
          background 
          layout="total, prev, pager, next" 
          :total="100" 
          :page-size="10"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
/* 页面容器 */
.page-container { padding: 10px; min-height: 100%; display: flex; flex-direction: column; }

/* 顶部区域 */
.header-section { 
  display: flex; justify-content: space-between; align-items: flex-end; 
  margin-bottom: 24px; padding: 0 5px;
}
.title-group { display: flex; align-items: center; gap: 15px; }
.icon-box {
  width: 48px; height: 48px; 
  background: linear-gradient(135deg, #101C4D 0%, #2c3e8c 100%);
  border-radius: 12px; color: #EFE3B2;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
  box-shadow: 0 4px 10px rgba(16, 28, 77, 0.2);
}
.page-title { margin: 0; font-size: 22px; color: #101C4D; font-weight: 800; }
.page-subtitle { margin: 4px 0 0 0; color: #64748b; font-size: 13px; }

/* 操作区域 */
.action-group { display: flex; gap: 12px; }
.custom-search { width: 260px; }
:deep(.custom-search .el-input__wrapper) {
  border-radius: 8px; box-shadow: 0 0 0 1px #e2e8f0 inset;
}
:deep(.custom-search .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #101C4D inset;
}
.add-btn { border-radius: 8px; font-weight: 600; }

/* 表格卡片 */
.table-card { border-radius: 16px; border: none; box-shadow: 0 8px 20px rgba(0,0,0,0.04); overflow: visible; }
.uid-tag { font-family: monospace; color: #94a3b8; font-weight: bold; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }

.user-info { display: flex; align-items: center; gap: 12px; }
.user-avatar { background: #EFE3B2; color: #101C4D; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.username { font-weight: 600; color: #334155; }

/* 状态徽章 */
.status-badge {
  display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px;
  border-radius: 20px; font-size: 12px; font-weight: 600;
}
.status-badge.active { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }
.status-badge.banned { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

.pagination-wrapper { margin-top: 25px; display: flex; justify-content: flex-end; }

/* 动画 */
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>