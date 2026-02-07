import axios from 'axios'

// 优先读取 Vercel 环境变量，没有则用本地默认值
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// 创建 axios 实例，统一配置请求
const request = axios.create({
  baseURL: API_BASE,
  timeout: 10000, // 10秒超时
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true'
  }
})

// 请求拦截器（可选：添加 token 等）
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器（可选：统一处理错误）
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 统一错误处理
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 导出 API_BASE 供其他文件使用
export { API_BASE }
export default request
