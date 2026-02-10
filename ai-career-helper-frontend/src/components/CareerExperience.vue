<script setup>
import { ref, computed } from 'vue'
import { VideoPlay, Trophy, Timer, Star } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

// 状态控制
const currentStep = ref(0) // 0:选择角色, 1:游戏中/答题, 2:结算/分析
const loading = ref(false)
const selectedRole = ref('')
const scriptData = ref(null)
const currentSceneIndex = ref(0)

// 新增：搜索 + AI 生成职业体验 & 15 道题
const searchKeyword = ref('')
const isAiMode = ref(false)            // true 表示走 /api/generate-job-test 流程
const currentJobName = ref('')         // AI 生成时记录用户输入的职业名
const testQuestions = ref([])          // 15 道测试题
const answers = ref({})                // 用户作答：{ qid: 选项文本 }
const submitting = ref(false)          // 提交分析中
const markdownRaw = ref('')            // 分析报告（Markdown 原文）

const allAnswered = computed(
  () => testQuestions.value.length > 0 &&
        testQuestions.value.every((q, idx) => answers.value[`q${idx + 1}`])
)

// 游戏数据
const hp = ref(100) // 职场能量值
const score = ref(0) // 绩效分
const logs = ref([]) // 互动记录

// 角色列表（保留：作为快捷入口）
const roles = [
  { id: 'product_manager', name: '产品经理', icon: '👔', desc: '沟通协作、需求管理、抗压能力' },
  { id: 'programmer', name: '全栈开发', icon: '💻', desc: '逻辑思维、技术攻坚、Bug修复' },
  { id: 'designer', name: 'UI设计师', icon: '🎨', desc: '审美能力、创意设计、像素眼' } // 后端没写这个，为了排版好看放着
]

