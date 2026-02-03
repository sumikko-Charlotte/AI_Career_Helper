<script setup>
import { ref, onMounted } from 'vue' // Removed computed as we will bind directly
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const emit = defineEmits(['login-success'])
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8001'
const SERVER_API = import.meta.env.VITE_USER_SERVER || 'http://127.0.0.1:3000' // 新增：用户持久化服务
console.debug('[Login] API_BASE ->', API_BASE, 'SERVER_API ->', SERVER_API)

// 响应式数据
const isLogin = ref(true) 
const loading = ref(false)
const rememberMe = ref(false)

// 表单数据
const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  grade: '',
  target_role: ''
})

// 页面加载时检查是否有“记住我”的历史
onMounted(() => {
  const savedUser = localStorage.getItem('remembered_username')
  if (savedUser) {
    loginForm.value.username = savedUser
    rememberMe.value = true
  }
})

const gradeOptions = [
  '大一', '大二', '大三', '大四', 
  '研一', '研二', '研三', 
  '博士', '已毕业/工作','管理员'
]

const roleOptions = [
  'Java开发工程师',
  'C++开发工程师',
  'Python开发工程师',
  'Go开发工程师',
  '前端开发工程师',
  '全栈开发工程师',
  '算法工程师 (AI/大模型)',
  '大数据开发工程师',
  '移动端开发 (iOS/Android)',
  '测试/测试开发',
  '运维/DevOps',
  '产品经理 (PM)',
  'UI/UX 设计师',
  '系统管理',
  '其他'
]

const toggleMode = () => {
  isLogin.value = !isLogin.value
  if (isLogin.value) {
    registerForm.value = { username: '', password: '', grade: '', target_role: '' }
  } else {
    // Switch to register, clear login password but maybe keep username if needed, or clear all
    loginForm.value = { username: '', password: '' }
  }
}

const handleForgotPassword = () => {
  alert('功能开发中：请联系管理员重置密码')
}

