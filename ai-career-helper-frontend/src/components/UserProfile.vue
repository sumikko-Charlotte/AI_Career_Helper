<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Message, Iphone, Edit, Upload } from '@element-plus/icons-vue'

const loading = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE ?? 'https://ai-career-helper-backend-u1s0.onrender.com'
console.debug('[UserProfile] API_BASE ->', API_BASE)

// 隐藏的文件上传 Input
const fileInput = ref(null)
// 图片预览（本地预览，上传前显示）
const avatarPreview = ref('')

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

// 加载资料（优先从登录信息中读取，然后从API加载最新数据）
const fetchProfile = async () => {
  // 获取用户名：优先从 localStorage，如果没有则尝试从 sessionStorage
  let currentUser = localStorage.getItem('remembered_username')
  if (!currentUser) {
    currentUser = sessionStorage.getItem('username')
  }
  
  // 如果找到了用户名，立即设置（作为默认值，用户可以编辑）
  if (currentUser) {
    form.username = currentUser
  }
  
  // 1. 优先从登录信息中读取用户数据（从 localStorage 或 sessionStorage）
  try {
    const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
    if (loginUserStr) {
      const loginUser = JSON.parse(loginUserStr)
      console.log('📥 [UserProfile] 从登录信息加载用户数据:', loginUser)
      
      // 填充表单（登录信息是最新的）
      if (loginUser.username) form.username = loginUser.username
      if (loginUser.email) form.email = loginUser.email
      if (loginUser.phone) form.phone = loginUser.phone
      if (loginUser.city) form.city = loginUser.city
      // 关键修复点：确保头像 URL 是完整路径（如果是相对路径，需要拼接 API_BASE）
      if (loginUser.avatar) {
        // 如果 avatar 是相对路径（以 / 开头但不是 http），拼接 API_BASE
        if (loginUser.avatar.startsWith('/') && !loginUser.avatar.startsWith('http')) {
          form.avatar = `${API_BASE}${loginUser.avatar}`
        } else {
          form.avatar = loginUser.avatar
        }
        console.log('📸 [UserProfile] 从登录信息加载头像:', form.avatar)
      }
    }
  } catch (error) {
    console.warn('[UserProfile] 解析登录信息失败:', error)
  }

  // 2. 从 API 加载最新数据（确保显示数据库中的最新数据）
  if (currentUser) {
    try {
      const res = await axios.get(`${API_BASE}/api/user/profile`, {
        params: { username: currentUser }
      })
      if (res.data.success && res.data.data) {
        const data = res.data.data
        console.log('📥 [UserProfile] 从API加载用户资料:', data)
        
        // 合并所有字段，确保显示最新保存的数据（API数据优先）
        form.username = data.username || currentUser
        form.avatar = data.avatar || form.avatar || ''  // 头像URL（API优先）
        form.email = data.email || form.email || ''
        form.phone = data.phone || form.phone || ''
        form.city = data.city || form.city || ''
        form.style = data.style || '专业正式'
        form.file_format = data.file_format || 'PDF'
        form.notify = data.notify !== undefined ? (data.notify === 'True' || data.notify === true) : true
        form.auto_save = data.auto_save !== undefined ? (data.auto_save === 'True' || data.auto_save === true) : true
        
        console.log('✅ [UserProfile] 用户资料加载成功，头像URL:', form.avatar)
      } else {
        console.warn('⚠️ [UserProfile] API 返回数据格式异常:', res.data)
      }
    } catch (error) {
      console.error('[UserProfile] 获取用户资料失败:', error)
      // API 失败不影响，继续使用登录信息中的默认值
    }
  }
}

