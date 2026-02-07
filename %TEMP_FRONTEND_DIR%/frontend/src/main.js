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