# 🔍 App.vue 模拟面试板块 - 代码参考

## 📌 快速查找导航

本文件提供所有新增代码的位置和快速参考

---

## 1️⃣ 导入声明

### 位置
**文件**: `src/App.vue` **第 13 行**

### 代码
```javascript
// ❌ 原来的
import { Monitor, ChatDotRound, DocumentChecked, User, Odometer, MagicStick, Calendar } from '@element-plus/icons-vue'

// ✅ 现在的
import { Monitor, ChatDotRound, DocumentChecked, User, Odometer, MagicStick, Calendar, Microphone, VolumeOff } from '@element-plus/icons-vue'
```

### 说明
添加了两个新图标用于麦克风状态切换

---

## 2️⃣ 面试官状态管理

### 位置
**文件**: `src/App.vue` **第 195-225 行**

### 关键代码
```javascript
// ============================================
// 面试官头像与状态栏相关变量
// ============================================
const interviewerStatus = ref('idle') // 'idle' | 'thinking' | 'speaking'

// 监听 chatSending 状态，更新面试官头像动画状态
watch(
  () => chatSending.value,
  (newVal) => {
    if (newVal) {
      interviewerStatus.value = 'thinking'
    }
  }
)

watch(
  () => chatHistory.value,
  () => {
    if (chatHistory.value.length > 0) {
      const lastMsg = chatHistory.value[chatHistory.value.length - 1]
      if (lastMsg.role === 'ai' && !chatSending.value) {
        interviewerStatus.value = 'speaking'
        // 3秒后恢复到 idle
        setTimeout(() => {
          interviewerStatus.value = 'idle'
        }, 3000)
      }
    }
  },
  { deep: true }
)
```

### 工作流程
```
点击发送 → chatSending=true → thinking (黄色)
         ↓
      后端返回 → chatSending=false → speaking (绿色)
         ↓
       3秒后 → idle (蓝色)
```

---

## 3️⃣ 语音识别系统

### 位置
**文件**: `src/App.vue` **第 226-285 行**

### 变量声明
```javascript
const isListening = ref(false)
let recognition = null
```

### 初始化函数
```javascript
const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    ElMessage.warning('您的浏览器不支持语音输入功能')
    return
  }

  recognition = new SpeechRecognition()
  recognition.continuous = false
  recognition.interimResults = false
  recognition.lang = 'zh-CN' // 中文识别

  recognition.onstart = () => {
    isListening.value = true
  }

  recognition.onresult = (event) => {
    let transcript = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        transcript += event.results[i][0].transcript
      }
    }
    if (transcript) {
      chatInput.value += transcript  // 填入输入框
    }
  }

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error)
    ElMessage.warning(`语音识别出错: ${event.error}`)
  }

  recognition.onend = () => {
    isListening.value = false
  }
}
```

### 切换函数
```javascript
const toggleSpeechRecognition = () => {
  if (!recognition) {
    initSpeechRecognition()
  }

  if (isListening.value) {
    recognition.stop()
  } else {
    recognition.start()
  }
}
```

### 关键参数
| 参数 | 值 | 说明 |
|------|-----|------|
| `continuous` | `false` | 说话结束自动停止 |
| `interimResults` | `false` | 仅处理最终结果 |
| `lang` | `'zh-CN'` | 中文简体 |

---

## 4️⃣ onMounted 生命周期

### 位置
**文件**: `src/App.vue` **第 288-295 行**

### 代码
```javascript
onMounted(() => {
  initSpeechRecognition()  // 初始化语音识别
  const onResize = () => {
    sandboxChart && sandboxChart.resize()
    resumeRadarChart && resumeRadarChart.resize()
  }
  window.addEventListener('resize', onResize)
  if (activeMenu.value === '3') nextTick(() => initSandboxChart())
})
```

---

## 5️⃣ 模板 - 面试官状态栏

### 位置
**文件**: `src/App.vue` **第 676-704 行** (Template)

