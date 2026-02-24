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

/* 【修改行34-42】电脑端强制左右布局（row方向） */
.interview-layout-container {
  display: flex !important;
  flex-direction: row !important; /* 强制左右布局 */
  gap: 20px;
  height: calc(100vh - 420px);
  min-height: 600px;
  width: 100%;
  padding: 0;
  box-sizing: border-box;
}

/* 【修改行44-60】左侧数字人区域：电脑端占40%宽度，居中放大显示 */
.digital-human-section {
  flex: 0 0 40% !important; /* 电脑端强制40%宽度 */
  display: flex !important;
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

/* 【修改行95-106】右侧聊天区域：电脑端占60%宽度，支持垂直滚动 */
.chat-shell {
  flex: 0 0 60% !important; /* 电脑端强制60%宽度 */
  display: flex !important;
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

/* 【修改行140-166】手机端（<768px）：强制上下布局，数字人30%高度，聊天70%高度 */
@media (max-width: 767px) {
  .interview-layout-container {
    flex-direction: column !important; /* 强制上下布局 */
    height: 100vh !important;
    min-height: 100vh !important;
    gap: 16px;
    padding: 0;
    box-sizing: border-box;
  }

  .digital-human-section {
    flex: 0 0 30% !important; /* 手机端占30%高度 */
    width: 100% !important;
    height: 30vh !important;
    min-height: 30vh !important;
    max-height: 30vh !important;
    padding: 20px 16px;
    order: 1 !important; /* 确保数字人在上方 */
  }

  .chat-shell {
    flex: 0 0 70% !important; /* 手机端占70%高度 */
    width: 100% !important;
    height: 70vh !important;
    min-height: 70vh !important;
    max-height: 70vh !important;
    order: 2 !important; /* 确保聊天框在下方 */
  }
}

/* 【修改行168-200】小屏手机优化：保持30%和70%高度分配 */
@media (max-width: 480px) {
  .interview-layout-container {
    gap: 12px;
  }

  .digital-human-section {
    flex: 0 0 30% !important;
    height: 30vh !important;
    min-height: 30vh !important;
    max-height: 30vh !important;
    padding: 16px 12px;
    border-radius: 16px;
  }

  .chat-shell {
    flex: 0 0 70% !important;
    height: 70vh !important;
    min-height: 70vh !important;
    max-height: 70vh !important;
    border-radius: 16px;
  }
}

/* 【修改行188-200】超小屏优化：保持30%和70%高度分配 */
@media (max-width: 360px) {
  .digital-human-section {
    flex: 0 0 30% !important;
    height: 30vh !important;
    min-height: 30vh !important;
    max-height: 30vh !important;
    padding: 12px 10px;
  }

  .chat-shell {
    flex: 0 0 70% !important;
    height: 70vh !important;
    min-height: 70vh !important;
    max-height: 70vh !important;
  }
}
</style>
