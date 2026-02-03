<script setup>
// ==========================================
// 1. 导入依赖 (Imports)
// ==========================================
import { ref, reactive, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'
import MarkdownIt from 'markdown-it'
import {
  Monitor, ChatDotRound, DocumentChecked, User, Odometer, MagicStick,
  Calendar, SwitchButton, CircleCheck, VideoPlay, Trophy, Loading, Compass, Aim,
  Microphone, Clock, Collection
} from '@element-plus/icons-vue'

// 引入组件
import Login from './components/Login.vue'
import ResumeDoctor from './components/ResumeDoctor.vue'
import DigitalHuman from './components/DigitalHuman.vue'
import UserProfile from './components/UserProfile.vue'
import { useRouter, useRoute } from 'vue-router'
import HistoryRecord from './components/HistoryRecord.vue'
import ResumeTemplates from './components/ResumeTemplates.vue'
import VirtualExperiment from './components/VirtualExperiment.vue'
import CareerExperience from './components/CareerExperience.vue'
const md = new MarkdownIt()

const router = useRouter()
const route = useRoute()
// ==========================================
// 2. 核心变量定义 (State) - 放在最前防止报错
// ==========================================
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8001'
console.debug('[App] API_BASE ->', API_BASE)
const currentUser = ref(null)
const activeMenu = ref('0')

// 如果路由携带 focus 参数（例如来自 /explore 的跳转），则将主界面聚焦到对应功能
// 处理来自 /explore 的一次性聚焦参数（可在首次加载或运行时实时响应）
const applyFocus = (f) => {
  if (!f) return
  activeMenu.value = String(f)
  // 和 handleSelect 中的行为保持一致：按需初始化对应模块
  if (String(f) === '3') nextTick(() => initSandboxChart())
  if (String(f) === '1') nextTick(() => initResumeRadar())
  if (String(f) === '7') router.push('/virtual-experiment').catch(() => {})
  // 处理一次性参数后清理，避免影响后续路由判断
  router.replace({ path: route.path, query: {} }).catch(() => {})
}

onMounted(() => {
  applyFocus(route.query.focus)
})

// 监听路由 query 中 focus 的变化（例如从 /explore push 到 /app?focus=2），并在运行时响应
watch(() => route.query.focus, (f) => {
  applyFocus(f)
})

// 顶部导航行为：直接跳转到探索引导页
const goExplore = () => router.push('/explore')

// --- 语音模块变量 (新增) ---
const isRecording = ref(false)
let recognitionInstance = null

// --- 聊天模块变量 ---
const chatInput = ref('')
const chatSending = ref(false)
const interviewerState = ref('neutral') // 控制数字人动作
const agentCalling = ref(false)
const chatHistory = ref([
  {
    role: 'ai',
    content: '你好，我是 AI 面试官。我们从工程化开始：请你简述一下你对 RESTful API 的理解，并说明你会如何做版本管理与错误码设计。'
  }
])
const jobsData = ref([])

// --- 生涯规划变量 ---
const roadmapGrade = ref('大一')
const roadmapRole = ref('算法')
const roadmapLoading = ref(false)
const roadmapData = ref([])
const roadmapRadar = ref(null)
const roadmapComment = ref('')
const radarChartRef = ref(null)
const roadmapCaptureRef = ref(null)
const personalityNote = ref('')
const careerFiles = ref([])
const careerGenerating = ref(false)
const careerPlanMarkdown = ref('')

// --- 简历医生变量 ---
const resumeText = ref('')
const resumeResult = ref(null)
const resumeAnalyzing = ref(false)
const resumeProgress = ref(0)
let resumeProgressTimer = null
const resumeRadarRef = ref(null)
let resumeRadarChart = null

// --- 竞争力沙盘变量 ---
const sandboxChartRef = ref(null)
let sandboxChart = null
let sandboxRafId = 0
let sandboxPending = false
const radarValues = reactive({
  gpa: 85, project: 70, intern: 60, competition: 80, english: 90, leader: 75
})

// --- 静态选项数据 (保留原样) ---
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]
const gradeOptions = ['大一', '大二', '大三', '大四', '研一', '研二', '研三', '博士']
const roleOptions = [
  { label: '互联网/AI', options: ['互联网', '电子商务', '计算机软件', '生活服务', '企业服务', '医疗健康', '游戏', '社交网络与媒体', '人工智能', '云计算', '在线教育', '计算机服务', '大数据', '广告营销', '物联网新零售', '信息安全'] },
  { label: '电子/通信/半导体', options: ['半导体', '电子', '通信', '智能硬件', '运营商', '计算机硬件', '硬件开发', '芯片', '集成电路', '消费电子', '网路设备', '增值服务'] },
  { label: '金融', options: ['互联网金融', '银行', '投资', '融资', '证券', '期货基金', '保险', '租赁', '拍卖', '典当', '担保信托', '财富管理'] },
  { label: '专业服务', options: ['咨询财务', '审计', '税务', '人力资源服务', '法律检测', '知识产权', '翻译'] },
  { label: '制造业', options: ['电器器械', '金属制品', '非金属矿物制品', '橡胶塑料制品', '化学原料', '化学制品', '仪器仪表', '自动化设备', '印刷', '包装', '造纸', '铁路', '船舶', '航空航天材料', '电子设备', '新材料', '机械设备', '重工', '工业自动化', '原材料加工', '摸具'] },
  { label: '房地产/建筑', options: ['装修装饰', '建筑工程', '土木工程', '机电工程', '物业管理', '房地产中介', '租赁', '建筑材料', '房地产开发经营', '建筑设计', '建筑工程咨询服务', '土地与公共设施管理', '工程施工'] },
  { label: '交通运输/物流', options: ['即时配送', '快递', '公路', '物流', '同城货运', '跨境物流', '装卸搬运', '仓储业', '客运服务', '铁路', '机场'] },
  { label: '制药/医疗', options: ['医疗服务', '医美服务', '医疗器械', 'IVD生物', '制药', '药物批发', '医疗研发外包'] },
  { label: '消费品/批发/零售', options: ['批发', '零食进出口贸易', '食品/饮料/烟酒', '服装', '纺织', '家具', '家电', '珠宝首饰'] },
  { label: '广告/传媒/文化/体育', options: ['文化艺术', '娱乐体育', '广告', '公关', '会展', '广播', '影视新闻', '出版社'] },
  { label: '教育培训', options: ['辅导机构', '职业培训', '学前教育学校', '学历教育', '学士研究'] },
  { label: '服务业', options: ['餐饮', '休闲', '娱乐运动', '健身保健', '养生', '景区', '摄影', '美容', '美发', '宠物服务', '婚庆', '家政服务', '旅游', '酒店'] },
  { label: '汽车', options: ['新能源汽车', '汽车智能网联', '汽车经销商', '汽车后市场', '汽车研发', '制造汽车零件', '摩托车/自行车之制造', '4S店'] },
  { label: '能源/化工/环保', options: ['光伏', '储能', '电池', '风电', '新能源环保', '电力', '热力', '水利', '石油', '石化', '矿产', '地质采掘', '冶炼'] },
  { label: '政府/非盈利机构/其他', options: ['公共事业', '农业', '林业', '牧业', '渔业', '政府'] }
]

// 新增：职业测评跳转方法（适配script setup）
const jumpToAssessment = () => {
  // 替换为你的测评页面实际URL
  window.open('https://minke8.cn/gd7.html', '_blank')
}
// ==========================================
// 3. 语音功能 (TTS & STT) - 核心新增
// ==========================================

// 3.1 获取最佳声音 (优先 Edge 晓晓)
const getBestVoice = () => {
  const voices = window.speechSynthesis.getVoices()
  return (
    voices.find(v => v.name.includes('Xiaoxiao') || v.name.includes('Yaoyao')) || 
    voices.find(v => v.name.includes('Google') && v.lang.includes('zh')) ||      
    voices.find(v => v.lang.includes('zh'))                                       
  )
}