### HTML 结构
```vue
<div class="chat-shell">
  <!-- 面试官状态栏 -->
  <div class="interviewer-header">
    <div class="interviewer-container">
      <div class="interviewer-avatar-wrapper" :class="`status-${interviewerStatus}`">
        <img
          :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=Interviewer`"
          alt="interviewer"
          class="interviewer-avatar"
        />
        <!-- 状态指示器 -->
        <div class="status-indicator" v-if="interviewerStatus !== 'idle'">
          <span class="pulse"></span>
        </div>
      </div>
      <div class="interviewer-info">
        <div class="interviewer-name">AI 面试官</div>
        <div class="interviewer-status">
          <span v-if="interviewerStatus === 'thinking'" class="status-text thinking">
            🤔 正在思考...
          </span>
          <span v-else-if="interviewerStatus === 'speaking'" class="status-text speaking">
            💬 正在回复...
          </span>
          <span v-else class="status-text idle">
            ✓ 等待您的回答
          </span>
        </div>
      </div>
    </div>
  </div>
  <!-- ... 其他内容 ... -->
</div>
```

---

## 6️⃣ 模板 - 麦克风按钮

### 位置
**文件**: `src/App.vue` **第 745-772 行** (Template)

### HTML 结构
```vue
<div class="input-area">
  <div class="input-wrapper">
    <!-- 麦克风按钮 -->
    <el-button
      :type="isListening ? 'danger' : 'default'"
      :icon="isListening ? 'VolumeOff' : 'Microphone'"
      circle
      size="large"
      @click="toggleSpeechRecognition"
      :title="isListening ? '停止录音' : '开始语音输入'"
      class="mic-btn"
    >
    </el-button>

    <el-input
      v-model="chatInput"
      placeholder="输入你的回答或点击🎙️进行语音输入…（Enter 发送）"
      @keyup.enter="sendMessage"
      size="large"
      class="chat-input-field"
    >
      <template #append>
        <el-button type="primary" :loading="chatSending" @click="sendMessage">
          发送
        </el-button>
      </template>
    </el-input>
  </div>
</div>
```

### 动态绑定说明
| 属性 | 含义 |
|------|------|
| `:type="isListening ? 'danger' : 'default'"` | 红色/灰色按钮 |
| `:icon="isListening ? 'VolumeOff' : 'Microphone'"` | 🔇/🎙️ 图标 |
| `:title` | 鼠标悬停提示 |

---

## 7️⃣ 模板 - 聊天消息气泡

### 位置
**文件**: `src/App.vue` **第 707-740 行** (Template)

### AI 消息气泡
```vue
<div v-for="(msg, i) in chatHistory" :key="i" class="msg-row" :class="msg.role">
  <div class="avatar" v-if="msg.role === 'ai'">
    <img
      :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=Interviewer`"
      alt="AI"
      class="avatar-img"
    />
  </div>
  <div class="bubble">
    <div class="bubble-text">{{ msg.content }}</div>
  </div>
  <!-- ... 用户头像 ... -->
</div>
```

### 用户消息气泡
```vue
<div class="avatar" v-if="msg.role === 'user'">
  <div class="avatar-user-placeholder">
    <el-icon><User /></el-icon>
  </div>
</div>
```

### Loading 动画
```vue
<!-- Loading 提示 -->
<div v-if="chatSending" class="msg-row ai">
  <div class="avatar">
    <img
      :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=Interviewer`"
      alt="AI"
      class="avatar-img"
    />
  </div>
  <div class="bubble loading-bubble">
    <div class="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</div>
```

---

## 8️⃣ CSS 动画 - 呼吸效果

### 位置
**文件**: `src/App.vue` **第 1034-1070 行** (Style)

### 呼吸动画
```css
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

@keyframes pulse-animate {
  0% { opacity: 1; transform: scale(1); }
  100% { opacity: 0.2; transform: scale(1.5); }
}
```

### 状态类
```css
.interviewer-avatar-wrapper.status-thinking {
  animation: breathe 2s ease-in-out infinite;
  border-color: rgba(255,193,7,0.60);
  box-shadow: 0 0 12px rgba(255,193,7,0.30);
}

