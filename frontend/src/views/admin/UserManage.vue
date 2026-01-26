<script setup>
import { ref, onMounted } from 'vue'
import { Search, Delete, Edit, UserFilled, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchQuery = ref('')
const tableData = ref([])

// --- 模拟数据 (后续对接后端 API) ---
const mockUsers = [
  { id: 1001, username: '张三', role: '大三/算法', status: '正常', date: '2026-01-20', avatar: 'Z' },
  { id: 1002, username: '李四', role: '研一/Java', status: '正常', date: '2026-01-21', avatar: 'L' },
  { id: 1003, username: '王五', role: '大二/前端', status: '禁用', date: '2026-01-22', avatar: 'W' },
  { id: 1004, username: '赵六', role: '博士/AI', status: '正常', date: '2026-01-23', avatar: 'Z' },
  { id: 1005, username: '钱七', role: '大四/产品', status: '正常', date: '2026-01-24', avatar: 'Q' },
]

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  // 模拟网络请求延迟
  setTimeout(() => {
    tableData.value = mockUsers
    loading.value = false
  }, 600)
}

// 封禁/解封用户
const toggleStatus = (row) => {
  const isBan = row.status === '正常'
  const actionText = isBan ? '禁用' : '解封'
  
  ElMessageBox.confirm(
    `确定要${actionText}用户 "${row.username}" 吗？${isBan ? '禁用后该用户将无法登录。' : '解封后该用户可正常使用。'}`,
    '权限变更确认',
    {
      confirmButtonText: '确定执行',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    row.status = isBan ? '禁用' : '正常'
    ElMessage.success(`用户已${actionText}`)
    // TODO: 这里调用后端 API: axios.post('/api/admin/user/status', { id: row.id, status: row.status })
  }).catch(() => {})
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '此操作将永久删除该用户及其所有数据（简历、历史记录等）, 是否继续?',
    '高风险操作警告',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
    }
  ).then(() => {
    tableData.value = tableData.value.filter(item => item.id !== row.id)
    ElMessage.success('用户已删除')
    // TODO: 这里调用后端 API: axios.delete(`/api/admin/user/${row.id}`)
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
        :data="tableData" 
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

        <el-table-column prop="role" label="年级/意向岗位" min-width="160">
           <template #default="scope">
             <el-tag size="small" effect="plain" type="info" round>{{ scope.row.role }}</el-tag>
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

        <el-table-column prop="date" label="注册日期" width="180" align="center" sortable />

        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              :type="scope.row.status === '正常' ? 'warning' : 'success'" 
              plain 
              :icon="scope.row.status === '正常' ? CircleClose : CircleCheck"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === '正常' ? '禁用' : '解封' }}
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