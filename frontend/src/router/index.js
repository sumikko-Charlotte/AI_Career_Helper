import { createRouter, createWebHistory } from 'vue-router'
import SloganPage from '../components/SloganPage.vue'
import Login from '../components/Login.vue'
import HistoryRecord from '../components/HistoryRecord.vue'
import AdminLayout from '../components/AdminLayout.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import UserManage from '../views/admin/UserManage.vue'
import PromptConfig from '../views/admin/PromptConfig.vue'
import ResumeTasks from '../views/admin/ResumeTasks.vue' 
import AdminGuide from '../views/admin/AdminGuide.vue'
import VirtualExperiment from '../components/VirtualExperiment.vue'
import AdminProfile from '../views/admin/AdminProfile.vue'
import ExploreGuide from '../views/ExploreGuide.vue'
import AboutUs from '@/views/AboutUs.vue'
import PrivacyPolicy from '@/views/PrivacyPolicy.vue'

const routes = [
  // 第1页：默认首页（slogan + 开始探索按钮）
  {
    path: '/',
    name: 'Slogan',
    component: SloganPage
  },
  // 第2页：登录页
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  // 第3页：过渡导航页（功能入口）
  {
    path: '/explore',
    name: 'Explore',
    component: ExploreGuide
  },
  // 第4页：功能页（主应用界面）
  // 注意：功能页实际上就是 App.vue 在登录后显示的主应用界面
  // 当用户从过渡页点击功能入口时，会跳转到 /app 路由
  // App.vue 会根据路由路径判断，在登录后显示主应用界面
  {
    path: '/app',
    name: 'App',
    // 使用一个简单的占位组件，实际内容由 App.vue 根据路由和登录状态渲染
    component: { template: '<div></div>' }
  },
  // 保留功能路由
  {
    path: '/virtual-experiment',
    name: 'VirtualExperiment',
    component: VirtualExperiment
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryRecord
  },
  // 关于我们和隐私政策（保留原有功能）
  {
    path: '/about-us',
    name: 'AboutUs',
    component: AboutUs
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy
  },
  // 管理员路由：默认进入「功能引导」而不是「数据大屏」
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/guide', // 访问 /admin 时自动跳转到功能引导
    beforeEnter: (to, from, next) => {
      next()
    },
    children: [
      { path: 'guide', component: AdminGuide },
      { path: 'dashboard', component: Dashboard },
      { path: 'users', component: UserManage },
      // 兼容友好别名（保留旧风格路径）
      { path: 'user-management', redirect: '/admin/users' },
      { path: 'tasks', component: ResumeTasks },
      { path: 'resume-tasks', redirect: '/admin/tasks' },
      { path: 'prompts', component: PromptConfig },
      { path: 'prompt-config', redirect: '/admin/prompts' },
      { path: 'profile', component: AdminProfile },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router