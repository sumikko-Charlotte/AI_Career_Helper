<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
  const $router = useRouter()
// 定义props和emits
const emit = defineEmits(['login-success'])

// 响应式数据
const isLogin = ref(true) // true: 登录模式, false: 注册模式
const loading = ref(false)

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
const currentUsername = computed({
  get() {
    return isLogin.value ? loginForm.value.username : registerForm.value.username
  },
  set(val) {
    if (isLogin.value) {
      loginForm.value.username = val
    } else {
      registerForm.value.username = val
    }
  }
})

const currentPassword = computed({
  get() {
    return isLogin.value ? loginForm.value.password : registerForm.value.password
  },
  set(val) {
    if (isLogin.value) {
      loginForm.value.password = val
    } else {
      registerForm.value.password = val
    }
  }
})

// 表单选项
const gradeOptions = ['大一', '大二', '大三', '大四', '研究生']
const roleOptions = ['前端', '后端', '算法', '全栈', '测试', '产品', '设计', '其他']

// 切换登录/注册模式
const toggleMode = () => {
  isLogin.value = !isLogin.value
  // 切换时清空表单
  if (isLogin.value) {
    registerForm.value = { username: '', password: '', grade: '', target_role: '' }
  } else {
    loginForm.value = { username: '', password: '' }
  }
}

// 提交登录
const handleLogin = async () => {
  // 打印日志，验证是否获取到输入内容
  console.log('输入的用户名：', loginForm.value.username)
  console.log('输入的密码：', loginForm.value.password)

  // 简单判断（避免空值）
  if (!loginForm.value.username.trim() || !loginForm.value.password.trim()) {
    alert('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // 关键：传参时用 loginForm.value（如果是 ref 包裹的）
    const response = await axios.post(
      'http://127.0.0.1:8000/api/login',
      loginForm.value // 直接传整个表单对象
    )

    if (response.data.success) {
      alert('登录成功！')
      emit('login-success', response.data.user)
      router.push('/') // 跳转到首页
    } else {
      alert('登录失败：' + response.data.message)
    }
  } catch (error) {
    console.error('登录请求失败：', error)
    alert('登录失败，请检查后端是否启动或接口地址是否正确')
  } finally {
    loading.value = false
  }
}

// 提交注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password ||
      !registerForm.value.grade || !registerForm.value.target_role) {
    alert('请填写所有必填字段')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/register', registerForm.value)
    if (response.data.success) {
      alert('注册成功！请登录')
      isLogin.value = true // 切换到登录模式
      loginForm.value.username = registerForm.value.username // 保留用户名
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

// 提交表单
const handleSubmit = () => {
  if (isLogin.value) {
    handleLogin()
  } else {
    handleRegister()
  }
}
</script>

<template>
  <div class="login-container">
    <!-- 背景渐变 -->
    <div class="background-gradient"></div>

    <!-- 登录框 -->
    <div class="login-card">
      <!-- 标题 -->
      <div class="login-header">
        <h1 class="login-title">职航——AI辅助的大学生生涯成长平台</h1>
        <p class="login-subtitle">
          {{ isLogin ? '登录您的账户' : '创建新账户' }}
        </p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleSubmit" class="login-form">
        <!-- 用户名输入框（完全修复） -->
<div class="form-group">
  <label class="form-label">用户名</label>
  <input
    :model-value="isLogin ? loginForm.username : registerForm.username"
    @input="value => {
      if (isLogin) {
        loginForm.username = value.target.value
      } else {
        registerForm.username = value.target.value
      }
    }"
    type="text"
    class="form-input"
    placeholder="请输入用户名"
    required
  >
</div>

<!-- 密码输入框（完全修复） -->
<div class="form-group">
  <label class="form-label">密码</label>
  <input
    :model-value="isLogin ? loginForm.password : registerForm.password"
    @input="value => {
      if (isLogin) {
        loginForm.password = value.target.value
      } else {
        registerForm.password = value.target.value
      }
    }"
    type="password"
    class="form-input"
    placeholder="请输入密码"
    required
  >
</div>

        <!-- 注册额外字段 -->
        <template v-if="!isLogin">
          <!-- 年级 -->
          <div class="form-group">
            <label class="form-label">年级</label>
            <select v-model="registerForm.grade" class="form-select" required>
              <option value="">请选择年级</option>
              <option v-for="grade in gradeOptions" :key="grade" :value="grade">
                {{ grade }}
              </option>
            </select>
          </div>

          <!-- 意向岗位 -->
          <div class="form-group">
            <label class="form-label">意向岗位</label>
            <select v-model="registerForm.target_role" class="form-select" required>
              <option value="">请选择意向岗位</option>
              <option v-for="role in roleOptions" :key="role" :value="role">
                {{ role }}
              </option>
            </select>
          </div>
        </template>

        <!-- 提交按钮 -->
        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <!-- 切换模式 -->
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
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
}

/* 深色蓝调背景渐变 */
.background-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  z-index: -1;
}

/* 添加一些科技感装饰 */
.background-gradient::before {
  content: '';
  position: absolute;
  top: 10%;
  left: 10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.background-gradient::after {
  content: '';
  position: absolute;
  bottom: 10%;
  right: 10%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(147, 51, 234, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* Glassmorphism 登录卡片 */
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

/* 标题区域 */
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

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.form-input,
.form-select {
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}
/* 下拉框文字颜色 */
.form-select {
  color: #ffffff !important; /* 强制白色文字 */
}
/* 下拉选项文字颜色 */
.form-select option {
  color: #333333 !important; /* 选项文字设为深灰色，在白色背景上清晰可见 */
  background-color: #ffffff !important; /* 选项背景设为白色 */
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #60a5fa;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

/* 提交按钮 */
.submit-button {
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(96, 165, 250, 0.3);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 切换模式 */
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

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 10px;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>