// 👇👇👇 修复后的登录逻辑 👇👇👇
const handleLogin = async () => {
  console.log('📝 Login Attempt:', loginForm.value)

  if (!loginForm.value.username.trim() || !loginForm.value.password.trim()) {
    alert('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    console.log('🚀 Sending login request')
    const response = await axios.post(
      `${API_BASE}/api/login`,
      loginForm.value
    )

    console.log('✅ Response:', response.data)
    
    if (response.data.success) {
      // 🟢 关键修复点 1：必须先把 user 取出来！
      const user = response.data.user
      
      // 调试看一下拿到的 user 是什么
      console.log('👤 User info:', user) 

      if (rememberMe.value) {
        localStorage.setItem('remembered_username', loginForm.value.username)
      } else {
        localStorage.removeItem('remembered_username')
      }

      // 同步到真实用户服务（用于持久化 CSV）
      try {
        const syncResp = await axios.post(`${SERVER_API}/api/login`, { username: loginForm.value.username, password: loginForm.value.password })
        if (!(syncResp.data && syncResp.data.code === 200)) {
          // 如果该用户在真实 CSV 中不存在，则尝试注册一次以保证持久化
          await axios.post(`${SERVER_API}/api/register`, { username: loginForm.value.username, password: loginForm.value.password })
        }
      } catch (e) { console.warn('同步登录到用户服务失败', e) }

      alert('登录成功！')
      
      // 🟢 关键修复点 2：现在 user 变量存在了，判断就不会报错了
      if (user.grade === '管理员' || user.username === 'admin') {
          console.log('👑 检测到管理员身份，跳转后台')
          await router.push('/admin/dashboard')
      } else {
          // 普通用户：登录成功后自动跳转到过渡导航页（第3页）
          emit('login-success', user)
          await router.push('/explore')
      }

    } else {
      alert('登录失败：' + response.data.message)
    }
  } catch (error) {
    console.error('登录错误详情:', error)
    alert('登录请求失败，请检查控制台报错')
  } finally {
    loading.value = false
    console.log('🔚 Login flow ended')
  }
}
const handleRegister = async () => {
  // Debug log to see if data is binding correctly now
  console.log('📝 Register Attempt:', registerForm.value)

  if (!registerForm.value.username || !registerForm.value.password ||
      !registerForm.value.grade || !registerForm.value.target_role) {
    alert('请填写所有必填字段')
    return
  }

  loading.value = true
  try {
    const response = await axios.post(`${API_BASE}/api/register`, registerForm.value)
    if (response.data.success) {
      alert('注册成功！请登录')
      isLogin.value = true 
      loginForm.value.username = registerForm.value.username 
      // 同步到真实用户服务，持久化到 CSV
      try {
        await axios.post(`${SERVER_API}/api/register`, registerForm.value)
      } catch (e) { console.warn('同步注册到用户服务失败', e) }
      registerForm.value = { username: '', password: '', grade: '', target_role: '' }
    } else {
      alert(response.data.message)
    }
  } catch (error) {
    console.error('注册失败:', error)
    alert('注册失败，请检查后端是否启动')
  } finally {
    loading.value = false
  }
}

const handleSubmit = () => {
  if (isLogin.value) {
    handleLogin()
  } else {
    handleRegister()
  }
}
</script>

<template>
 <!-- 登录页左上角 关于我们 + 隐私政策 跳转代码 -->
<div style="position: absolute; top: 20px; left: 20px; display: flex; gap: 25px; z-index: 999;">
  <router-link to="/about-us" style="font-size: 14px; font-weight: 500; color: #409EFF;">关于我们</router-link>
  <router-link to="/privacy-policy" style="font-size: 14px; font-weight: 500; color: #409EFF;">隐私政策</router-link>
</div>
  <div class="login-container">
    <!-- ==========================================
         修改背景样式：替换为UI组设计图的星空/蓝紫渐变背景
         ========================================== -->
    <div class="background-gradient"></div>

    <div class="login-card">
      <div class="login-header">
        <!-- ==========================================
             样式恢复：完全还原为居中登录卡片，不显示任何Logo
             ========================================== -->
        <h1 class="login-title">职航——AI辅助的大学生生涯成长平台</h1>
        <p class="login-subtitle">
          {{ isLogin ? '登录您的账户' : '创建新账户' }}
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        
        <div v-if="isLogin">
            <div class="form-group">
            <label class="form-label">账号</label>
            <input
                v-model="loginForm.username"
                type="text"
                class="form-input"
                placeholder="请输入用户名 / 手机号 / 邮箱" 
                required
            >
            </div>

            <div class="form-group" style="margin-top: 20px;">
            <label class="form-label">密码</label>
            <input
                v-model="loginForm.password"
                type="password"
                class="form-input"
                placeholder="请输入密码"
                required
            >
            </div>

            <div class="form-options">
            <label class="remember-me">
                <input type="checkbox" v-model="rememberMe"> 
                <span>记住我</span>
            </label>
            <button type="button" @click="handleForgotPassword" class="forgot-password">
                忘记密码？
            </button>
            </div>
        </div>

        <div v-else>
            <div class="form-group">
            <label class="form-label">账号</label>
            <input
                v-model="registerForm.username"
                type="text"
                class="form-input"
                placeholder="设置用户名" 
                required
            >
            </div>

            <div class="form-group" style="margin-top: 20px;">
            <label class="form-label">密码</label>
            <input
                v-model="registerForm.password"
                type="password"
                class="form-input"
                placeholder="设置密码"
                required
            >
            </div>

            <div class="form-group" style="margin-top: 20px;">
            <label class="form-label">年级</label>
            <select v-model="registerForm.grade" class="form-select" required>
                <option value="">请选择年级</option>
                <option v-for="grade in gradeOptions" :key="grade" :value="grade">
                {{ grade }}
                </option>
            </select>
            </div>

            <div class="form-group" style="margin-top: 20px;">
            <label class="form-label">意向岗位</label>
            <select v-model="registerForm.target_role" class="form-select" required>
                <option value="">请选择意向岗位</option>
                <option v-for="role in roleOptions" :key="role" :value="role">
                {{ role }}
                </option>
            </select>
            </div>
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <div class="toggle-mode">
        <span class="toggle-text">
          {{ isLogin ? '还没有账户？' : '已有账户？' }}
          <button type="button" @click="toggleMode" class="toggle-link">
            {{ isLogin ? '立即注册' : '立即登录' }}
          </button>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================
   基础容器样式（保持不变）
   ========================================== */
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
}

