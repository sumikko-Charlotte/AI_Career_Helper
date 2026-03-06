import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 只创建一次 App 实例
const app = createApp(App)

// 安装路由插件
app.use(router)

// 安装 Element Plus
app.use(ElementPlus)

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载到页面
app.mount('#app')

// =========================
// 前端保活逻辑
// =========================

const BACKEND_HEALTH_URL =
  'https://ai-career-helper-backend-u1s0.onrender.com/health'
const STREAMLIT_URL =
  'https://ai-career-apper-resume-doctor-69etycfa4ohbkxdweoawk.streamlit.app'
// Vercel 前端自身一般不需要保活，这里仅保留变量以备扩展
const FRONTEND_SELF_URL = 'https://www.aicareerhelper.xyz'

const KEEPALIVE_INTERVAL = 5 * 60 * 1000 // 5 分钟

function ping(url) {
  if (!url) return
  // no-cors：不关心响应内容，只要请求发出去即可
  fetch(url, { method: 'GET', mode: 'no-cors' }).catch((err) => {
    console.warn('[frontend keepalive] 请求失败', url, err)
  })
}

if (typeof window !== 'undefined') {
  // 页面首次加载时立即 ping 一次
  ping(BACKEND_HEALTH_URL)
  ping(STREAMLIT_URL)
  // 如需也保活前端，可以放开下一行
  // ping(FRONTEND_SELF_URL)

  // 定时心跳
  setInterval(() => {
    ping(BACKEND_HEALTH_URL)
    ping(STREAMLIT_URL)
    // ping(FRONTEND_SELF_URL)
  }, KEEPALIVE_INTERVAL)
}