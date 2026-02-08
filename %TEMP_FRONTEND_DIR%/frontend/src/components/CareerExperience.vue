<script setup>
import { ref } from 'vue'
import { VideoPlay, Trophy, Timer, Star } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

// 状态控制
const currentStep = ref(0) // 0:选择角色, 1:游戏中, 2:结算
const loading = ref(false)
const selectedRole = ref('')
const scriptData = ref(null)
const currentSceneIndex = ref(0)

// 游戏数据
const hp = ref(100) // 职场能量值
const score = ref(0) // 绩效分
const logs = ref([]) // 互动记录

// 角色列表
const roles = [
  { id: 'product_manager', name: '产品经理', icon: '👔', desc: '沟通协作、需求管理、抗压能力' },
  { id: 'programmer', name: '全栈开发', icon: '💻', desc: '逻辑思维、技术攻坚、Bug修复' },
  { id: 'designer', name: 'UI设计师', icon: '🎨', desc: '审美能力、创意设计、像素眼' } // 后端没写这个，为了排版好看放着
]

// 开始游戏
const startGame = async (roleId) => {
  if (roleId === 'designer') return ElMessage.warning('该职业剧本正在编写中...')
  
  selectedRole.value = roleId
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/simulation/start`, { role_id: roleId })
    if (res.data.success) {
      scriptData.value = res.data.data
      currentStep.value = 1
      currentSceneIndex.value = 0
      hp.value = 100
      score.value = 60 // 初始及格分
      logs.value = []
    }
  } catch (e) {
    ElMessage.error('加载剧本失败')
  } finally {
    loading.value = false
  }
}

// 做出选择
const makeChoice = (option) => {
  // 1. 记录反馈
  logs.value.push({
    scene: scriptData.value.scenes[currentSceneIndex.value].text,
    choice: option.label,
    feedback: option.feedback,
    score_change: option.score_change
  })

  // 2. 更新数值
  score.value += option.score_change
  if (option.score_change < 0) hp.value -= 10 // 扣分同时扣血条
  
  // 3. 弹窗反馈
  ElMessage({
    message: option.feedback,
    type: option.score_change > 0 ? 'success' : 'warning',
    duration: 3000
  })

  // 4. 进入下一关或结算
  if (currentSceneIndex.value < scriptData.value.scenes.length - 1) {
    setTimeout(() => {
      currentSceneIndex.value++
    }, 1500)
  } else {
    setTimeout(() => {
      currentStep.value = 2 // 结算
    }, 1500)
  }
}

// 重置
const resetGame = () => {
  currentStep.value = 0
  scriptData.value = null
}

// 评价等级
const getEvaluation = () => {
  if (score.value >= 90) return { level: 'S', text: '天选打工人！这就是你的梦中情职！' }
  if (score.value >= 70) return { level: 'A', text: '表现不错，这碗饭你端得稳。' }
  if (score.value >= 60) return { level: 'B', text: '勉强及格，职场险恶，仍需努力。' }
  return { level: 'C', text: '这种工作可能不适合你，快逃！' }
}
</script>

<template>
  <div class="sim-container animate-fade-in">
    
    <div v-if="currentStep === 0" class="role-selection">
      <div class="section-header">
        <h2><el-icon><VideoPlay /></el-icon> 虚拟职业体验</h2>
        <p>沉浸式模拟真实工作场景，测试你的职业匹配度</p>
      </div>
      
      <div class="roles-grid">
        <div 
          v-for="role in roles" 
          :key="role.id" 
          class="role-card"
          @click="startGame(role.id)"
        >
          <div class="role-icon">{{ role.icon }}</div>
          <h3>{{ role.name }}</h3>
          <p>{{ role.desc }}</p>
          <el-button round size="small" type="primary" plain>开始体验</el-button>
        </div>
      </div>
    </div>

    <div v-if="currentStep === 1" class="game-interface">
      <div class="status-bar">
        <div class="bar-item">
          <span>职场能量</span>
          <el-progress :percentage="hp" :status="hp > 60 ? 'success' : 'exception'" style="width: 120px" />
        </div>
        <div class="bar-item">
          <span>当前绩效</span>
          <span class="score-num">{{ score }}</span>
        </div>
        <el-tag effect="dark">{{ scriptData.title }}</el-tag>
      </div>

      <el-card class="story-card">
        <template #header>
          <div class="story-header">
            <span><el-icon><Timer /></el-icon> 场景 {{ currentSceneIndex + 1 }} / {{ scriptData.scenes.length }}</span>
          </div>
        </template>
        
        <div class="story-content">
          {{ scriptData.scenes[currentSceneIndex].text }}
        </div>

        <div class="options-list">
          <div 
            v-for="(opt, idx) in scriptData.scenes[currentSceneIndex].options" 
            :key="idx"
            class="option-btn"
            @click="makeChoice(opt)"
          >
            <div class="opt-label">A{{ idx + 1 }}</div>
            <div class="opt-text">{{ opt.label }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <div v-if="currentStep === 2" class="result-report">
      <div class="report-card">
        <div class="badge-icon"><el-icon><Trophy /></el-icon></div>
        <h2>体验报告</h2>
        
        <div class="final-score">
          <span class="score-val">{{ score }}</span>
          <span class="score-level">{{ getEvaluation().level }}</span>
        </div>
        <p class="comment">{{ getEvaluation().text }}</p>

        <el-divider>复盘记录</el-divider>
        
        <div class="timeline">
          <div v-for="(log, i) in logs" :key="i" class="log-item">
            <div class="log-scene">场景：{{ log.scene.substring(0, 15) }}...</div>
            <div class="log-choice">你的选择：{{ log.choice }}</div>
            <div class="log-feedback" :class="log.score_change > 0 ? 'good' : 'bad'">
              {{ log.feedback }} ({{ log.score_change > 0 ? '+' : '' }}{{ log.score_change }})
            </div>
          </div>
        </div>

        <el-button type="primary" size="large" @click="resetGame" style="margin-top: 30px; width: 200px;">
          体验其他职业
        </el-button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.sim-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
  min-height: 80vh;
}

/* 角色选择 */
.section-header { text-align: center; margin-bottom: 40px; }
.section-header h2 { color: #101C4D; font-size: 28px; margin-bottom: 10px; }
.section-header p { color: #64748b; }

.roles-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
.role-card {
  background: white; border-radius: 16px; padding: 30px; text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); cursor: pointer; transition: all 0.3s;
  border: 2px solid transparent;
}
.role-card:hover { transform: translateY(-5px); border-color: #101C4D; box-shadow: 0 10px 20px rgba(16, 28, 77, 0.1); }
.role-icon { font-size: 48px; margin-bottom: 15px; }
.role-card h3 { color: #101C4D; margin-bottom: 10px; }
.role-card p { color: #94a3b8; font-size: 13px; margin-bottom: 20px; height: 40px; }

/* 游戏界面 */
.game-interface { max-width: 800px; margin: 0 auto; }
.status-bar {
  display: flex; justify-content: space-between; align-items: center;
  background: white; padding: 15px 25px; border-radius: 12px; margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.bar-item { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; color: #64748b; }
.score-num { font-size: 20px; color: #f59e0b; font-weight: 800; }

.story-card { border-radius: 16px; min-height: 400px; display: flex; flex-direction: column; }
.story-header { font-weight: bold; color: #101C4D; }
.story-content {
  font-size: 18px; line-height: 1.6; color: #334155; margin-bottom: 40px; padding: 20px 0;
  font-weight: 500;
}

.options-list { display: flex; flex-direction: column; gap: 15px; }
.option-btn {
  background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px 20px; border-radius: 12px;
  display: flex; align-items: center; gap: 15px; cursor: pointer; transition: all 0.2s;
}
.option-btn:hover { background: #eff6ff; border-color: #3b82f6; transform: translateX(5px); }
.opt-label { 
  background: #101C4D; color: white; width: 30px; height: 30px; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;
}
.opt-text { font-size: 15px; color: #1e293b; font-weight: 500; }

/* 结算报告 */
.report-card { 
  background: white; border-radius: 20px; padding: 40px; text-align: center; max-width: 600px; margin: 0 auto; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
.badge-icon { font-size: 50px; color: #f59e0b; margin-bottom: 10px; }
.final-score { margin: 20px 0; }
.score-val { font-size: 48px; font-weight: 800; color: #101C4D; margin-right: 10px; }
.score-level { 
  background: #101C4D; color: #EFE3B2; padding: 2px 10px; border-radius: 8px; 
  font-weight: bold; font-size: 20px; vertical-align: top; 
}
.comment { color: #64748b; font-size: 16px; margin-bottom: 30px; }

.timeline { text-align: left; background: #f8fafc; padding: 20px; border-radius: 12px; }
.log-item { margin-bottom: 15px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 15px; }
.log-item:last-child { border: none; margin: 0; padding: 0; }
.log-scene { font-size: 12px; color: #94a3b8; margin-bottom: 5px; }
.log-choice { font-weight: 600; color: #334155; font-size: 14px; margin-bottom: 5px; }
.log-feedback { font-size: 13px; }
.log-feedback.good { color: #10b981; }
.log-feedback.bad { color: #ef476f; }

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>