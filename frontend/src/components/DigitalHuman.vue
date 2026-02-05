<script setup>
import { computed } from 'vue'

const props = defineProps({
  isTalking: {
    type: Boolean,
    default: false
  },
  gender: {
    type: String,
    default: 'female' // 'female' 或 'male'
  }
})

// 根据性别动态加载视频路径
const staticVideoPath = computed(() => {
  return props.gender === 'female' ? '/female_static.mp4' : '/male_static.mp4'
})

const speakingVideoPath = computed(() => {
  return props.gender === 'female' ? '/female_speaking.mp4' : '/male_speaking.mp4'
})
</script>

<template>
  <div class="digital-human-container">
    <div class="video-wrapper">
      <video
        v-show="!isTalking"
        class="digital-video"
        :src="staticVideoPath"
        autoplay
        loop
        muted
        playsinline
        preload="auto"
      ></video>

      <video
        v-show="isTalking"
        class="digital-video"
        :src="speakingVideoPath"
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