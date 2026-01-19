<script setup>
//import { defineProps } from 'vue'

// 保持原有导入路径，新增 require 兼容处理（避免加载失败）
import idleVideo from '../assets/idle.mp4'
import talkingVideo from '../assets/talking.mp4'

// 兼容 Vue 打包后的视频路径解析（可选，增强稳定性）
const getVideoSrc = (src) => {
  return typeof src === 'string' ? src : src.default
}

defineProps({
  isTalking: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="digital-human-container">
    <div class="video-wrapper">
      <!-- 空闲状态视频 -->
      <video
        v-show="!isTalking"
        class="digital-video"
        :src="getVideoSrc(idleVideo)"
        autoplay
        loop
        muted
        playsinline
        preload="auto" <!-- 预加载，提升切换流畅度 -->
      ></video>

      <!-- 说话状态视频 -->
      <video
        v-show="isTalking"
        class="digital-video"
        :src="getVideoSrc(talkingVideo)"
        autoplay
        loop
        muted
        playsinline
        preload="auto" <!-- 预加载，避免切换时空白 -->
      ></video>

      <div class="glow-overlay"></div>
    </div>
  </div>
</template>

<style scoped>
.digital-human-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px; /* 避免边缘紧贴容器 */
  box-sizing: border-box;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #0a192f 0%, #112940 100%); /* 加载前过渡背景 */
  box-sizing: border-box;
}

.digital-video {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 核心：完整显示视频，不裁剪 */
  display: block;
  margin: 0 auto; /* 确保视频水平居中 */
  background: transparent;
}

/* 优化渐变 overlay 不遮挡视频主体 */
.glow-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%; /* 降低渐变高度，避免遮挡视频上半部分 */
  background: linear-gradient(
    to top,
    rgba(100, 200, 255, 0.2) 0%,
    rgba(100, 200, 255, 0.08) 50%,
    rgba(100, 200, 255, 0) 100%
  );
  pointer-events: none;
  box-shadow: inset 0 -15px 30px rgba(64, 158, 255, 0.15);
}
</style>