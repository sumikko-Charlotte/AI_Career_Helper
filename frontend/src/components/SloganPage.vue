<template>
    <div class="slogan-page">
      <!-- 左侧侧边栏 -->
      <div class="sidebar">
        <div class="logo">LOGO</div>
        <div class="menu">
          <div class="menu-item" @click="goToAboutUs">关于我们</div>
          <div class="menu-item" @click="goToPrivacyPolicy">隐私政策</div>
        </div>
      </div>
  
      <!-- 右侧主内容区 -->
      <div class="main-content">
        <h1 class="slogan">职航——AI辅助的大学生生涯成长平台</h1>
        <p class="sub-slogan">发现你的无限可能</p>
        <button class="start-btn" @click="goToRegister">开始探索</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  // 修改：点击「开始探索」按钮，直接跳转到登录页
  const goToRegister = () => {
    router.push('/login')
  }
  // 保留原有功能：关于我们和隐私政策跳转
  const goToAboutUs = () => {
    router.push('/about-us')
  }
  const goToPrivacyPolicy = () => {
    router.push('/privacy-policy')
  }
  </script>
  
  <style scoped>
  /* 整体布局 */
  .slogan-page {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: linear-gradient(135deg, #0A1A40 0%, #4A6FA5 100%);
  }
  
  /* 左侧侧边栏 */
  .sidebar {
    width: 200px;
    background: rgba(10, 26, 64, 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding-top: 40px;
    color: #FFFFFF;
  }
  
  .logo {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 80px;
  }
  
  .menu-item {
    font-size: 16px;
    margin: 16px 0;
    cursor: pointer;
  }
  
  /* 右侧主内容区 */
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
  }
  
  .slogan {
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 20px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }
  
  .sub-slogan {
    font-size: 20px;
    margin-bottom: 60px;
    opacity: 0.8;
  }
  
  .start-btn {
    background: linear-gradient(90deg, #4A89DC 0%, #967ADC 100%);
    border: none;
    border-radius: 30px;
    color: #FFFFFF;
    padding: 14px 40px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.3s ease;
  }
  
  .start-btn:hover {
    transform: scale(1.05);
  }
  </style>