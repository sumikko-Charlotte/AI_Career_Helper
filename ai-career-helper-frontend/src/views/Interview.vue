<template>
  <div class="interview-container">
    <!-- 面试官和聊天区域的左右布局容器 -->
    <div class="interview-layout-container">
      <!-- 左侧：数字人展示区（40%宽度） -->
      <div class="digital-human-section">
        <slot name="digital-human">
          <!-- 数字人组件插槽 -->
        </slot>
      </div>

      <!-- 右侧：聊天区域（60%宽度） -->
      <div class="chat-shell">
        <slot name="chat-content">
          <!-- 聊天内容插槽 -->
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
// 此组件仅用于布局样式，不包含业务逻辑
// 所有业务逻辑和数据处理都在父组件中
</script>

<style scoped>
/* 面试布局容器：左右分栏布局 */
.interview-container {
  width: 100%;
  height: 100%;
}

.interview-layout-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 420px);
  min-height: 600px;
  width: 100%;
  padding: 0;
  box-sizing: border-box;
}

/* 左侧：数字人展示区（40%宽度，居中放大显示） */
.digital-human-section {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.85);
  border: 1px solid rgba(15, 23, 42, 0.12);
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
  overflow: hidden;
  min-height: 0;
  position: relative;
  padding: 30px 20px;
  box-sizing: border-box;
}

/* 数字人视频容器（占据主要空间，居中放大） */
.digital-human-section :deep(.digital-human-container) {
  flex: 1;
  width: 100%;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.digital-human-section :deep(.video-wrapper) {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  overflow: hidden;
}

.digital-human-section :deep(.digital-video) {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

/* 右侧：聊天区域（60%宽度，支持滚动） */
.chat-shell {
  flex: 0 0 60%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
  overflow: hidden;
  min-height: 0;
}

/* 聊天窗口支持垂直滚动 */
.chat-shell :deep(.chat-window),
.chat-shell :deep(.chat-window-el) {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
}

/* 滚动条样式优化 */
.chat-shell :deep(.chat-window)::-webkit-scrollbar,
.chat-shell :deep(.chat-window-el)::-webkit-scrollbar {
  width: 6px;
}

.chat-shell :deep(.chat-window)::-webkit-scrollbar-track,
.chat-shell :deep(.chat-window-el)::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.04);
  border-radius: 3px;
}

.chat-shell :deep(.chat-window)::-webkit-scrollbar-thumb,
.chat-shell :deep(.chat-window-el)::-webkit-scrollbar-thumb {
  background: rgba(15, 23, 42, 0.2);
  border-radius: 3px;
}

.chat-shell :deep(.chat-window)::-webkit-scrollbar-thumb:hover,
.chat-shell :deep(.chat-window-el)::-webkit-scrollbar-thumb:hover {
  background: rgba(15, 23, 42, 0.3);
}

/* 响应式设计：移动端自动切换为上下布局 */
@media (max-width: 768px) {
  .interview-layout-container {
    flex-direction: column;
    height: auto;
    min-height: auto;
    gap: 16px;
    padding: 0;
  }

  .digital-human-section {
    flex: 0 0 auto;
    height: 320px;
    width: 100%;
    min-height: 320px;
    padding: 20px 16px;
    order: 1; /* 确保数字人在上方 */
  }

  .chat-shell {
    flex: 0 0 auto;
    height: calc(100vh - 520px);
    min-height: 400px;
    width: 100%;
    order: 2; /* 确保聊天框在下方 */
  }
}

/* 进一步优化移动端显示（小屏手机） */
@media (max-width: 480px) {
  .interview-layout-container {
    gap: 12px;
  }

  .digital-human-section {
    height: 280px;
    min-height: 280px;
    padding: 16px 12px;
    border-radius: 16px;
  }

  .chat-shell {
    height: calc(100vh - 480px);
    min-height: 350px;
    border-radius: 16px;
  }
}

/* 超小屏优化 */
@media (max-width: 360px) {
  .digital-human-section {
    height: 240px;
    min-height: 240px;
    padding: 12px 10px;
  }

  .chat-shell {
    height: calc(100vh - 440px);
    min-height: 300px;
  }
}
</style>
