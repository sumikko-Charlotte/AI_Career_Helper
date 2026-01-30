<script setup>
import { ref, reactive, onMounted } from 'vue'
import { User, Message, Iphone, Upload, Postcard, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

// 数据容器
const adminInfo = ref({
  username: '',
  nickname: '',
  role: '',
  department: '',
  email: '',
  phone: '',
  avatar: '', 
  lastLogin: '',
  ip: ''
})

const passwordForm = reactive({ oldPass: '', newPass: '', confirmPass: '' })
const activeTab = ref('base')
const loading = ref(false)

// 🟢 1. 获取信息
const fetchProfile = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/admin/profile`)
    if (res.data.success) {
      adminInfo.value = { ...adminInfo.value, ...res.data.data }
    }
  } catch (error) {
    console.error('获取失败', error)
  }
}

// 🟢 2. 保存并通知顶栏
const handleSaveInfo = async () => {
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/admin/profile/update`, adminInfo.value)
    if (res.data.success) {
      ElMessage.success('保存成功！')
      // 发送信号让 Layout 刷新头像
      window.dispatchEvent(new Event('admin-profile-updated'))
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('网络错误或图片太大，请换张小图试试')
  } finally {
    loading.value = false
  }
}

// 🟢 3. 核心修复：头像选择逻辑
const handleAvatarChange = (uploadFile) => {
  const file = uploadFile.raw
  
  if (!file) return

  // A. 格式限制
  const isJPGOrPNG = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJPGOrPNG) {
    return ElMessage.error('头像只能是 JPG 或 PNG 格式!')
  }

  // B. 大小限制 (非常重要！限制为 200KB)
  // 因为我们是存 JSON，图片太大后端会崩溃
  const isLt200K = file.size / 1024 < 200
  if (!isLt200K) {
    return ElMessage.error('图片太大了！为了系统流畅，请上传 200KB 以下的图片。')
  }

  // C. 转 Base64 用于显示和存储
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = (e) => {
    // 把转好的字符串存进变量，页面上的头像会立马变
    adminInfo.value.avatar = e.target.result 
    ElMessage.success('头像已预览，请点击底部的“保存修改”以永久生效')
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (passwordForm.newPass !== passwordForm.confirmPass) return ElMessage.error('两次密码不一致')
  if (passwordForm.newPass.length < 6) return ElMessage.warning('密码长度至少 6 位')

  loading.value = true
  try {
    const payload = {
      ...adminInfo.value,
      new_password: passwordForm.newPass
    }
    const res = await axios.post(`${API_BASE}/api/admin/profile/update`, payload)

    if (res.data.success) {
      ElMessage.success('密码修改成功！下次请用新密码登录')
      passwordForm.oldPass = ''
      passwordForm.newPass = '' 
      passwordForm.confirmPass = ''
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('请求失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<template>
  <div class="page-container animate-fade-in">
    <el-row :gutter="20">
      
      <el-col :span="8" :xs="24">
        <el-card shadow="hover" class="profile-card">
          <div class="user-header">
            <div class="avatar-wrapper">
              <el-avatar 
                v-if="adminInfo.avatar" 
                :size="100" 
                :src="adminInfo.avatar" 
                class="avatar-img" 
              />
              <el-avatar v-else :size="100" class="avatar-img">Admin</el-avatar>

              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :auto-upload="false"
                :on-change="handleAvatarChange"
              >
                <div class="upload-mask">
                  <el-icon><Upload /></el-icon>
                  <span>更换头像</span>
                </div>
              </el-upload>
            </div>

            <h2 class="nickname">{{ adminInfo.nickname || '未设置昵称' }}</h2>
            <p class="username">@{{ adminInfo.username }}</p>
            <el-tag effect="dark" color="#101C4D" style="border:none; margin-top:10px;">
              {{ adminInfo.role || '管理员' }}
            </el-tag>
          </div>

          <el-divider />

          <div class="user-stats">
            <div class="stat-item">
              <div class="label"><el-icon><Postcard /></el-icon> 部门</div>
              <div class="value">{{ adminInfo.department || '暂无' }}</div>
            </div>
            <div class="stat-item">
              <div class="label"><el-icon><Message /></el-icon> 邮箱</div>
              <div class="value">{{ adminInfo.email || '未绑定' }}</div>
            </div>
            <div class="stat-item">
              <div class="label"><el-icon><Iphone /></el-icon> 手机</div>
              <div class="value">{{ adminInfo.phone || '未绑定' }}</div>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="log-card">
          <template #header>
            <div class="card-header">
              <span>安全概览</span>
            </div>
          </template>
          <div class="log-row">
            <span class="log-label">上次登录</span>
            <span class="log-val">{{ adminInfo.lastLogin || '刚刚' }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16" :xs="24">
        <el-card shadow="hover" class="settings-card">
          <el-tabs v-model="activeTab">
            
            <el-tab-pane label="基本资料" name="base">
              <div class="form-wrapper">
                <el-form :model="adminInfo" label-position="top">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="昵称">
                        <el-input v-model="adminInfo.nickname" :prefix-icon="User" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="手机号">
                        <el-input v-model="adminInfo.phone" :prefix-icon="Iphone" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  
                  <el-form-item label="邮箱">
                    <el-input v-model="adminInfo.email" :prefix-icon="Message" />
                  </el-form-item>

                  <el-form-item label="部门 / 职位">
                    <el-input v-model="adminInfo.department" placeholder="例如：技术部" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" color="#101C4D" :loading="loading" @click="handleSaveInfo">
                      保存修改
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="安全设置" name="security">
              <div class="form-wrapper security-wrapper">
                <el-alert title="修改密码后需要重新登录" type="warning" show-icon :closable="false" style="margin-bottom:20px;" />
                
                <el-form :model="passwordForm" label-width="100px" label-position="left">
                  <el-form-item label="新密码">
                    <el-input v-model="passwordForm.newPass" type="password" show-password />
                  </el-form-item>
                  <el-form-item label="确认密码">
                    <el-input v-model="passwordForm.confirmPass" type="password" show-password />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="danger" plain :loading="loading" @click="handleChangePassword">
                      确认修改密码
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

    </el-row>
  </div>
</template>

<style scoped>
.page-container { padding: 10px; min-height: 100%; }

/* 左侧卡片 */
.profile-card { text-align: center; border-radius: 12px; border: none; }
.user-header { position: relative; padding: 20px 0; }
.avatar-wrapper { 
  width: 100px; height: 100px; margin: 0 auto 15px; position: relative; 
  border-radius: 50%; border: 4px solid #f0f2f5; overflow: hidden;
  background-color: #f0f2f5;
  display: flex; align-items: center; justify-content: center;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.upload-mask {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); color: white;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  opacity: 0; transition: opacity 0.3s; cursor: pointer;
  z-index: 10;
}
.avatar-wrapper:hover .upload-mask { opacity: 1; }

/* 必须确保 uploader 占满父容器 */
.avatar-uploader {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
}
:deep(.el-upload) {
  width: 100%; height: 100%; display: block;
}

.nickname { margin: 0; color: #101C4D; font-size: 22px; font-weight: 700; }
.username { margin: 5px 0 0; color: #909399; font-size: 14px; }

.user-stats { text-align: left; padding: 0 10px; }
.stat-item { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 14px; }
.stat-item .label { color: #606266; display: flex; align-items: center; gap: 8px; }
.stat-item .value { font-weight: 600; color: #303133; }

/* 日志卡片 */
.log-card { margin-top: 20px; border-radius: 12px; border: none; background: #fdfdfd; }
.card-header { font-weight: bold; color: #101C4D; }
.log-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; }
.log-label { color: #909399; }
.log-val { font-family: monospace; color: #303133; }

/* 右侧卡片 */
.settings-card { min-height: 500px; border-radius: 12px; border: none; }
.form-wrapper { padding: 10px 20px; max-width: 600px; }
.security-wrapper { max-width: 500px; }

:deep(.el-tabs__item.is-active) { color: #101C4D !important; font-weight: bold; }
:deep(.el-tabs__item:hover) { color: #101C4D; }
:deep(.el-tabs__active-bar) { background-color: #101C4D; }

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>