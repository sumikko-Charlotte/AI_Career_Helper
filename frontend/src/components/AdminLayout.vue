<script setup>
import { 
  DataLine, User, Setting, SwitchButton, 
  Document, Monitor 
} from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const handleLogout = () => {
  localStorage.removeItem('remembered_username')
  router.push('/')
}
</script>

<template>
  <div class="admin-layout">
    <el-container class="layout-container">
      <el-aside width="240px" class="admin-aside">
        <div class="logo-area">
          <div class="logo-icon">职</div>
          <span class="logo-text">职航管理后台</span>
        </div>
        
        <el-menu 
  router 
  :default-active="route.path" 
  background-color="#101C4D" 
  text-color="#a0aec0" 
  active-text-color="#EFE3B2"
  class="custom-menu"
>
  <el-menu-item index="/admin/dashboard">
    <el-icon><DataLine /></el-icon><span>数据大屏</span>
  </el-menu-item>
  
  <el-menu-item index="/admin/users">
    <el-icon><User /></el-icon><span>用户管理</span>
  </el-menu-item>
  
  <el-menu-item index="/admin/tasks">
    <el-icon><Document /></el-icon><span>简历任务</span>
  </el-menu-item>

  <el-menu-item index="/admin/prompts">
    <el-icon><Setting /></el-icon><span>Prompt 配置</span>
  </el-menu-item>
</el-menu>

        <div class="aside-footer">
          <p>© 2026 CareerFly Admin</p>
        </div>
      </el-aside>
      
      <el-container>
        <el-header class="admin-header">
          <div class="header-left">
            <span class="welcome-text">欢迎回来，管理员</span>
          </div>
          <div class="header-right">
            <el-button type="danger" plain size="small" :icon="SwitchButton" @click="handleLogout">
              退出登录
            </el-button>
          </div>
        </el-header>
        
        <el-main class="admin-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.layout-container { height: 100vh; }

/* 复刻 UI 组的深蓝色调 */
.admin-aside {
  background: linear-gradient(180deg, #101C4D 0%, #000025 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
  z-index: 10;
}

.logo-area {
  height: 80px;
  display: flex;
  align-items: center;
  padding-left: 24px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.logo-icon {
  width: 36px; height: 36px;
  background: #EFE3B2; /* 金色点缀 */
  color: #101C4D;
  border-radius: 8px;
  font-weight: 900;
  display: flex; align-items: center; justify-content: center;
  margin-right: 12px;
}
.logo-text { font-size: 18px; font-weight: bold; color: #fff; letter-spacing: 1px; }

.custom-menu { border-right: none; margin-top: 20px; flex: 1; }

.admin-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 30px;
  height: 64px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.admin-main { background-color: #f8f9fa; padding: 24px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>