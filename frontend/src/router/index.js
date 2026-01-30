import { createRouter, createWebHistory } from 'vue-router'
import SloganPage from '../components/SloganPage.vue'
import Login from '../components/Login.vue'
import HistoryRecord from '../components/HistoryRecord.vue'
import AdminLayout from '../components/AdminLayout.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import UserManage from '../views/admin/UserManage.vue'
import PromptConfig from '../views/admin/PromptConfig.vue'
import ResumeTasks from '../views/admin/ResumeTasks.vue' 
import VirtualExperiment from '../components/VirtualExperiment.vue'

const routes = [
  {
    path: '/',
    name: 'Slogan',
    component: SloganPage
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryRecord
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/virtual-experiment',
    name: 'VirtualExperiment',
    component: VirtualExperiment
  },
  {
    path: '/admin',
    component: AdminLayout,
    // 把 beforeEnter 放在 /admin 路由对象内部（正确位置）
    beforeEnter: (to, from, next) => {
      // 开发阶段直接放行，后续可替换为权限判断
      // 示例：if (localStorage.getItem('role') === 'admin') { next() } else { next('/login') }
      next()
    },
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'users', component: UserManage },
      { path: 'tasks', component: ResumeTasks },
      { path: 'prompts', component: PromptConfig },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router