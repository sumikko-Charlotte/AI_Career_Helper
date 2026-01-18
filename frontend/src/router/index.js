import { createRouter, createWebHistory } from 'vue-router'
import SloganPage from '../components/SloganPage.vue'
import Login from '../components/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Slogan',
    component: SloganPage
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