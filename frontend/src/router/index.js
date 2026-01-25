import { createRouter, createWebHistory } from 'vue-router'
import SloganPage from '../components/SloganPage.vue'
import Login from '../components/Login.vue'
import HistoryRecord from '../components/HistoryRecord.vue' // 引入组件

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router