// ============================================
// 👇 强制启用“自然语音”版 (请替换原有的 speakText)
// ============================================

// 全局变量防止秒断
let currentUtterance = null 

const speakText = (text) => {
  if (!window.speechSynthesis) return

  // 1. 强制打断之前的发音
  window.speechSynthesis.cancel()

  // 2. 创建发音请求
  currentUtterance = new SpeechSynthesisUtterance(text)

  // 3. 🔥 核心修改：精准挑选最逼真的声音
  const voices = window.speechSynthesis.getVoices()
  
  // 优先级规则：
  // 第一名：Edge 的 "Xiaoxiao" (晓晓 - 最自然)
  // 第二名：Edge 的 "Yunxi" (云希 - 男声，也很自然)
  // 第三名：任何带有 "Natural" (自然) 标签的中文声音
  // 第四名：Google 的中文 (Chrome 里的)
  // 第五名：实在没有，才用保底的系统中文
  
  const bestVoice = 
    voices.find(v => v.name.includes('Xiaoxiao')) || 
    voices.find(v => v.name.includes('Yunxi')) || 
    voices.find(v => v.name.includes('Natural') && v.lang.includes('zh')) || 
    voices.find(v => v.name.includes('Google') && v.lang.includes('zh')) ||
    voices.find(v => v.lang.includes('zh'))

  if (bestVoice) {
    currentUtterance.voice = bestVoice
    // 在控制台打印出来，看看是不是选对了
    console.log('✅ 当前使用的是:', bestVoice.name) 
  } else {
    console.warn('⚠️ 未找到高质量中文语音，使用默认声音')
  }

  // 4. 微调参数 (让声音更有情感一点)
  currentUtterance.lang = 'zh-CN'
  currentUtterance.rate = 1.0  // 语速：1.0 是标准，1.1 稍微轻快
  currentUtterance.pitch = 1.0 // 音调

  // 5. 联动数字人状态
  currentUtterance.onstart = () => { 
    console.log('▶️ 开始播放...')
    if (typeof interviewerState !== 'undefined') interviewerState.value = 'talking' 
  }
  
  const finish = () => {
    console.log('⏹️ 播放结束')
    if (typeof interviewerState !== 'undefined') interviewerState.value = 'neutral'
  }
  
  currentUtterance.onend = finish
  currentUtterance.onerror = (e) => {
    console.error('❌ 播放出错:', e)
    finish()
  }

  // 6. 播放
  window.speechSynthesis.speak(currentUtterance)
}// 3.3 语音输入
const toggleVoiceInput = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) return ElMessage.error('请使用 Edge 或 Chrome 浏览器')

  // 停止录音
  if (isRecording.value) {
    if (recognitionInstance) recognitionInstance.stop()
    isRecording.value = false
    return
  }

  // 开始录音
  recognitionInstance = new SpeechRecognition()
  recognitionInstance.lang = 'zh-CN'
  recognitionInstance.interimResults = false

  recognitionInstance.onstart = () => {
    isRecording.value = true
    ElMessage.success('请说话...')
  }
  recognitionInstance.onend = () => {
    isRecording.value = false
  }
  recognitionInstance.onresult = (event) => {
    const text = event.results[0][0].transcript
    if (text) {
      chatInput.value = text // 填入
      setTimeout(() => sendMessage(), 100) // 自动发送
    }
  }
  recognitionInstance.start()
}

// ==========================================
// 4. 业务逻辑 (Business Logic)
// ==========================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const goToResumeDoctor = () => window.open('http://localhost:8501', '_blank')

const scrollChatToBottom = () => {
  const el = document.querySelector('.chat-window')
  if (el) el.scrollTop = el.scrollHeight
}

const fetchJobsData = async () => {
  try {
    const res = await axios.post(`${API_BASE}/api/recommend`)
    if (res.data.success) jobsData.value = res.data.data
  } catch (e) { console.error(e) }
}

// --- 发送消息 (已集成语音) ---
const sendMessage = async () => {
  if (!chatInput.value || chatSending.value) return
  const userMsg = chatInput.value
  
  chatHistory.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  await nextTick()
  scrollChatToBottom()

  try {
    chatSending.value = true
    // 可选：为模拟面试场景注入 Admin 配置的提示词（localStorage ）
    const defaultInterviewPrompt = `你是一个严厉但公正的技术面试官。请根据用户的求职意向（如Java后端），提出有深度的技术问题。\n每次只问一个问题，并在用户回答后进行追问。不要一次性抛出太多问题。`
    const interviewPrompt = localStorage.getItem('admin_ai_interview') || defaultInterviewPrompt

    const res = await axios.post(`${API_BASE}/api/chat`, { message: userMsg, system_prompt: interviewPrompt })
    let reply = res.data?.reply || res.data?.reply_text || '（未返回内容）'

    if (jobsData.value.length > 0 && Math.random() > 0.5) { 
      const randomJob = jobsData.value[Math.floor(Math.random() * jobsData.value.length)]
      reply += `\n\n💼 推荐：${randomJob['岗位']} - ${randomJob['平均薪资']}`
    }

    chatHistory.value.push({ role: 'ai', content: reply })
    
    // 🔥 触发语音播报
    speakText(reply) 

    await nextTick()
    scrollChatToBottom()
  } catch (e) {
    chatHistory.value.push({ role: 'ai', content: '连接后端失败' })
  } finally {
    chatSending.value = false
  }
}

// --- 召唤 Agent (已集成语音) ---
const callAgent = async () => {
  if (agentCalling.value) return
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }

  agentCalling.value = true
  chatHistory.value.push({ role: 'ai', content: 'Agent 正在分析您的画像...' })
  scrollChatToBottom()

  try {
    const res = await axios.post(`${API_BASE}/api/agent`, {
      grade: currentUser.value.grade || '大一',
      target_job: currentUser.value.target_role || '算法'
    })
    
    setTimeout(() => {
       const replyText = res.data.reply || '为您找到以下推荐岗位：'
       const jobList = res.data.data || []

       chatHistory.value.push({ 
         role: 'ai', 
         content: replyText, 
         jobs: jobList 
       })
       
       // 🔥 触发语音播报
       speakText(replyText)
       
       agentCalling.value = false
       scrollChatToBottom()
    }, 2000)
    
  } catch (e) {
    console.error(e)
    chatHistory.value.push({ role: 'ai', content: 'Agent 掉线了' })
    agentCalling.value = false
  }
}

// --- 投递逻辑 ---
const handleApply = async (job) => {
  job._loading = true
  try {
    ElMessage.info(`正在对接 HR...`)
    await sleep(1500) 
    await axios.post(`${API_BASE}/api/apply`, {
      username: currentUser.value ? currentUser.value.username : '游客',
      job_name: job['岗位'],
      salary: job['平均薪资'] || '面议'
    })
    ElMessage.success(`✅ 投递成功！`)
    job._applied = true 
  } catch (e) {
    console.error(e)
    ElMessage.error('投递失败')
  } finally {
    job._loading = false
  }
}

// ==========================================
// 5. 复杂模块逻辑 (简历/沙盘/规划)
// ==========================================

