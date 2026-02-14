<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Message, Iphone, Edit, Upload } from '@element-plus/icons-vue'

const loading = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE ?? ''
console.debug('[UserProfile] API_BASE ->', API_BASE)

// 隐藏的文件上传 Input
const fileInput = ref(null)

// 修改密码弹窗状态
const pwdDialogVisible = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 用户资料表单
const form = reactive({
  username: '',
  avatar: '', // 头像URL
  email: '',
  phone: '',
  city: '',
  style: '专业正式',
  file_format: 'PDF',
  notify: true,
  auto_save: true
})

const stats = reactive({
  count: 12, days: '3个月', score: '4.8/5.0', level: '高级会员'
})

// 加载资料
const fetchProfile = async () => {
  const currentUser = localStorage.getItem('remembered_username')
  if (!currentUser) return
  form.username = currentUser 

  try {
    const res = await axios.get(`${API_BASE}/api/user/profile`, {
      params: { username: currentUser }
    })
    if (res.data.success && res.data.data) {
      Object.assign(form, res.data.data)
      form.username = currentUser 
    }
  } catch (error) {
    console.error(error)
  }
}

// 保存资料
const handleSave = async () => {
  loading.value = true
  try {
    // 关键修复点：确保发送完整的数据结构，包括 username
    const profileData = {
      username: form.username || localStorage.getItem('remembered_username'),
      avatar: form.avatar || '',
      email: form.email || '',
      phone: form.phone || '',
      city: form.city || '',
      style: form.style || '专业正式',
      file_format: form.file_format || 'PDF',
      notify: form.notify !== undefined ? form.notify : true,
      auto_save: form.auto_save !== undefined ? form.auto_save : true
    }
    
    console.log('💾 [UserProfile] 保存用户资料:', profileData)
    
    const res = await axios.post(`${API_BASE}/api/user/profile`, profileData, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (res.data.success || res.data.code === 200) {
      ElMessage.success(res.data.message || res.data.msg || '保存成功！数据已持久化到数据库')
      
      // 更新 localStorage 中的用户信息
      try {
        const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
        if (loginUserStr) {
          const loginUser = JSON.parse(loginUserStr)
          loginUser.email = profileData.email
          loginUser.phone = profileData.phone
          loginUser.city = profileData.city
          loginUser.avatar = profileData.avatar
          localStorage.setItem('login_user', JSON.stringify(loginUser))
          sessionStorage.setItem('login_user', JSON.stringify(loginUser))
        }
      } catch (e) {
        console.warn('更新 localStorage 失败:', e)
      }
    } else {
      ElMessage.error(res.data.message || res.data.msg || '保存失败')
    }
  } catch (error) {
    console.error('[UserProfile] 保存失败:', error)
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data
      
      if (status === 400) {
        ElMessage.error(errorData?.detail || errorData?.message || '参数错误')
      } else if (status === 404) {
        ElMessage.error('用户不存在，请重新登录')
      } else if (status === 500) {
        ElMessage.error(errorData?.detail || errorData?.message || '服务器错误')
      } else {
        ElMessage.error(errorData?.detail || errorData?.message || '保存失败')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
  } finally {
    loading.value = false
  }
}

// --- 📸 头像上传逻辑 ---
const triggerUpload = () => {
  fileInput.value.click() // 触发隐藏的 input
}

const handleFileChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    return ElMessage.warning('仅支持 JPG、PNG、GIF、WEBP 格式的图片')
  }

  // 验证文件大小（限制 10MB）
  if (file.size > 10 * 1024 * 1024) {
    return ElMessage.warning('图片大小不能超过 10MB')
  }

  // 获取用户名
  const currentUser = form.username || localStorage.getItem('remembered_username')
  if (!currentUser) {
    return ElMessage.warning('请先登录')
  }

  const formData = new FormData()
  formData.append('avatar', file)  // 关键修复点：使用 'avatar' 字段名，与后端匹配
  formData.append('username', currentUser)  // 关键修复点：添加 username 字段

  try {
    const res = await axios.post(`${API_BASE}/api/user/avatar`, formData, {  // 关键修复点：使用正确的接口路径
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000  // 增加超时时间，支持大文件上传
    })
    
    if (res.data.success || res.data.code === 200) {
      // 关键修复点：使用返回的 url 字段（前端期望的字段）
      const avatarUrl = res.data.url || res.data.avatarUrl || res.data.avatar_url || res.data.avatar
      form.avatar = avatarUrl
      
      // 更新 localStorage 中的用户信息
      try {
        const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
        if (loginUserStr) {
          const loginUser = JSON.parse(loginUserStr)
          loginUser.avatar = avatarUrl
          localStorage.setItem('login_user', JSON.stringify(loginUser))
          sessionStorage.setItem('login_user', JSON.stringify(loginUser))
        }
      } catch (e) {
        console.warn('更新 localStorage 失败:', e)
      }
      
      ElMessage.success(res.data.msg || res.data.message || '头像更新成功')
    } else {
      ElMessage.error(res.data.msg || res.data.message || '头像上传失败')
    }
  } catch (error) {
    console.error('[UserProfile] 头像上传失败:', error)
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data
      
      if (status === 400) {
        ElMessage.error(errorData?.detail || errorData?.message || '文件格式不支持或参数错误')
      } else if (status === 413) {
        ElMessage.error('文件过大，请选择小于 10MB 的图片')
      } else if (status === 404) {
        ElMessage.error('用户不存在，请重新登录')
      } else {
        ElMessage.error(errorData?.detail || errorData?.message || '头像上传失败')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
  } finally {
    // 清空文件输入，允许重复选择同一文件
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

// --- 🔒 修改密码逻辑 ---
const openPwdDialog = () => {
  pwdForm.old_password = ''
  pwdForm.new_password = ''
  pwdForm.confirm_password = ''
  pwdDialogVisible.value = true
}

const submitPasswordChange = async () => {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    return ElMessage.warning('请填写完整')
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    return ElMessage.warning('两次新密码输入不一致')
  }

  try {
    const res = await axios.post(`${API_BASE}/api/user/change_password`, {
      username: form.username,
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    
    if (res.data.success) {
      ElMessage.success('密码修改成功，请重新登录')
      pwdDialogVisible.value = false
      // 可选：退出登录逻辑
      // localStorage.clear(); location.reload();
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('请求失败')
  }
}

onMounted(() => fetchProfile())
</script>

<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>个人中心</h2>
      <p>管理您的个人信息和账户设置</p>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="panel-card">
          <h3 class="card-title">基本信息</h3>
          <el-form label-position="top" size="large">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名">
                  <el-input v-model="form.username" disabled :prefix-icon="User" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="form.email" :prefix-icon="Message" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号">
                  <el-input v-model="form.phone" :prefix-icon="Iphone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
  <el-form-item label="所在城市">
    <el-select v-model="form.city" placeholder="请选择" style="width: 100%">
      <el-option label="北京" value="北京" />
      <el-option label="上海" value="上海" />
      <el-option label="广州" value="广州" />
      <el-option label="深圳" value="深圳" />
      <el-option label="杭州" value="杭州" />
      <el-option label="成都" value="成都" />
      <el-option label="武汉" value="武汉" />
      <el-option label="南京" value="南京" />
      <el-option label="西安" value="西安" />
      <el-option label="重庆" value="重庆" />
      <el-option label="天津" value="天津" />
      <el-option label="苏州" value="苏州" />
      <el-option label="长沙" value="长沙" />
      <el-option label="其他" value="其他" />
    </el-select>
  </el-form-item>
</el-col>
            </el-row>
          </el-form>
        </div>

        <div class="panel-card" style="margin-top: 20px;">
          <h3 class="card-title">偏好设置</h3>
          <el-form label-position="top">
            <el-form-item label="默认润色风格">
              <el-radio-group v-model="form.style">
                <el-radio-button label="专业正式" />
                <el-radio-button label="现代科技" />
                <el-radio-button label="创意表达" />
              </el-radio-group>
            </el-form-item>
            <div class="switches">
              <el-checkbox v-model="form.notify" label="润色完成邮件通知" border />
              <el-checkbox v-model="form.auto_save" label="自动保存历史记录" border />
            </div>
          </el-form>
        </div>
      </div>

      <div class="right-panel">
        <div class="user-card">
          <input type="file" ref="fileInput" accept="image/*" style="display: none" @change="handleFileChange">
          
          <div class="avatar-wrapper" @click="triggerUpload">
            <img v-if="form.avatar" :src="form.avatar" class="avatar-img" />
            <div v-else class="avatar-circle">{{ form.username.charAt(0).toUpperCase() }}</div>
            <div class="avatar-mask"><el-icon><Upload /></el-icon></div>
          </div>
          
          <div class="user-name">{{ form.username }}</div>
          <div class="user-role">高级用户</div>
          
          <el-button plain round size="small" :icon="Edit" style="margin-top: 15px" @click="triggerUpload">
            更换头像
          </el-button>
        </div>

        <div class="stats-card">
          <div class="stat-title">账户统计</div>
          <div class="stat-row"><span>润色次数</span><span class="val">{{ stats.count }}</span></div>
          <div class="stat-row"><span>账户时长</span><span class="val">{{ stats.days }}</span></div>
          <div class="stat-row"><span>平均评分</span><span class="val score">{{ stats.score }}</span></div>
          
          <el-button type="primary" class="save-btn" :loading="loading" @click="handleSave">保存更改</el-button>
          <el-button class="logout-btn" @click="openPwdDialog">更改密码</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="400px" center>
      <el-form :model="pwdForm" label-position="top">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="pwdDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPasswordChange">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* (原有样式保持不变，只增加头像相关) */
.profile-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 25px; }
.content-wrapper { display: flex; gap: 20px; }
.left-panel { flex: 2; }
.right-panel { flex: 1; display: flex; flex-direction: column; gap: 20px; }
.panel-card, .user-card, .stats-card { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.card-title { margin: 0 0 20px 0; font-size: 16px; font-weight: bold; color: #303133; }
.user-card { display: flex; flex-direction: column; align-items: center; }

/* 头像样式 */
.avatar-wrapper {
  position: relative; cursor: pointer;
  width: 80px; height: 80px; margin-bottom: 15px;
}
.avatar-circle, .avatar-img {
  width: 100%; height: 100%; border-radius: 50%;
  box-shadow: 0 4px 10px rgba(64,158,255,0.3);
  object-fit: cover;
}
.avatar-circle {
  background: #409EFF; color: white; font-size: 32px;
  font-weight: bold; line-height: 80px; text-align: center;
}
.avatar-mask {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4); border-radius: 50%;
  display: flex; justify-content: center; align-items: center;
  color: white; font-size: 24px; opacity: 0; transition: opacity 0.3s;
}
.avatar-wrapper:hover .avatar-mask { opacity: 1; }

.user-name { font-size: 18px; font-weight: bold; }
.user-role { font-size: 13px; color: #909399; margin-top: 4px; }
.stat-row { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; color: #606266; }
.stat-row .val { font-weight: bold; color: #303133; }
.stat-row .score { color: #E6A23C; }
.save-btn { width: 100%; margin-top: 15px; font-weight: bold; }
.logout-btn { width: 100%; margin-top: 10px; margin-left: 0; }
.switches { display: flex; gap: 15px; margin-top: 10px; }
</style>