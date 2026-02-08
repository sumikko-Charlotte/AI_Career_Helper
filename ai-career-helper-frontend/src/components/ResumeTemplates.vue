<script setup>
import { ref } from 'vue'
import { TopRight, Collection } from '@element-plus/icons-vue'

// 这里填你想嵌入的网址 (截图里的网址)
const targetUrl = 'https://www.jianlimoban-ziyuan.com/zhongwen/'

const openExternal = () => {
  window.open(targetUrl, '_blank')
}
</script>

<template>
  <div class="page-container">
    <div class="header-bar">
      <div class="left">
        <h2><el-icon><Collection /></el-icon> 精选简历模板库</h2>
        <p>为您甄选全网优质免费简历模板，助您脱颖而出</p>
      </div>
      <div class="right">
        <el-button type="primary" plain @click="openExternal">
          <el-icon style="margin-right: 5px"><TopRight /></el-icon> 
          全屏/新窗口打开
        </el-button>
      </div>
    </div>

    <div class="iframe-wrapper animate-fade">
      <iframe 
        :src="targetUrl" 
        class="web-frame"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.header-bar h2 {
  margin: 0 0 5px 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-bar p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.iframe-wrapper {
  flex: 1; /* 占满剩余高度 */
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  position: relative;
  min-height: 600px; /* 最小高度，防止太扁 */
}

.web-frame {
  width: 100%;
  height: 100%;
  display: block;
}

.animate-fade {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>