// --- 简历医生 ---
const resumeRadarIndicator = computed(() => {
  const dims = resumeResult.value?.dimensions || []
  return dims.map((d) => ({ name: d.name, max: 100 }))
})
const resumeRadarValue = computed(() => {
  const dims = resumeResult.value?.dimensions || []
  return dims.map((d) => d.score)
})
const renderResumeRadar = () => {
   if (!resumeRadarRef.value || !resumeResult.value?.dimensions?.length) return
   if (!resumeRadarChart) resumeRadarChart = echarts.init(resumeRadarRef.value)
   const option = {
     tooltip: { trigger: 'item' },
     radar: {
       indicator: resumeRadarIndicator.value,
       radius: '70%', center: ['50%', '54%'], splitNumber: 4,
       axisName: { color: 'rgba(31,47,61,0.85)', fontSize: 12 },
       splitLine: { lineStyle: { color: 'rgba(64,158,255,0.12)' } },
       splitArea: { areaStyle: { color: ['rgba(64,158,255,0.03)', 'rgba(64,158,255,0.01)'] } },
       axisLine: { lineStyle: { color: 'rgba(64,158,255,0.18)' } }
     },
     series: [{
       type: 'radar',
       data: [{
         value: resumeRadarValue.value, name: '诊断维度',
         areaStyle: { color: 'rgba(64,158,255,0.18)' },
         lineStyle: { width: 2, color: 'rgba(64,158,255,0.95)' },
         itemStyle: { color: '#409EFF' }
       }]
     }]
   }
   resumeRadarChart.setOption(option, { notMerge: true })
}
const initResumeRadar = () => { nextTick(() => renderResumeRadar()) }
watch(() => resumeResult.value, async () => { await nextTick(); initResumeRadar() })

const analyzeResume = async () => {
  if (!resumeText.value) return ElMessage.warning('请输入简历内容')
  resumeAnalyzing.value = true
  resumeProgress.value = 0
  if (resumeProgressTimer) clearInterval(resumeProgressTimer)
  
  const startedAt = Date.now()
  resumeProgressTimer = setInterval(() => {
    const elapsed = Date.now() - startedAt
    const t = Math.min(1, elapsed / 2000)
    resumeProgress.value = Math.min(95, Math.round(t * 95))
  }, 40)

  try {
    const [res] = await Promise.all([
      axios.post(`${API_BASE}/api/analyze_resume`, { content: resumeText.value }),
      sleep(2000)
    ])
    resumeResult.value = res.data
    resumeProgress.value = 100
    ElMessage.success('诊断完成')
  } catch (e) {
    ElMessage.error('失败')
  } finally {
    if (resumeProgressTimer) clearInterval(resumeProgressTimer)
    resumeProgressTimer = null
    resumeAnalyzing.value = false
  }
}

// --- 生涯规划 ---
const generateRoadmap = async () => {
  if (!roadmapGrade.value || !roadmapRole.value) return ElMessage.warning('请选择年级和方向')
  roadmapLoading.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/generate_roadmap`, {
      current_grade: roadmapGrade.value,
      target_role: roadmapRole.value
    })
    roadmapData.value = res.data.roadmap
    roadmapRadar.value = res.data.radar_chart
    roadmapComment.value = res.data.ai_comment
    ElMessage.success('生成成功')
    setTimeout(() => { initRadarChart() }, 100)
  } catch (e) { ElMessage.error('生成失败') } 
  finally { roadmapLoading.value = false }
}

const initRadarChart = () => {
  if (!radarChartRef.value || !roadmapRadar.value) return
  const myChart = echarts.init(radarChartRef.value)
  const option = {
    radar: {
      indicator: roadmapRadar.value.indicators,
      shape: 'circle', splitNumber: 4, axisName: { color: '#666' },
      splitArea: {
        areaStyle: { color: ['rgba(64,158,255, 0.1)', 'rgba(64,158,255, 0.2)', 'rgba(64,158,255, 0.3)', 'rgba(64,158,255, 0.4)'] }
      }
    },
    series: [{
      type: 'radar', name: '能力模型',
      data: [{ value: roadmapRadar.value.values, name: '当前能力', itemStyle: { color: '#409EFF' }, areaStyle: { opacity: 0.3 } }]
    }]
  }
  myChart.setOption(option)
}

// --- 竞争力沙盘 ---
const sandboxIndicator = [
   { name: '学业成绩 (GPA)', max: 100 }, { name: '项目实战', max: 100 },
   { name: '实习经验', max: 100 }, { name: '竞赛获奖', max: 100 },
   { name: '英语能力', max: 100 }, { name: '领导协作', max: 100 }
]
const sandboxSeriesValue = () => [
  radarValues.gpa, radarValues.project, radarValues.intern, 
  radarValues.competition, radarValues.english, radarValues.leader
]
const renderSandboxChart = (isInit = false) => {
  if (!sandboxChart) return
  const option = {
    backgroundColor: 'transparent', tooltip: { trigger: 'item' },
    radar: {
      indicator: sandboxIndicator, radius: '68%', center: ['50%', '56%'], splitNumber: 5,
      axisName: { color: 'rgba(31,47,61,0.85)', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(64,158,255,0.12)' } },
      splitArea: { areaStyle: { color: ['rgba(64,158,255,0.03)', 'rgba(64,158,255,0.01)'] } },
      axisLine: { lineStyle: { color: 'rgba(64,158,255,0.18)' } }
    },
    animation: true, animationDuration: isInit ? 350 : 0, animationDurationUpdate: 320, animationEasingUpdate: 'cubicOut',
    series: [{
      type: 'radar', name: '核心竞争力', symbol: 'circle', symbolSize: 6,
      data: [{
        value: sandboxSeriesValue(), name: '当前状态',
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(64,158,255, 0.65)' }, { offset: 1, color: 'rgba(64,158,255, 0.12)' }]) },
        itemStyle: { color: '#409EFF', borderColor: '#fff', borderWidth: 1 },
        lineStyle: { width: 3, color: 'rgba(64,158,255,0.95)' }
      }]
    }]
  }
  sandboxChart.setOption(option, { notMerge: true, lazyUpdate: true })
}
const initSandboxChart = () => {
  if (!sandboxChartRef.value) return
  if (sandboxChart) return
  sandboxChart = echarts.init(sandboxChartRef.value)
  renderSandboxChart(true)
}
const scheduleSandboxUpdate = () => {
  if (sandboxPending) return
  sandboxPending = true
  sandboxRafId = requestAnimationFrame(() => {
    sandboxPending = false
    renderSandboxChart(false)
  })
}
watch(radarValues, () => { scheduleSandboxUpdate() })

// ==========================================
// 6. 生命周期 & 辅助 (Lifecycle)
// ==========================================
const handleSelect = (key) => {
  activeMenu.value = key
  if (key === '3') nextTick(() => initSandboxChart())
  if (key === '1') nextTick(() => initResumeRadar())
  if (key === '7') router.push('/virtual-experiment')
}
const handleLoginSuccess = (userData) => {
  currentUser.value = userData
  ElMessage.success(`欢迎回来，${userData.username}！`)
}
const handleLogout = () => {
  currentUser.value = null
  ElMessage.info('已退出登录')
}

onMounted(() => {
  const onResize = () => {
    sandboxChart && sandboxChart.resize()
    resumeRadarChart && resumeRadarChart.resize()
  }
  window.addEventListener('resize', onResize)
  if (activeMenu.value === '3') nextTick(() => initSandboxChart())
  fetchJobsData()
})

// ==========================================
// 7. 生涯规划扩展：性格测试 & AI 整合报告
// ==========================================
const openPersonalityTest = () => {
  window.open('https://www.16personalities.com/ch/%E4%BA%BA%E6%A0%BC%E6%B5%8B%E8%AF%95', '_blank')
}

const downloadPersonalityResult = async () => {
  try {
    const target = roadmapCaptureRef.value || document.body
    const canvas = await html2canvas(target, { useCORS: true, backgroundColor: '#ffffff' })
    const dataUrl = canvas.toDataURL('image/png')

    const payload = {
      type: 'personality_test_result',
      source: '16personalities',
      captured_at: new Date().toISOString(),
      note: personalityNote.value || '',
      screenshot_png_base64: dataUrl
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `性格测试结果_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('已导出 JSON')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败：请确认页面可被截图（同源内容）')
  }
}

const careerPlanHtml = computed(() => (careerPlanMarkdown.value ? md.render(careerPlanMarkdown.value) : ''))

const readFileAsText = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = reject
    reader.readAsText(file)
  })