.interviewer-avatar-wrapper.status-speaking {
  animation: breathe 1.5s ease-in-out infinite;
  border-color: rgba(76,175,80,0.60);
  box-shadow: 0 0 16px rgba(76,175,80,0.35);
}
```

---

## 9️⃣ CSS - 气泡样式

### 位置
**文件**: `src/App.vue` **第 1165-1227 线** (Style)

### AI 气泡（灰色）
```css
.msg-row.ai .bubble { 
  background: rgba(240,242,245,0.95);
  border-radius: 16px 16px 16px 6px;  /* 左下凹陷 */
  border: 1px solid rgba(15,23,42,0.08);
  color: #0f172a;
}
```

### 用户气泡（蓝色）
```css
.msg-row.user .bubble {
  background: linear-gradient(135deg, rgba(64,158,255,0.92), rgba(64,158,255,0.68));
  color: #fff;
  border: 1px solid rgba(64,158,255,0.40);
  border-radius: 16px 16px 6px 16px;  /* 右下凹陷 */
}
```

### 文本样式
```css
.bubble-text { 
  line-height: 1.65; 
  font-size: 14px; 
  white-space: pre-wrap;
  word-break: break-word;
}
```

---

## 🔟 CSS - Loading 动画

### 位置
**文件**: `src/App.vue` **第 1229-1267 行** (Style)

### 代码
```css
@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-8px);
  }
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(15,23,42,0.40);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
```

---

## 🎯 常用查询

### 想修改呼吸动画速度？
```javascript
// Script 部分（第 212-220 行）
setTimeout(() => {
  interviewerStatus.value = 'idle'
}, 3000)  // ← 改这个数字（单位：ms）
```

### 想改变头像来源？
```vue
// Template 部分（第 681、712、724 行）
:src="`https://api.dicebear.com/7.x/avataaars/svg?seed=Interviewer`"
     ↑ 改这个 seed 值
```

### 想支持其他语言？
```javascript
// Script 部分（第 242 行）
recognition.lang = 'zh-CN'  // ← 改这个
// 支持：en-US, es-ES, fr-FR, de-DE 等
```

### 想改变气泡宽度？
```css
/* Style 部分（第 1179 行）*/
max-width: 70%;  // ← 改这个百分比
```

### 想改变颜色方案？
```css
/* Style 部分 */
// AI 气泡背景：第 1219 行
background: rgba(240,242,245,0.95);

// 用户气泡背景：第 1224 行
background: linear-gradient(135deg, rgba(64,158,255,0.92), ...);

// 思考状态颜色：第 1109 行
color: #F57F17;  /* 黄色 */

// 说话状态颜色：第 1114 行
color: #388E3C;  /* 绿色 */
```

---

## 📍 行号速查表

| 功能 | 部分 | 行号范围 |
|------|------|---------|
| 导入图标 | Script | 13 |
| 面试官状态变量 | Script | 195 |
| 面试官监听器 | Script | 197-224 |
| 语音变量 | Script | 226-227 |
| 初始化语音识别 | Script | 229-263 |
| 切换语音识别 | Script | 265-275 |
| onMounted 钩子 | Script | 277-283 |
| 面试官状态栏 | Template | 676-704 |
| 聊天窗口 | Template | 706-740 |
| 麦克风按钮 | Template | 750-761 |
| 输入框 | Template | 763-773 |
| 面试官样式 | Style | 1005-1120 |
| 气泡样式 | Style | 1165-1227 |
| Loading 动画 | Style | 1229-1267 |

---

## ✨ 最佳实践

### 调试技巧
```javascript
// 在浏览器控制台查看状态
console.log(interviewerStatus.value)  // 当前状态
console.log(isListening.value)        // 录音状态
console.log(chatHistory.value)        // 对话历史
```

### 测试检查清单
- [ ] 刷新页面后面试官头像显示正常
- [ ] 点击发送时头像变黄并呼吸
- [ ] AI 回复后头像变绿
- [ ] 3 秒后头像变蓝恢复
- [ ] 麦克风按钮默认灰色
- [ ] 点击麦克风按钮变红
- [ ] 说话完成自动填入文本
- [ ] AI 气泡在左，用户气泡在右
- [ ] 没有控制台错误

---

**参考文档版本**：1.0
**最后更新**：2026-01-17
**文档完成度**：100%
