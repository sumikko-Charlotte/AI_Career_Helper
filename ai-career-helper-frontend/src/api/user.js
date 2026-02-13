import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'https://ai-career-helper-backend-u1s0.onrender.com'

// 创建 axios 实例
const request = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

// 获取用户资料
export const getUserProfile = (username) => {
  return request.get('/api/user/profile', {
    params: { username }
  })
}

// 更新用户资料（PUT 请求）
export const updateUserProfile = (data) => {
  return request.put('/api/user/profile', data)
}

// 上传头像
export const uploadAvatar = (formData) => {
  return request.post('/api/user/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 修改密码
export const changePassword = (data) => {
  return request.post('/api/user/change-password', data)
}