const onCareerFilesChange = (_file, fileList) => {
  careerFiles.value = fileList || []
}

const generateCareerPlan = async () => {
  // 禁用用户检查
  try {
    const banned = JSON.parse(localStorage.getItem('competition_banned_user_ids') || '[]')
    const username = localStorage.getItem('remembered_username') || ''
    const users = JSON.parse(localStorage.getItem('competition_user_list') || '[]')
    const me = users.find(u => u.username === username)
    if (me && banned.includes(me.id)) {
      return ElMessage.error('您的账号已被管理员禁用，无法使用该功能')
    }
  } catch (e) {}

  const raws = (careerFiles.value || []).map(f => f.raw).filter(Boolean)
  const jsonFile = raws.find(f => (f.name || '').toLowerCase().endsWith('.json'))
  const mdFile = raws.find(f => (f.name || '').toLowerCase().endsWith('.md'))

  if (!jsonFile || !mdFile) {
    return ElMessage.warning('请同时上传：性格测试 JSON + 虚拟实验 Markdown（.md）')
  }

  careerGenerating.value = true
  careerPlanMarkdown.value = ''
  try {
    const jsonText = await readFileAsText(jsonFile)
    const mdText = await readFileAsText(mdFile)
    const personalityJson = JSON.parse(jsonText)

    const defaultCareerPlanPrompt = `你是一个资深的大学生职业规划导师。请根据学生的年级和专业，为他规划一条清晰的学习路线图。\n请列出具体的学习阶段、推荐书籍和关键项目。`
    const careerPrompt = localStorage.getItem('admin_ai_career_plan') || defaultCareerPlanPrompt

    const res = await axios.post(`${API_BASE}/api/generate-career`, {
      personality_json: personalityJson,
      experiment_markdown: mdText,
      note: personalityNote.value || '',
      system_prompt: careerPrompt
    })

    careerPlanMarkdown.value = res?.data?.markdown || ''
    ElMessage.success('生涯规划报告已生成')
  } catch (e) {
    console.error(e)
    ElMessage.error('生成失败：请检查文件格式或后端服务')
  } finally {
    careerGenerating.value = false
  }
}