/* ==========================================
   修改背景样式：替换为UI组设计图的星空/蓝紫渐变背景
   ========================================== */
.background-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* 使用背景图片（如果图片存在）或CSS渐变作为备选 */
  background-image: 
    url('/assets/login-bg.jpg'),
    linear-gradient(135deg, #0a1a40 0%, #1e293b 30%, #4A6FA5 70%, #2d1b4e 100%);
  background-size: cover, cover;
  background-position: center, center;
  background-repeat: no-repeat, no-repeat;
  /* 如果图片加载失败，渐变会作为底层显示 */
  z-index: -1;
}

/* 添加星空效果（可选，增强视觉） */
.background-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(2px 2px at 20% 30%, rgba(255, 255, 255, 0.3), transparent),
    radial-gradient(2px 2px at 60% 70%, rgba(255, 255, 255, 0.2), transparent),
    radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(1px 1px at 80% 10%, rgba(255, 255, 255, 0.3), transparent);
  background-size: 200% 200%;
  animation: twinkle 8s ease-in-out infinite;
  opacity: 0.6;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

.login-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}


.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  /* gap: 20px; Removed gap here to control spacing manually inside v-if blocks */
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
}

/* ==========================================
   修改输入框样式：改成UI组设计的半透明白色圆角样式
   ========================================== */
.form-input,
.form-select {
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  /* 半透明白色背景，贴合UI设计 */
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 16px;
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
  /* 添加轻微内阴影，增强立体感 */
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-select {
  color: #ffffff !important;
}

.form-select option {
  color: #333333 !important;
  background-color: #ffffff !important;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 
    0 0 0 3px rgba(96, 165, 250, 0.2),
    inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  font-size: 14px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  user-select: none;
}

.remember-me input[type="checkbox"] {
  accent-color: #60a5fa;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.forgot-password {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  transition: color 0.3s;
}

.forgot-password:hover {
  color: #a78bfa;
  text-decoration: underline;
}

/* ==========================================
   修改登录按钮样式：改成UI组设计的深蓝到紫色渐变样式
   ========================================== */
.submit-button {
  padding: 14px;
  border: none;
  border-radius: 12px;
  /* 深蓝到紫色渐变，贴合UI设计 */
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #7c3aed 100%);
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 25px;
  width: 100%;
  /* 添加按钮阴影，增强视觉层次 */
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  /* 悬浮时增强阴影和渐变 */
  background: linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #8b5cf6 100%);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toggle-mode {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.toggle-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.toggle-link {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: underline;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.toggle-link:hover {
  color: #a78bfa;
}

/* ==========================================
   响应式适配：电脑、平板、手机端都能正常显示
   ========================================== */
@media (max-width: 768px) {
  /* 平板端适配 */
  .logo-image {
    max-width: 220px;
  }
  
  .login-card {
    padding: 35px 25px;
  }
}

@media (max-width: 480px) {
  /* 手机端适配 */
  .login-card {
    padding: 30px 20px;
    margin: 10px;
  }

  .login-title {
    font-size: 24px;
  }
  
  .logo-image {
    max-width: 180px;
  }
  
  .logo-container {
    margin-bottom: 20px;
  }
}

@media (max-width: 360px) {
  /* 小屏手机适配 */
  .logo-image {
    max-width: 150px;
  }
  
  .login-title {
    font-size: 20px;
  }
}
</style>