// 开始游戏（快捷入口：使用后端预置剧本）
const startGame = async (roleId) => {
  if (roleId === 'designer') return ElMessage.warning('该职业剧本正在编写中...')
  
  isAiMode.value = false
  markdownRaw.value = ''
  testQuestions.value = []
  answers.value = {}

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

// 🔍 顶部搜索：优先匹配已有职业 → 否则走 /api/generate-job-test
const handleSearch = async () => {
  const jobName = searchKeyword.value.trim()
  if (!jobName) {
    return ElMessage.warning('请输入想体验的职业，例如：律师、法务、教师等')
  }

  // 1）先尝试匹配现有快捷职业卡片
  const matched = roles.find(
    r => r.name.includes(jobName) || jobName.includes(r.name)
  )
  if (matched && matched.id !== 'designer') {
    await startGame(matched.id)
    return
  }

  // 2）未匹配到 → 调用后端 AI 接口 /api/generate-job-test
  isAiMode.value = true
  currentJobName.value = jobName
  loading.value = true
  markdownRaw.value = ''
  testQuestions.value = []
  answers.value = {}

  try {
    const res = await axios.post(`${API_BASE}/api/generate-job-test`, { jobName })
    const data = res.data || {}

    // 后端业务错误（约定：返回 {code, msg}）
    if (data.code && data.code !== 200 && !data.script && !data.testQuestions) {
      throw new Error(data.msg || 'AI生成失败，请稍后重试')
    }

    const scriptText = data.script || 'AI 暂未返回体验脚本，请稍后重试'
    const questions = data.testQuestions || []

    // 体验脚本：在 AI 模式下，使用纯文本说明（无需场景切换）
    scriptData.value = {
      title: `${jobName} 职业体验`,
      script: scriptText
    }

    // 15 道测试题：补充前端本地 id（q1~q15），方便作答与分析
    const normalized = questions.slice(0, 15).map((q, idx) => ({
      id: `q${idx + 1}`,
      question: q.question || q.title || q.stem || `第 ${idx + 1} 题`,
      options: q.options || [],
      answer: q.answer || '',
      analysis: q.analysis || q.explanation || ''
    }))

    if (!normalized.length) {
      throw new Error('AI 暂未返回测试题，请稍后重试')
    }

    testQuestions.value = normalized
    answers.value = Object.fromEntries(
      normalized.map(q => [q.id, ''])
    )

    // 进入「答题 + 分析」界面
    currentStep.value = 1
    currentSceneIndex.value = 0
    hp.value = 100
    score.value = 60
    logs.value = []

    ElMessage.success(`已为「${jobName}」生成职业体验与测试题`)
  } catch (e) {
    console.error(e)
    const msg = e.response?.data?.msg || e.message || 'AI生成失败，请稍后重试'
    ElMessage.error(msg)
    isAiMode.value = false
  } finally {
    loading.value = false
  }
}

// 提交 15 题答案，生成匹配度分析报告（Markdown）
const submitAnswers = async () => {
  if (!isAiMode.value) return
  if (!currentJobName.value) return ElMessage.warning('当前职业名缺失，请重新搜索后体验')
  if (!allAnswered.value) return ElMessage.warning('请先完成全部题目再提交')

  submitting.value = true
  markdownRaw.value = ''
  try {
    const url = `${API_BASE}/api/analyze-experiment`
    const payload = {
      answers: answers.value,
      career: currentJobName.value
    }

    const res = await axios.post(url, payload)
    if (!res.data || !res.data.success) {
      throw new Error(res.data?.message || '分析生成失败，请稍后重试')
    }

    markdownRaw.value = res.data.markdown || ''
    if (!markdownRaw.value) {
      ElMessage.warning('AI 暂未返回分析内容，但你可以稍后重试')
    } else {
      ElMessage.success('职业匹配度分析已生成')
      // 进入结果步骤（沿用 currentStep = 2），但保留原有总结视图用于预置剧本
      currentStep.value = 2
    }
  } catch (e) {
    console.error('analyze-experiment request failed:', e)
    if (!e.response) {
      ElMessage.error('网络异常或无法连接后端，请检查后端是否已启动')
    } else if (e.response.status === 404) {
      ElMessage.error('分析接口不存在（404），请确认后端是否包含 POST /api/analyze-experiment')
    } else if (e.response.status >= 500) {
      ElMessage.error('后端出现异常（5xx），请稍后重试或查看后端日志')
    } else {
      ElMessage.error('分析生成失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 下载 Markdown 报告
const downloadMd = () => {
  if (!markdownRaw.value) return ElMessage.warning('暂无报告可下载')
  const filenameCareer = currentJobName.value || '职业体验'
  const blob = new Blob([markdownRaw.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `虚拟职业体验_${filenameCareer}_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.md`
  a.click()
  URL.revokeObjectURL(url)
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
  testQuestions.value = []
  answers.value = {}
  markdownRaw.value = ''
  isAiMode.value = false
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

      <!-- 顶部搜索框：优先匹配现有职业，匹配不到则走 AI 生成 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          size="large"
          placeholder="输入想体验的职业，例如：律师、法务、教师等"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prepend>职业搜索</template>
          <template #append>
            <el-button
              type="primary"
              :loading="loading"
              @click="handleSearch"
            >
              开始体验
            </el-button>
          </template>
        </el-input>
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

    <!-- 预置剧本模式：原有游戏化场景体验 -->
    <div v-if="currentStep === 1 && !isAiMode" class="game-interface">
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

    <!-- AI 生成职业体验 + 15 题模式 -->
    <div v-if="currentStep === 1 && isAiMode" class="game-interface">
      <div class="status-bar">
        <div class="bar-item">
          <span>当前职业</span>
          <span class="score-num">{{ currentJobName || 'AI 生成职业' }}</span>
        </div>
        <div class="bar-item">
          <span>提示</span>
          <span style="font-size:12px;color:#64748b;">先阅读体验脚本，再完成 15 题，最后生成匹配度分析</span>
        </div>
      </div>

      <!-- 职业体验脚本（文本） -->
      <el-card class="story-card">
        <template #header>
          <div class="story-header">
            <span><el-icon><Timer /></el-icon> {{ scriptData?.title || 'AI 职业体验脚本' }}</span>
          </div>
        </template>

        <div class="story-content ai-script">
          {{ scriptData?.script || 'AI 正在为你生成体验脚本...' }}
        </div>
      </el-card>

      <!-- 15 道测试题 -->
      <el-card v-if="testQuestions.length" class="quiz-card" style="margin-top: 20px;">
        <template #header>
          <div class="story-header">
            <span><el-icon><Star /></el-icon> 职业匹配度测试（共 {{ testQuestions.length }} 题）</span>
          </div>
        </template>

        <div class="quiz-list">
          <div
            v-for="(q, index) in testQuestions"
            :key="q.id"
            class="quiz-item"
          >
            <div class="quiz-title">
              {{ index + 1 }}. {{ q.question }}
            </div>
            <el-radio-group v-model="answers[q.id]" class="quiz-options">
              <el-radio
                v-for="(opt, oi) in q.options"
                :key="oi"
                :value="opt"
              >
                {{ String.fromCharCode(65 + oi) }}. {{ opt }}
              </el-radio>
            </el-radio-group>
            <div class="quiz-analysis" v-if="q.analysis">
              （参考解析）{{ q.analysis }}
            </div>
          </div>
        </div>

        <div class="quiz-actions">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="!allAnswered"
            @click="submitAnswers"
          >
            {{ submitting ? '生成分析中...' : '提交答案，生成匹配度分析' }}
          </el-button>
          <el-button
            type="success"
            size="large"
            plain
            :disabled="!markdownRaw"
            @click="downloadMd"
          >
            下载分析报告
          </el-button>
        </div>
      </el-card>

      <!-- 分析报告（Markdown 原文简单展示，重点是支持下载） -->
      <el-card v-if="markdownRaw" class="analysis-card" style="margin-top: 20px;">
        <template #header>
          <div class="story-header">
            <span>📄 AI 职业匹配度分析（预览）</span>
          </div>
        </template>
        <pre class="analysis-report">{{ markdownRaw }}</pre>
      </el-card>
    </div>

    <div v-if="currentStep === 2 && !isAiMode" class="result-report">
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

.search-bar {
  max-width: 520px;
  margin: 0 auto 24px;
}

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

/* AI 生成脚本 & 题目样式补充（保持与整体风格一致） */
.ai-script {
  white-space: pre-wrap;
  font-size: 14px;
  color: #334155;
}

.quiz-card {
  border-radius: 16px;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quiz-item {
  padding: 12px 0;
  border-bottom: 1px dashed #e2e8f0;
}

.quiz-item:last-child {
  border-bottom: none;
}

.quiz-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: #0f172a;
}

.quiz-options {
  margin: 4px 0 6px;
}

.quiz-analysis {
  margin-top: 4px;
  font-size: 13px;
  color: #6b7280;
}

.quiz-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.analysis-card {
  border-radius: 16px;
}

.analysis-report {
  white-space: pre-wrap;
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
}
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