const downloadCareerPlan = () => {
  if (!careerPlanMarkdown.value) return ElMessage.warning('暂无规划报告可下载')
  const blob = new Blob([careerPlanMarkdown.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AI生涯规划报告_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.md`
  a.click()
  URL.revokeObjectURL(url)
}

onBeforeUnmount(() => {
  if (resumeProgressTimer) clearInterval(resumeProgressTimer)
  resumeProgressTimer = null
  if (sandboxRafId) cancelAnimationFrame(sandboxRafId)
  sandboxRafId = 0
  if (sandboxChart) sandboxChart.dispose()
  sandboxChart = null
  if (resumeRadarChart) resumeRadarChart.dispose()
  resumeRadarChart = null
  if (recognitionInstance) recognitionInstance.stop() // 停止录音
})
</script>
  
<template>
  <!-- 未登录状态：显示首页、登录页等 -->
  <div v-if="!currentUser" class="guest-container">
    <router-view @login-success="handleLoginSuccess" />
    
    <Login 
      v-if="$route.path !== '/' && $route.path !== '/login'" 
      @login-success="handleLoginSuccess" 
    />
  </div>

  <!-- 已登录状态：如果是过渡页(/explore)，显示过渡页 -->
  <div v-else-if="$route.path === '/explore'" class="guest-container">
    <router-view />
  </div>

  <!-- 已登录状态：显示主应用界面（功能页） -->
  <!-- 当路由为 /app 或其他功能相关路由时，显示主应用界面 -->
  <el-container v-else class="app-shell">

    <el-aside width="260px" class="app-aside">
        <div class="brand">
          <div class="brand-icon">
            <el-icon :size="22"><Monitor /></el-icon>
          </div>
          <div class="brand-text">
            <div class="brand-title">职航——AI辅助的大学生生涯成长平台</div>
            <button class="explore-btn" @click="goExplore">探索</button>
            <div class="brand-subtitle">挑战杯 · 演示版 Demo</div>
          </div>
        </div>
  
        <el-menu
  class="side-menu"
  :default-active="activeMenu"
  background-color="transparent"
  text-color="rgba(255,255,255,0.72)"
  active-text-color="#ffffff"
  @select="handleSelect"
>
  <el-menu-item index="0">
    <el-icon><Calendar /></el-icon>
    <span>生涯路径规划</span>
  </el-menu-item>

  <el-menu-item index="1">
  <el-icon><DocumentChecked /></el-icon>
  <span>AI 简历医生</span>
</el-menu-item>

<el-menu-item index="6" @click="activeMenu = '6'">
  <el-icon><Collection /></el-icon>
  <span>简历模板库</span>
</el-menu-item>

  <el-menu-item index="2">
    <el-icon><ChatDotRound /></el-icon>
    <span>模拟面试</span>
  </el-menu-item>

  <el-menu-item index="3">
    <el-icon><Odometer /></el-icon>
    <span>竞争力沙盘</span>
  </el-menu-item>

  <el-menu-item index="7">
    <el-icon><VideoPlay /></el-icon>
    <span>虚拟职业体验</span>
  </el-menu-item>

  <el-menu-item index="5" @click="activeMenu = '5'">
  <el-icon><Clock /></el-icon>
  <span>历史记录</span>
</el-menu-item>

  <el-menu-item index="4">
  <el-icon><User /></el-icon>
  <span>个人中心</span>
</el-menu-item>

</el-menu>
  

      <div class="aside-footer">
        <div class="user-chip">
          <el-avatar :size="34" style="background: #409EFF">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-meta">
            <div class="user-name">{{ currentUser?.username || '用户名' }}</div>
            <div class="user-desc">{{ currentUser?.grade || '年级' }} / {{ currentUser?.target_role || '岗位' }}</div>
          </div>
        </div>
        <!-- 退出登录按钮 -->
        <el-button
          type="text"
          size="small"
          @click="handleLogout"
          class="logout-button"
          style="color: rgba(255,255,255,0.7); margin-top: 8px; width: 100%;"
        >
          <el-icon style="margin-right: 4px"><User /></el-icon>
          退出登录
        </el-button>
      </div>
      </el-aside>
  
      <el-container class="app-main">
        <el-header class="topbar">
          <div class="topbar-left">
            <div class="topbar-title">
  {{
    activeMenu === '0' ? '生涯路径规划' :
    activeMenu === '1' ? 'AI 简历医生' :
    activeMenu === '2' ? '模拟面试' :
    activeMenu === '3' ? '竞争力沙盘' :
    activeMenu === '7' ? '虚拟职业体验' :
    '个人中心'
  }}
</div>
            </div>
            <div class="topbar-tag">科技蓝 · 商业级演示</div>
          <div class="topbar-right">
            <el-button type="primary" plain>
              <el-icon style="margin-right: 6px"><MagicStick /></el-icon>
              一键演示
            </el-button>
            <el-button @click="speakText('测试声音，如果你听到这句话，说明语音功能是正常的')">
  🔊 测试声音
</el-button>
          </div>
        </el-header>
  
        <el-main class="page">
          <!-- 功能 0：生涯路径规划 -->
          <div v-if="activeMenu === '0'" class="animate-fade">
  <div class="page-header">
    <h2>🚀 AI 生涯智航</h2>
    <p>构建您的核心竞争力模型，规划最优职业路径</p>
  </div>

  <div class="glass-card control-bar-pro" ref="roadmapCaptureRef">
  <div class="control-left">
    <div class="control-title">
      <el-icon class="icon-pulse"><Compass /></el-icon>
      <span>规划导航</span>
    </div>
    <div class="control-subtitle">定制你的专属成长路线图</div>
  </div>

  <div class="control-right">
    <el-button type="primary" plain size="large" @click="openPersonalityTest">
      性格测试
    </el-button>
    <el-button type="success" plain size="large" @click="downloadPersonalityResult">
      下载测试结果
    </el-button>

    <el-select 
      v-model="roadmapGrade" 
      placeholder="当前年级" 
      size="large" 
      class="select-item"
      effect="light"
    >
      <template #prefix><el-icon><User /></el-icon></template>
      <el-option v-for="g in gradeOptions" :key="g" :label="g" :value="g"/>
    </el-select>

    <el-select 
      v-model="roadmapRole" 
      placeholder="目标方向" 
      size="large" 
      class="select-item"
      effect="light"
      filterable
    >
      <template #prefix><el-icon><Aim /></el-icon></template>
      <el-option-group
        v-for="group in roleOptions"
        :key="group.label"
        :label="group.label"
      >
        <el-option
          v-for="item in group.options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-option-group>
    </el-select>

    <!-- 新增：职业测评按钮 -->
    <el-button 
      type="success" 
      size="large" 
      class="assessment-btn"
      @click="jumpToAssessment"
      round
    >
      职业测评 <el-icon class="el-icon--right"><UserFilled /></el-icon>
    </el-button>

    <el-button 
      type="primary" 
      size="large" 
      class="generate-btn"
      @click="generateRoadmap" 
      :loading="roadmapLoading"
      round
    >
      AI 智能生成 <el-icon class="el-icon--right"><MagicStick /></el-icon>
    </el-button>
  </div>
</div>

  <div class="glass-card" style="margin-top: 14px;">
    <div class="card-title">🧩 AI 生涯分析整合</div>
    <div style="display:flex; gap: 12px; align-items:center; flex-wrap: wrap;">
      <el-input
        v-model="personalityNote"
        placeholder="可选：补充一段性格测试结果摘要/自我描述（会被一并用于生成规划）"
        style="min-width: 360px; flex: 1;"
      />

      <el-upload
        action="#"
        :auto-upload="false"
        :multiple="true"
        :on-change="onCareerFilesChange"
        :show-file-list="true"
        accept=".json,.md"
      >
        <el-button type="primary" plain>导入分析文件</el-button>
      </el-upload>

      <el-button type="primary" :loading="careerGenerating" @click="generateCareerPlan">
        {{ careerGenerating ? '生成中...' : '生成生涯规划报告' }}
      </el-button>
      <el-button type="success" plain :disabled="!careerPlanMarkdown" @click="downloadCareerPlan">
        下载规划报告
      </el-button>
    </div>

    <el-divider />
    <div v-if="careerPlanMarkdown" class="markdown-body" v-html="careerPlanHtml"></div>
    <div v-else style="color:#909399;">提示：请上传「性格测试 JSON」与「虚拟实验 .md」后生成报告。</div>
  </div>

  <div v-if="roadmapData.length > 0">
    <el-row :gutter="24">
      <el-col :span="9">
        <div class="glass-card dashboard-card">
          <div class="card-title">📊 竞争力模型分析</div>
          <div class="radar-chart-box" ref="radarChartRef"></div>
          
          <div class="ai-insight">
            <div class="insight-title"><el-icon><Trophy /></el-icon> AI 导师洞察</div>
            <p>{{ roadmapComment }}</p>
          </div>
        </div>
      </el-col>

      <el-col :span="15">
        <div class="glass-card roadmap-timeline-card">
          <div class="card-title">📅 关键里程碑规划</div>
          <el-timeline>
            <el-timeline-item
              v-for="(item, i) in roadmapData"
              :key="i"
              :color="item.color"
              :icon="item.icon === 'Loading' ? Loading : (item.icon === 'CircleCheck' ? CircleCheck : '')"
              size="large"
            >
              <div class="timeline-box" :class="{'active-node': item.status === 'process'}">
                <div class="node-header">
                  <span class="time-tag">{{ item.time || item.timestamp }}</span>
                  <span class="node-title">{{ item.title }}</span>
                  <el-tag v-if="item.status === 'done'" type="success" size="small" effect="dark">已完成</el-tag>
                  <el-tag v-else-if="item.status === 'process'" type="primary" size="small" effect="dark">进行中</el-tag>
                  <el-tag v-else type="info" size="small" effect="dark">待开始</el-tag>
                </div>
                
                <p class="node-content">{{ item.content }}</p>
                
                <!-- 推荐资源 -->
                <div class="node-resources" v-if="item.resources && item.resources.length">
                  <div class="res-label">📚 推荐资源：</div>
                  <div class="res-chips">
                    <span v-for="(r, idx) in item.resources" :key="idx" class="res-chip">
                      {{ r }}
                    </span>
                  </div>
                </div>
                
                <!-- 荣誉/证书 -->
                <div class="node-certificates" v-if="item.certificates && item.certificates.length">
                  <div class="cert-label">🏆 目标证书/荣誉：</div>
                  <div class="cert-chips">
                    <span v-for="(c, idx) in item.certificates" :key="idx" class="cert-chip">
                      {{ c }}
                    </span>
                  </div>
                </div>
                
                <!-- 推荐企业（仅大四阶段显示） -->
                <div class="node-companies" v-if="item.recommended_companies && item.recommended_companies.length">
                  <div class="company-label">💼 适配入职企业：</div>
                  <div class="company-chips">
                    <span v-for="(company, idx) in item.recommended_companies" :key="idx" class="company-chip">
                      {{ company }}
                    </span>
                  </div>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>
  </div>

  <div v-else-if="!roadmapLoading" class="empty-state-box">
    <div class="empty-emoji">🧭</div>
    <h3>配置您的生涯导航</h3>
    <p>请在上方选择年级与方向，AI 将为您生成专属能力雷达与成长路径。</p>
  </div>
</div>

          <!-- 功能 1：AI 简历医生 -->
<div v-if="activeMenu === '1'" class="animate-fade">
  <ResumeDoctor />
</div>

          <!-- 功能 7：虚拟实验体验 -->
          <div v-if="activeMenu === '7'" class="animate-fade">
            <VirtualExperiment />
          </div>
          <!-- 功能 2：模拟面试 -->
          <div v-if="activeMenu === '2'" class="animate-fade">
            <div class="page-header">
              <h2>模拟面试官 · ChatGPT 风格对话</h2>
              <p>用户右侧气泡，AI 左侧气泡（含头像），支持 Enter 快速发送</p>
            </div>

            <!-- 数字人展示区 -->
            <div class="digital-human-section">
              <DigitalHuman :isTalking="interviewerState === 'talking'" />
            </div>

            <div class="chat-shell">
              <div class="chat-window chat-window-el">
                <div v-for="(msg, i) in chatHistory" :key="i" class="msg-row" :class="msg.role">
                  <div class="avatar" v-if="msg.role === 'ai'">
                    <el-avatar :size="36" class="avatar-ai">AI</el-avatar>
                  </div>
                  <div class="bubble">
  <div class="bubble-name">{{ msg.role === 'ai' ? 'AI 面试官' : '我' }}</div>
  <div class="bubble-text">{{ msg.content }}</div>

  <div v-if="msg.jobs && msg.jobs.length > 0" class="job-card-list">
    <div v-for="(job, jIndex) in msg.jobs" :key="jIndex" class="job-card-item">
  
  <div class="job-info">
    <div class="job-name">{{ job['岗位'] }}</div>
    <div class="job-salary">💰 {{ job['平均薪资'] }}</div>
    
    <div v-if="job._applied" class="apply-success-text">
      <el-icon><CircleCheck /></el-icon> 简历已送达 HR 邮箱
    </div>
  </div>

  <el-button 
    :type="job._applied ? 'success' : 'primary'" 
    size="small" 
    :loading="job._loading" 
    :disabled="job._applied"
    @click="handleApply(job)"
  >
    {{ job._applied ? '✅ 投递成功' : '⚡ 一键投递' }}
  </el-button>
  
</div>
  </div>
  </div>
                  <div class="avatar" v-if="msg.role === 'user'">
                    <el-avatar :size="36" class="avatar-user">
                      <el-icon><User /></el-icon>
                    </el-avatar>
                  </div>
                </div>
              </div>
  
              <div class="input-area">
                <div class="input-row">
  <el-input
    v-model="chatInput"
    placeholder="输入你的回答…（Enter 发送）"
    @keyup.enter="sendMessage"
    size="large"
    class="full-width-input"
  >
    <template #prepend>
      <el-button 
        @click="toggleVoiceInput"
        :class="{ 'recording-active': isRecording }"
        :title="isRecording ? '点击停止' : '点击说话'"
      >
        <el-icon :class="{ 'mic-pulse': isRecording }" :size="20">
          <Microphone />
        </el-icon>
      </el-button>
    </template>
    
    <div class="input-row">
  <el-input
    v-model="chatInput"
    placeholder="输入你的回答…（Enter 发送）"
    @keyup.enter="sendMessage"
    size="large"
    class="full-width-input" 
  >
    <template #prepend>
      <el-button 
        @click="toggleVoiceInput"
        :class="{ 'recording-active': isRecording }"
        :title="isRecording ? '点击停止' : '点击说话'"
      >
        <el-icon :class="{ 'mic-pulse': isRecording }" :size="20">
          <Microphone />
        </el-icon>
      </el-button>
    </template>
    
    <template #append>
      <el-button 
        :type="chatInput.trim().length > 0 ? 'success' : 'primary'" 
        :loading="chatSending" 
        @click="sendMessage"
        class="rocket-btn"
      >
        {{ chatInput.trim().length > 0 ? '发送 🚀' : '发送' }}
      </el-button>
    </template>
  </el-input>
</div>
  </el-input>
</div>

    

<div class="agent-action">
  <el-button type="success" :loading="agentCalling" @click="callAgent" class="agent-button">
    ⚡ 召唤 Agent 智能推荐
  </el-button>
</div>
              </div>
            </div>
          </div>
  
          <!-- 功能 3：竞争力沙盘 -->
          <div v-if="activeMenu === '3'" class="animate-fade">
            <div class="page-header">
              <h2>个人核心竞争力沙盘推演</h2>
              <p>左侧 6 个滑块实时驱动右侧雷达图平滑变形（无卡顿）</p>
              <div class="ai-suggestion">
                💡 基于您的目标岗位，AI 建议您重点提升【实习经验】和【项目实战】维度
              </div>
            </div>
  
            <el-row :gutter="18">
              <el-col :span="8">
                <div class="glass-card control-panel">
                  <div class="card-title">参数调节</div>
                  <div class="slider-item">
                    <span>学业成绩 (GPA)</span>
                    <el-slider v-model="radarValues.gpa" :min="0" :max="100" show-input />
                  </div>
                  <div class="slider-item">
                    <span>项目实战经验</span>
                    <el-slider v-model="radarValues.project" :min="0" :max="100" show-input />
                  </div>
                  <div class="slider-item">
                    <span>名企实习经历</span>
                    <el-slider v-model="radarValues.intern" :min="0" :max="100" show-input />
                  </div>
                  <div class="slider-item">
                    <span>竞赛获奖情况</span>
                    <el-slider v-model="radarValues.competition" :min="0" :max="100" show-input />
                  </div>
                  <div class="slider-item">
                    <span>英语/学术能力</span>
                    <el-slider v-model="radarValues.english" :min="0" :max="100" show-input />
                  </div>
                  <div class="slider-item">
                    <span>领导力与协作</span>
                    <el-slider v-model="radarValues.leader" :min="0" :max="100" show-input />
                  </div>
                </div>
              </el-col>
  
              <el-col :span="16">
                <div class="glass-card chart-wrap">
                  <div class="chart-title">ECharts · Radar (Smooth Update)</div>
                  <div class="chart-container" ref="sandboxChartRef"></div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 功能 4：个人中心 -->
          <div v-if="activeMenu === '4'" class="animate-fade">
            <UserProfile />
          </div>
          <!-- 功能 5：历史记录 -->
          <div v-if="activeMenu === '5'" class="animate-fade">
  <HistoryRecord />
</div>
          <!-- 功能 6：简历模板库 --> 
<div v-if="activeMenu === '6'" style="height: 100%">
  <ResumeTemplates />
</div>
          <!-- 功能 7：虚拟职业体验 --> 
<div v-if="activeMenu === '7'" class="content-wrapper">
  <CareerExperience />
</div>
          </el-main>
      </el-container>
    </el-container>
  </template>
  
  <style scoped>
  :deep(.el-button--primary) { --el-color-primary: #409EFF; }
  
  .app-shell {
    height: 100vh;
    background: linear-gradient(180deg, #f6f9ff 0%, #f2f5fb 100%);
    font-family: 'PingFang SC', 'Helvetica Neue', sans-serif;
  }
  
  /* UI 统一样式说明（中文注释）
     - 统一内容区 padding、卡片圆角与阴影风格，保持 Element Plus 风格的视觉一致性
     - 侧边栏图标居中对齐，菜单项高度统一
  */
  :deep(.side-menu .el-menu-item .el-icon) { display:flex; align-items:center; justify-content:center; width:28px; }
  .page { padding: 20px; }
  .glass-card { border-radius: 12px; }
  
  .app-aside {
    position: relative;
    color: #fff;
    background:
      radial-gradient(1200px 600px at 10% 10%, rgba(64,158,255,0.22), transparent 60%),
      radial-gradient(900px 500px at 90% 20%, rgba(0,255,255,0.10), transparent 55%),
      linear-gradient(180deg, #081427 0%, #050b16 100%);
    box-shadow: 8px 0 24px rgba(2, 6, 23, 0.35);
    display: flex;
    flex-direction: column;
    padding: 18px 14px;
  }
  
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 10px 16px 10px;
  }
  
  .brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(64,158,255,0.95), rgba(64,158,255,0.22));
    box-shadow: 0 10px 24px rgba(64,158,255,0.28);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .brand-title { font-weight: 700; letter-spacing: 0.5px; font-size: 14px; }
.explore-btn { margin-left:12px; background: linear-gradient(90deg,#4A89DC 0%, #967ADC 100%); color: #fff; border: none; padding:6px 12px; border-radius:8px; cursor:pointer }
  .brand-subtitle { margin-top: 2px; font-size: 12px; color: rgba(255,255,255,0.56); }
  
  .side-menu { border-right: none; margin-top: 6px; background: transparent; }
  
  :deep(.side-menu .el-menu-item) {
    height: 48px;
    border-radius: 12px;
    margin: 6px 8px;
  }
  
  :deep(.side-menu .el-menu-item.is-active) {
    background: linear-gradient(135deg, rgba(64,158,255,0.92), rgba(64,158,255,0.18));
    color: #fff !important;
    box-shadow: 0 10px 24px rgba(64,158,255,0.22);
  }
  
  :deep(.side-menu .el-menu-item:hover) { background: rgba(64,158,255,0.16); }
  
  .aside-footer { margin-top: auto; padding: 10px 8px 6px; }
  .user-chip {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px;
    border-radius: 14px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
  }
  .user-name { font-size: 13px; color: rgba(255,255,255,0.92); }
  .user-desc { margin-top: 2px; font-size: 12px; color: rgba(255,255,255,0.60); }
  
  .app-main { min-width: 0; }
  .topbar {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    background: rgba(255,255,255,0.76);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(15,23,42,0.06);
  }
  .topbar-title { font-size: 16px; font-weight: 700; color: #0f172a; }
  .topbar-tag { margin-top: 2px; font-size: 12px; color: rgba(15,23,42,0.60); }
  .topbar-left { display: flex; flex-direction: column; }
  
  .page { padding: 18px; overflow: auto; }
  .page-header { margin: 10px 4px 14px; }
  .page-header h2 { margin: 0 0 8px; color: #0f172a; font-size: 26px; letter-spacing: 0.2px; }
  .page-header p { margin: 0; color: rgba(15,23,42,0.62); }
  
  .ai-suggestion {
    margin-top: 12px;
    padding: 12px 14px;
    background: linear-gradient(135deg, rgba(255,193,7,0.15), rgba(255,152,0,0.10));
    border: 1px solid rgba(255,193,7,0.25);
    border-radius: 8px;
    color: rgba(15,23,42,0.78);
    font-size: 13px;
    line-height: 1.6;
  }
  
  .glass-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(15,23,42,0.06);
    border-radius: 16px;
    box-shadow: 0 18px 50px rgba(15,23,42,0.08);
    padding: 16px;
  }
  .card-title { font-weight: 700; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
  .card-actions { margin-top: 12px; display: flex; justify-content: flex-end; }
  .progress-wrap { margin-top: 14px; }
  .progress-title { font-size: 12px; color: rgba(15,23,42,0.60); margin-bottom: 8px; }
  
  .report-card .empty-hint {
    color: rgba(15,23,42,0.55);
    background: rgba(64,158,255,0.06);
    border: 1px dashed rgba(64,158,255,0.25);
    border-radius: 14px;
    padding: 14px;
    line-height: 1.7;
  }
  
  .score-row { display: flex; gap: 14px; margin-bottom: 10px; }
  .score-left {
    width: 92px;
    height: 92px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(64,158,255,0.95), rgba(64,158,255,0.16));
    color: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 16px 36px rgba(64,158,255,0.26);
  }
  .score-number { font-size: 34px; font-weight: 800; line-height: 1; }
  .score-label { margin-top: 6px; font-size: 12px; opacity: 0.9; }
  .score-level { font-weight: 700; color: #0f172a; }
  .score-summary { margin-top: 6px; font-size: 12px; color: rgba(15,23,42,0.62); line-height: 1.6; }
  
  .mini-chart { height: 220px; margin: 8px 0 4px; }
  .pill-list { display: flex; flex-wrap: wrap; gap: 8px; }
  .suggestions { margin-top: 6px; }
  
  .control-panel { height: 520px; overflow: auto; }
  .slider-item { margin-bottom: 16px; }
  .slider-item span { display: block; margin-bottom: 8px; font-size: 13px; color: rgba(15,23,42,0.72); font-weight: 700; }
  .chart-wrap { padding: 16px; }
  .chart-title { font-size: 12px; color: rgba(15,23,42,0.55); margin-bottom: 8px; }
  .chart-container { height: 520px; }
  
  .digital-human-section {
    height: 200px;
    border-radius: 16px;
    background: rgba(0,0,0,0.85);
    border: 1px solid rgba(15,23,42,0.10);
    margin-bottom: 12px;
    box-shadow: 0 18px 50px rgba(15,23,42,0.08);
    overflow: hidden;
  }
  
  .chat-shell {
    height: calc(100vh - 420px);
    display: flex;
    flex-direction: column;
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(15,23,42,0.06);
    border-radius: 16px;
    box-shadow: 0 18px 50px rgba(15,23,42,0.08);
    overflow: hidden;
  }
  .chat-window-el {
    flex: 1;
    overflow-y: auto;
    padding: 18px 16px;
    background:
      radial-gradient(900px 400px at 20% 0%, rgba(64,158,255,0.10), transparent 60%),
      linear-gradient(180deg, #f7faff 0%, #f3f6fc 100%);
  }
  .input-area { 
    padding: 14px; 
    background: rgba(255,255,255,0.92); 
    border-top: 1px solid rgba(15,23,42,0.06); 
  }
  .input-row {
    margin-bottom: 10px;
  }
  .agent-action {
    display: flex;
    justify-content: center;
  }
  .agent-button {
    width: 100%;
    max-width: 400px;
    height: 40px;
    font-weight: 600;
    font-size: 14px;
    background: linear-gradient(135deg, #67C23A, #85CE61);
    border: 1px solid #85CE61;
  }
  .agent-button:hover {
    background: linear-gradient(135deg, #85CE61, #67C23A);
    filter: brightness(1.1);
  }
  .msg-row { display: flex; gap: 10px; margin: 14px 0; align-items: flex-end; }
  .msg-row.user { justify-content: flex-end; }
  .bubble {
    max-width: 72%;
    padding: 12px 14px;
    border-radius: 14px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.08);
    border: 1px solid rgba(15,23,42,0.06);
  }
  .msg-row.ai .bubble { background: rgba(255,255,255,0.95); border-top-left-radius: 8px; }
  .msg-row.user .bubble {
    background: linear-gradient(135deg, rgba(64,158,255,0.98), rgba(64,158,255,0.62));
    color: #fff;
    border: 1px solid rgba(64,158,255,0.30);
    border-top-right-radius: 8px;
  }
  .bubble-name { font-size: 12px; opacity: 0.85; margin-bottom: 6px; }
  .bubble-text { line-height: 1.65; font-size: 14px; white-space: pre-wrap; }
  .avatar-ai { background: rgba(64,158,255,0.16); color: #409EFF; border: 1px solid rgba(64,158,255,0.20); }
  .avatar-user { background: rgba(15,23,42,0.88); color: #fff; border: 1px solid rgba(15,23,42,0.15); }
  
  .roadmap-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-card {
    padding: 18px;
  }
  
  .filter-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  
  .filter-item {
    display: flex;
    flex-direction: column;
  }
  
  .filter-item label {
    font-size: 13px;
    font-weight: 700;
    color: rgba(15,23,42,0.72);
    margin-bottom: 8px;
  }
  
  .filter-actions {
    display: flex;
    justify-content: flex-start;
    gap: 12px;
  }
  
  .timeline-card {
    padding: 20px;
  }
  
  :deep(.timeline-card .el-timeline-item__wrapper) {
    padding: 0;
  }
  
  :deep(.timeline-card .el-timeline-item__content) {
    padding: 0;
  }
  
  .timeline-content {
    padding: 14px 16px;
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    border: 1px solid rgba(64,158,255,0.10);
    box-shadow: 0 4px 12px rgba(15,23,42,0.06);
    transition: all 0.3s ease;
  }
  
  .timeline-content.active-stage {
    background: linear-gradient(135deg, rgba(64,158,255,0.08), rgba(64,158,255,0.04));
    border: 1px solid rgba(64,158,255,0.25);
    box-shadow: 0 8px 20px rgba(64,158,255,0.15);
    transform: scale(1.02);
  }
  
  .timeline-title {
    font-weight: 700;
    color: #0f172a;
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .timeline-text {
    font-size: 13px;
    color: rgba(15,23,42,0.68);
    line-height: 1.65;
  }
  
  .empty-roadmap {
    padding: 40px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  .empty-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
  }
  
  .empty-desc {
    font-size: 13px;
    color: rgba(15,23,42,0.62);
  }
  
  .animate-fade { animation: fadeIn 0.5s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }</style>
  /* --- 岗位投递卡片样式 --- */
.job-card-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.job-card-item {
  background: #f0f9eb; /* 浅绿色背景 */
  border: 1px solid #e1f3d8;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between; /* 左右对齐 */
  align-items: center;
}

.job-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.job-name {
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.job-salary {
  font-size: 12px;
  color: #f56c6c; /* 红色高亮薪资 */
  font-weight: bold;
}
/* --- 新增：投递成功提示字样式 --- */
.apply-success-text {
  font-size: 12px;
  color: #67C23A; /* Element Plus 的成功绿色 */
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  animation: fadeIn 0.5s ease;
}

/* 让图标稍微对齐一下 */
.apply-success-text .el-icon {
  font-size: 14px;
}
/* --- 生涯规划 Pro 样式 --- */
.control-area {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}
.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.score-panel {
  border-top: 1px solid #eee;
  padding-top: 15px;
  animation: fadeIn 0.6s ease;
}
.score-info {
  margin-bottom: 10px;
}
.score-info .label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  font-weight: bold;
}
.skill-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.tag-label { font-size: 12px; color: #999; }

.timeline-area {
  padding: 10px 5px;
}
.timeline-card {
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.timeline-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-header h4 { margin: 0; font-size: 16px; color: #303133; }
.tags-row { display: flex; gap: 6px; }
.content-text { color: #606266; line-height: 1.6; font-size: 14px; margin-bottom: 12px; }

.resources-box {
  background: #fdf6ec; /* 浅橙色背景 */
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #e6a23c;
}
.res-label {
  font-size: 12px;
  color: #d48806;
  font-weight: bold;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.res-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.res-link {
  font-size: 12px;
  color: #606266;
  background: rgba(255,255,255,0.6);
  padding: 2px 8px;
  border-radius: 4px;
}/* --- 智能版生涯规划 CSS --- */
.control-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  margin-bottom: 30px;
  background: white;
}
.control-input { width: 180px; }

.dashboard-card { background: white; padding: 20px; height: 100%; }
.roadmap-timeline-card { background: white; padding: 20px; min-height: 500px; }
.card-title { font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #303133; border-left: 4px solid #409EFF; padding-left: 10px; }

.radar-chart-box { width: 100%; height: 300px; margin-bottom: 10px; }

.ai-insight {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #c2e7b0;
}
.insight-title { color: #67C23A; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; gap: 5px; }
.ai-insight p { color: #606266; font-size: 13px; line-height: 1.6; margin: 0; }

/* 时间轴样式 */
.timeline-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #eee;
  transition: all 0.3s;
}
.timeline-box:hover { transform: translateX(5px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.active-node {
  background: #ecf5ff;
  border-color: #b3d8ff;
  box-shadow: 0 4px 12px rgba(64,158,255,0.15);
}

.node-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.time-tag { font-weight: bold; color: #409EFF; }
.node-title { font-weight: bold; color: #303133; font-size: 15px; }
.node-content { color: #606266; font-size: 14px; margin-bottom: 10px; }

.node-resources { 
  display: flex; 
  align-items: flex-start; 
  gap: 10px; 
  border-top: 1px dashed #e4e7ed; 
  padding-top: 10px; 
  margin-top: 10px;
  flex-direction: column;
}
.res-label { font-size: 12px; color: #909399; font-weight: 600; margin-bottom: 6px; }
.res-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.res-chip {
  font-size: 12px; color: #606266; background: #f0f9ff; border: 1px solid #b3d8ff;
  padding: 4px 10px; border-radius: 12px;
}

/* 证书样式 */
.node-certificates {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border-top: 1px dashed #e4e7ed;
  padding-top: 10px;
  margin-top: 10px;
  flex-direction: column;
}
.cert-label { font-size: 12px; color: #909399; font-weight: 600; margin-bottom: 6px; }
.cert-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.cert-chip {
  font-size: 12px; color: #e6a23c; background: #fdf6ec; border: 1px solid #f5dab1;
  padding: 4px 10px; border-radius: 12px;
}

/* 推荐企业样式 */
.node-companies {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border-top: 1px dashed #e4e7ed;
  padding-top: 10px;
  margin-top: 10px;
  flex-direction: column;
}
.company-label { font-size: 12px; color: #909399; font-weight: 600; margin-bottom: 6px; }
.company-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.company-chip {
  font-size: 12px; color: #67c23a; background: #f0f9eb; border: 1px solid #c2e7b0;
  padding: 4px 10px; border-radius: 12px;
  font-weight: 500;
}

.empty-state-box { text-align: center; padding: 60px; color: #909399; }
.empty-emoji { font-size: 60px; margin-bottom: 20px; }
/* --- 生涯规划控制栏 Pro 样式 --- */

/* 1. 外层容器：左右布局，增加投影和圆角 */
.control-bar-pro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 30px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95); /* 磨砂白 */
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1); /* 柔和投影 */
  border: 1px solid rgba(255, 255, 255, 0.6);
}

/* 2. 左侧标题区 */
.control-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.control-title {
  font-size: 18px;
  font-weight: 800;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.icon-pulse {
  color: #409EFF;
  animation: pulse 2s infinite;
}
.control-subtitle {
  font-size: 13px;
  color: #909399;
  letter-spacing: 0.5px;
}

/* 3. 右侧操作区：弹性布局，防止重叠 */
.control-right {
  display: flex;
  align-items: center;
  gap: 16px; /* 控件之间的间距 */
}

/* 下拉框样式优化 */
.select-item {
  width: 180px; /* 增加宽度，防止文字截断 */
  transition: all 0.3s;
}
.select-item:hover {
  transform: translateY(-2px); /* 悬浮微动效 */
}

/* 按钮样式优化 */
.generate-btn {
  padding: 0 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}
.generate-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* 定义简单的呼吸动画 */
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

/* 📱 适配手机端：如果是小屏幕，自动变成竖排 */
@media (max-width: 768px) {
  .control-bar-pro {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  .control-right {
    width: 100%;
    flex-direction: column;
    gap: 12px;
  }
  .select-item, .generate-btn {
    width: 100% !important;
  }
}
/* AI 按钮特效 */
.ai-jump-btn {
  background: linear-gradient(135deg, #FF4B4B 0%, #FF914D 100%); /* Streamlit 风格渐变红 */
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 20px; /* 圆角 */
  font-weight: bold;
  cursor: pointer;
  margin-left: 15px; /* 和左边的按钮拉开点距离 */
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(255, 75, 75, 0.2);
}

.ai-jump-btn:hover {
  transform: translateY(-2px); /* 鼠标悬停上浮 */
  box-shadow: 0 6px 12px rgba(255, 75, 75, 0.3);
}
/* 录音按钮激活状态：变红 */
.is-recording-active {
  color: #F56C6C !important;      /* 红色文字/图标 */
  background-color: #fef0f0 !important; /* 浅红背景 */
  border-color: #fab6b6 !important;     /* 红色边框 */
}

/* 麦克风图标呼吸动画 */
.mic-pulse {
  animation: pulse-animation 1.5s infinite ease-in-out;
}

@keyframes pulse-animation {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.6; }
  100% { transform: scale(1); opacity: 1; }
}
/* --- 修复布局压缩 (必加) --- */
.input-row {
  width: 100%;
  display: flex; /* 让子元素横向排列 */
}

/* 强制输入框占满剩余空间 */
.full-width-input {
  flex: 1; 
  width: 100%;
}

/* 录音按钮激活态 */
.recording-active {
  color: #F56C6C !important;
  background-color: #fef0f0 !important;
  border-color: #fab6b6 !important;
}

/* 呼吸动画 */
.mic-pulse {
  animation: pulse 1.5s infinite ease-in-out;
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.6; }
  100% { transform: scale(1); opacity: 1; }
}
/* --- 修复布局压缩 --- */
.input-row {
  width: 100%;
  display: flex; 
}
.full-width-input {
  flex: 1; 
  width: 100%;
}

/* --- 录音按钮特效 --- */
.recording-active {
  color: #F56C6C !important;
  background-color: #fef0f0 !important;
  border-color: #fab6b6 !important;
}
.mic-pulse {
  animation: pulse 1.5s infinite ease-in-out;
}

/* --- 🚀 火箭按钮丝滑过渡 --- */
.rocket-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  font-weight: bold;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.6; }
  100% { transform: scale(1); opacity: 1; }
}
/* 新增按钮的样式适配，保证间距美观 */
.assessment-btn {
  margin-right: 12px; /* 和生成按钮保持间距，与现有布局一致 */
  transition: all 0.2s ease;
}

.assessment-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

/* 保持原有样式不变 */
/* ... 你的其他样式 ... */