// 保存资料（确保所有字段都保存到数据库和CSV）
const handleSave = async () => {
  // 获取用户名：优先从 localStorage，如果没有则使用表单中的用户名
  let currentUser = localStorage.getItem('remembered_username')
  if (!currentUser) {
    currentUser = sessionStorage.getItem('username')
  }
  
  // 如果表单中有用户名，使用表单中的（允许用户修改姓名）
  if (form.username) {
    // 如果之前没有保存的用户名，使用表单中的用户名
    if (!currentUser) {
      currentUser = form.username
    }
  } else if (currentUser) {
    // 如果表单中没有用户名，但 localStorage 中有，使用 localStorage 中的
    form.username = currentUser
  } else {
    // 如果都没有，提示用户
    return ElMessage.warning('请填写姓名')
  }
  
  loading.value = true
  try {
    // 关键修复点：确保只发送头像URL，不发送base64数据
    // 如果 form.avatar 是 base64 数据（以 data: 开头），则不发送，只发送已上传的URL
    let avatarUrl = form.avatar || ''
    if (avatarUrl.startsWith('data:')) {
      // 如果是 base64 预览数据，不发送（等待用户上传后再保存）
      avatarUrl = ''
      console.warn('⚠️ [UserProfile] 检测到 base64 预览数据，跳过保存（等待上传完成）')
    }
    
    // 确保所有字段都包含在请求中，包括头像、邮箱、手机、城市等
    const profileData = {
      username: currentUser,  // 使用当前登录的用户名（不可修改）
      avatar: avatarUrl,  // 关键修复点：只发送URL，不发送base64
      email: form.email || '',
      phone: form.phone || '',
      city: form.city || '',
      style: form.style || '专业正式',
      file_format: form.file_format || 'PDF',
      notify: form.notify !== undefined ? form.notify : true,
      auto_save: form.auto_save !== undefined ? form.auto_save : true
    }
    
    console.log('💾 [UserProfile] 保存用户资料:', profileData)
    
    // 关键修复点：使用 PUT 方法（如果支持），否则使用 POST
    const res = await axios.put(`${API_BASE}/api/user/profile`, profileData, {
      headers: {
        'Content-Type': 'application/json'  // 明确指定 JSON 格式
      }
    }).catch(async (error) => {
      // 如果 PUT 不支持，回退到 POST
      if (error.response?.status === 405) {
        console.warn('⚠️ [UserProfile] PUT 方法不支持，回退到 POST')
        return await axios.post(`${API_BASE}/api/user/profile`, profileData, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
      }
      throw error
    })
    if (res.data.success || res.data.code === 200) {
      ElMessage.success(res.data.message || res.data.msg || '保存成功！数据已持久化到数据库')
      
      // 更新登录信息中的用户数据（确保刷新后也能显示）
      try {
        const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
        if (loginUserStr) {
          const loginUser = JSON.parse(loginUserStr)
          loginUser.email = profileData.email
          loginUser.phone = profileData.phone
          loginUser.city = profileData.city
          if (profileData.avatar) loginUser.avatar = profileData.avatar
          localStorage.setItem('login_user', JSON.stringify(loginUser))
          sessionStorage.setItem('login_user', JSON.stringify(loginUser))
        }
      } catch (e) {
        console.warn('[UserProfile] 更新登录信息失败:', e)
      }
      
      // 保存成功后重新获取最新数据，确保显示最新内容
      await fetchProfile()
    } else {
      ElMessage.error(res.data.message || res.data.msg || '保存失败')
    }
  } catch (error) {
    console.error('[UserProfile] 保存失败:', error)
    if (error.response) {
      ElMessage.error(error.response.data?.message || '保存失败')
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
  if (!file.type.startsWith('image/')) {
    return ElMessage.warning('请选择图片文件')
  }

  // 验证文件大小（限制 5MB，与后端保持一致）
  if (file.size > 5 * 1024 * 1024) {
    return ElMessage.warning('图片大小不能超过 5MB')
  }

  // 📸 立即显示预览（本地预览，无需等待上传）
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
    // 临时更新头像显示，让用户立即看到预览
    form.avatar = e.target.result
  }
  reader.readAsDataURL(file)

  // 获取用户名：优先从表单，其次从 localStorage
  let currentUser = form.username || localStorage.getItem('remembered_username')
  if (!currentUser) {
    currentUser = sessionStorage.getItem('username')
  }
  
  if (!currentUser) {
    return ElMessage.warning('请先填写姓名')
  }

  const formData = new FormData()
  formData.append('avatar', file) // 后端期望的字段名是 'avatar'（用户已改回）
  formData.append('username', currentUser) // 传递用户名

  try {
    // 注意：不要手动设置 Content-Type，让 axios 自动设置（包含 boundary）
    const res = await axios.post(`${API_BASE}/api/user/avatar`, formData, {
      timeout: 30000  // 增加超时时间，支持大文件上传
      // 不设置 headers，让 axios 自动处理 multipart/form-data
    })
    if (res.data.success || res.data.code === 200) {
      // 更新头像显示（使用服务器返回的URL，替换本地预览）
      const serverAvatarUrl = res.data.avatarUrl || res.data.url || res.data.avatar_url || res.data.avatar
      form.avatar = serverAvatarUrl
      avatarPreview.value = '' // 清空本地预览
      
      // 更新登录信息中的头像（确保刷新后也能显示）
      try {
        const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
        if (loginUserStr) {
          const loginUser = JSON.parse(loginUserStr)
          loginUser.avatar = serverAvatarUrl
          localStorage.setItem('login_user', JSON.stringify(loginUser))
          sessionStorage.setItem('login_user', JSON.stringify(loginUser))
        }
      } catch (e) {
        console.warn('[UserProfile] 更新登录信息失败:', e)
      }
      
      // 立即保存头像URL到用户资料（保存到数据库和CSV，确保持久化）
      // 注意：这里只保存头像URL，其他字段保持不变
      try {
        const saveRes = await axios.post(`${API_BASE}/api/user/profile`, {
          username: currentUser,
          avatar: serverAvatarUrl,
          email: form.email || '',
          phone: form.phone || '',
          city: form.city || '',
          style: form.style || '专业正式',
          file_format: form.file_format || 'PDF',
          notify: form.notify !== undefined ? form.notify : true,
          auto_save: form.auto_save !== undefined ? form.auto_save : true
        })
        if (saveRes.data.success) {
          console.log('✅ [UserProfile] 头像URL已保存到数据库和CSV')
        } else {
          console.warn('⚠️ [UserProfile] 头像URL保存失败:', saveRes.data.message)
        }
      } catch (saveError) {
        console.error('❌ [UserProfile] 保存头像URL失败:', saveError)
        // 保存失败不影响上传成功提示，但会在控制台记录错误
      }
      
      ElMessage.success(res.data.msg || res.data.message || '头像上传并保存成功')
    } else {
      ElMessage.error(res.data.message || res.data.msg || '头像上传失败')
      // 上传失败，保留本地预览
    }
  } catch (error) {
    console.error('[UserProfile] 头像上传失败:', error)
    console.error('[UserProfile] 错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      statusText: error.response?.statusText
    })
    
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data
      
      if (status === 400) {
        const detail = errorData?.detail || errorData?.message || '文件格式不支持或参数错误'
        ElMessage.error(`上传失败: ${detail}`)
      } else if (status === 413) {
        ElMessage.error('文件过大，请选择小于 5MB 的图片')
      } else if (status === 404) {
        ElMessage.error('用户不存在，请重新登录')
      } else if (status === 500) {
        const detail = errorData?.detail || errorData?.message || '服务器内部错误'
        ElMessage.error(`服务器错误: ${detail}`)
      } else {
        const detail = errorData?.detail || errorData?.message || '头像上传失败'
        ElMessage.error(`上传失败 (${status}): ${detail}`)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络错误：无法连接到服务器，请检查网络连接')
      console.error('[UserProfile] 请求已发出但无响应:', error.request)
    } else {
      // 请求配置错误
      ElMessage.error(`请求配置错误: ${error.message}`)
    }
    // 上传失败，保留本地预览，让用户知道选择了什么图片
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
  // 验证输入
  if (!pwdForm.old_password || !pwdForm.new_password || !pwdForm.confirm_password) {
    return ElMessage.warning('请填写完整信息')
  }
  
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    return ElMessage.warning('两次新密码输入不一致')
  }

  // 验证新密码长度
  if (pwdForm.new_password.length < 6) {
    return ElMessage.warning('新密码长度至少为 6 位')
  }

  // 获取用户名：优先从表单，其次从 localStorage
  let currentUser = form.username || localStorage.getItem('remembered_username')
  if (!currentUser) {
    currentUser = sessionStorage.getItem('username')
  }
  
  if (!currentUser) {
    return ElMessage.warning('请先填写姓名')
  }

  try {
    const res = await axios.post(`${API_BASE}/api/user/change_password`, {
      username: currentUser,
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    
    if (res.data.success) {
      ElMessage.success('密码修改成功，请重新登录')
      pwdDialogVisible.value = false
      // 清空表单
      pwdForm.old_password = ''
      pwdForm.new_password = ''
      pwdForm.confirm_password = ''
      // 可选：退出登录逻辑（如果需要）
      // localStorage.clear()
      // window.location.href = '/login'
    } else {
      ElMessage.error(res.data.message || '密码修改失败')
    }
  } catch (error) {
    console.error('[UserProfile] 密码修改失败:', error)
    if (error.response) {
      if (error.response.status === 400) {
        ElMessage.error(error.response.data?.message || '旧密码不正确或参数错误')
      } else if (error.response.status === 401) {
        ElMessage.error('未授权，请重新登录')
      } else {
        ElMessage.error(error.response.data?.message || '密码修改失败，请稍后重试')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
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
                  <el-input v-model="form.username" :prefix-icon="User" placeholder="请输入姓名" />
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
            <!-- 优先显示预览，其次显示已保存的头像，最后显示默认头像 -->
            <img v-if="avatarPreview" :src="avatarPreview" class="avatar-img" alt="预览" />
            <img v-else-if="form.avatar" :src="form.avatar" class="avatar-img" alt="头像" />
            <div v-else class="avatar-circle">{{ form.username ? form.username.charAt(0).toUpperCase() : 'U' }}</div>
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