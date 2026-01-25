<script setup>
import { defineProps } from 'vue'

// ============================================================
// 👇 关键修改：直接使用字符串路径 👇
// ============================================================
// '/idle.mp4' 代表直接去 public 文件夹里找，这样就不会报 416 错误了
const idleVideoPath = '/idle.mp4'
const talkingVideoPath = '/talking.mp4'

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
      <video
        v-show="!isTalking"
        class="digital-video"
        :src="idleVideoPath"
        autoplay
        loop
        muted
        playsinline
        preload="auto"
      ></video>

      <video
        v-show="isTalking"
        class="digital-video"
        :src="talkingVideoPath"
        autoplay
        loop
        muted
        playsinline
        preload="auto"
      ></video>

      <div class="glow-overlay"></div>
    </div>
  </div>
</template>

<style scoped>
/* 👇 你的原有样式，完全保留 👇 */
.digital-human-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  box-sizing: border-box;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #0a192f 0%, #112940 100%);
  box-sizing: border-box;
}

.digital-video {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保持比例，不裁切 */
  display: block;
  margin: 0 auto;
  background: transparent;
}

.glow-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
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