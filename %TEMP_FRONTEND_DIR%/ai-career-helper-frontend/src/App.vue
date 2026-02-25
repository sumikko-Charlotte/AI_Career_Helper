<script setup>
// ==========================================
// 1. 导入依赖 (Imports)
// ==========================================
import { ref, reactive, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import html2canvas from 'html2canvas'
import MarkdownIt from 'markdown-it'
import {
  Monitor, ChatDotRound, DocumentChecked, User, Odometer, MagicStick,
  Calendar, SwitchButton, CircleCheck, VideoPlay, Trophy, Loading, Compass, Aim,
  Microphone, Clock, Collection, InfoFilled, ArrowRight
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
// 合并冲突：保留使用可空合并运算符的 API_BASE 定义，兼容环境变量未配置的情况
const API_BASE = import.meta.env.VITE_API_BASE ?? ''
// 报告生成降级开关（开发/测试环境可通过 .env 配置，例如：VITE_INTERVIEW_REPORT_NO_FALLBACK=true）
const INTERVIEW_REPORT_NO_FALLBACK = import.meta.env.VITE_INTERVIEW_REPORT_NO_FALLBACK === 'true'
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
    content: '你好，我是AI模拟面试官😊'
  }
])
const jobsData = ref([])
// --- 模拟面试优化：加载状态、打字机效果、缓存 ---
const aiThinkingMsgId = ref(null) // 当前正在思考的消息ID（用于显示加载状态）
const typingTimer = ref(null) // 打字机效果定时器
const CACHE_KEY = 'interview_cache'
const CACHE_EXPIRE_DAYS = 7
const TIMEOUT_MS = 15000 // 15秒超时（用于最终失败判断）
const AI_TIMEOUT_MS = 8000 // 8秒超时（用于触发模板降级）
const MAX_RETRY = 1 // 最多重试1次
const useTemplateMode = ref(false) // 用户主动选择模板模式
const templateQuestionIndex = ref(0) // 模板问题索引（用于轮次逻辑）
// --- 模拟面试：引导环节状态 ---
const isGuidingPhase = ref(true) // 是否在引导环节（true=引导环节，false=正式面试）
// 引导环节只负责收集基础信息（年级、岗位），不再“凑轮数”
const guideRoundCount = ref(0) // 已完成的引导轮次（主要用于兜底保护，避免死循环）
const guideMaxRounds = 5 // 安全上限（极端情况下强制跳出引导）
// --- 模拟面试：面试终止 & 提问状态 ---
const isInterviewEnded = ref(false) // 面试是否已终止
const interviewReportLoading = ref(false) // 报告生成中
const interviewReportMarkdown = ref('') // 生成的报告内容
const lastInterviewQuestionText = ref('') // 上一次提问内容（用于去重）
const interviewStartTime = ref(null) // 面试开始时间（首条用户回答时间）
const interviewEndTime = ref(null) // 面试结束时间（终止时刻）
// 正式面试问题追踪
const usedQuestionIds = ref(new Set()) // 已使用的问题 ID
const usedDimensions = ref(new Set()) // 近期已使用的问题维度
// --- 面试官性别选择 ---
const interviewerGender = ref(localStorage.getItem('interviewer_gender') || 'female') // 默认女性，从缓存读取
const genderSelectionVisible = ref(true) // 性别选择组件是否可见（引导环节开始时显示）

// --- 语音输入状态 ---
const voiceLang = ref('zh-CN') // 语音识别语言：默认中文
const voiceSeconds = ref(0) // 当前录音时长（秒）
let voiceAutoStopTimer = null
let voiceDurationTimer = null

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

// --- 竞争力沙盘：表单输入（替换原滑块，但不改变整体布局） ---
const sandboxForm = reactive({
  gpa: '',
  project: '',
  intern: '',
  competition: '',
  english: '',
  leader: ''
})
const sandboxReportLoading = ref(false)
const sandboxReportMarkdown = ref('')
const sandboxReportHtml = computed(() => (sandboxReportMarkdown.value ? md.render(sandboxReportMarkdown.value) : ''))

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
// 👇 语音合成：自然语音 + 文本预处理 (过滤表情/图片等噪音)
// ============================================

// 全局变量防止秒断
let currentUtterance = null 

// 语音播报前的文本清洗：去掉图片/表情等描述，仅保留纯文本内容
const _cleanSpeechText = (raw) => {
  if (!raw) return ''
  let text = String(raw)

  // 1. 去掉 Markdown 图片语法 ![alt](url)
  text = text.replace(/!\[[^\]]*]\([^)]*\)/g, '')

  // 2. 去掉形如 [image] / [图片] / [表情] / [xxx 表情 xxx] 的占位内容
  text = text.replace(/\[\s*(image|img|图片|表情|emoji|表情包)\s*]/gi, '')
  text = text.replace(/\[[^\]]*(image|img|图片|表情|emoji|表情包)[^\]]*]/gi, '')

  // 3. 去掉可能的 HTML 标签占位（如 <image ...>）
  text = text.replace(/<[^>]+>/g, '')

  // 4. 多个空行/空白压缩
  text = text.replace(/\s{2,}/g, ' ')
  text = text.replace(/\n{3,}/g, '\n\n')

  return text.trim()
}

const speakText = (text) => {
  if (!window.speechSynthesis) return

  // 1. 强制打断之前的发音
  window.speechSynthesis.cancel()

  // 2. 创建发音请求（先做文本清洗，过滤表情/图片描述等噪音）
  const cleanText = _cleanSpeechText(text)
  if (!cleanText) return
  currentUtterance = new SpeechSynthesisUtterance(cleanText)

  // 3. 🔥 核心修改：根据用户选择的面试官性别选择音色
  const voices = window.speechSynthesis.getVoices()
  
  // 根据性别选择音色
  let bestVoice = null
  if (interviewerGender.value === 'female') {
    // 女性面试官：优先使用女声音色
    bestVoice = 
      voices.find(v => v.name.includes('Xiaoxiao')) || 
      voices.find(v => v.name.includes('Xiaoyi')) ||
      voices.find(v => v.name.includes('Natural') && v.lang.includes('zh') && (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('女'))) ||
      voices.find(v => v.name.includes('Google') && v.lang.includes('zh')) ||
      voices.find(v => v.lang.includes('zh') && v.gender === 'female') ||
      voices.find(v => v.lang.includes('zh'))
  } else {
    // 男性面试官：优先使用男声音色
    bestVoice = 
      voices.find(v => v.name.includes('Yunxi')) || 
      voices.find(v => v.name.includes('Yunyang')) ||
      voices.find(v => v.name.includes('Natural') && v.lang.includes('zh') && (v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('男'))) ||
      voices.find(v => v.name.includes('Google') && v.lang.includes('zh')) ||
      voices.find(v => v.lang.includes('zh') && v.gender === 'male') ||
      voices.find(v => v.lang.includes('zh'))
  }

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
    if (voiceAutoStopTimer) clearTimeout(voiceAutoStopTimer)
    if (voiceDurationTimer) clearInterval(voiceDurationTimer)
    voiceAutoStopTimer = null
    voiceDurationTimer = null
    voiceSeconds.value = 0

    if (recognitionInstance) recognitionInstance.stop()
    isRecording.value = false
    return
  }

  // 开始录音
  recognitionInstance = new SpeechRecognition()
  recognitionInstance.lang = voiceLang.value || 'zh-CN'
  recognitionInstance.interimResults = false

  recognitionInstance.onstart = () => {
    isRecording.value = true
    voiceSeconds.value = 0

    if (voiceDurationTimer) clearInterval(voiceDurationTimer)
    voiceDurationTimer = setInterval(() => {
      voiceSeconds.value += 1
    }, 1000)

    if (voiceAutoStopTimer) clearTimeout(voiceAutoStopTimer)
    // 最长录音 60 秒，超时自动停止
    voiceAutoStopTimer = setTimeout(() => {
      if (recognitionInstance) recognitionInstance.stop()
    }, 60000)

    ElMessage.success(`开始录音（${voiceLang.value === 'en-US' ? 'English' : '中文'}），请在 60 秒内完成回答`)
  }
  recognitionInstance.onend = () => {
    isRecording.value = false
    if (voiceAutoStopTimer) clearTimeout(voiceAutoStopTimer)
    if (voiceDurationTimer) clearInterval(voiceDurationTimer)
    voiceAutoStopTimer = null
    voiceDurationTimer = null
    voiceSeconds.value = 0
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
// 简历医生 URL：部署时通过 Vercel 环境变量 VITE_RESUME_DOCTOR_URL 设置
const RESUME_DOCTOR_URL = import.meta.env.VITE_RESUME_DOCTOR_URL || '{{STREAMLIT_RESUME_DOCTOR_URL}}'
const goToResumeDoctor = () => window.open(RESUME_DOCTOR_URL, '_blank')

const scrollChatToBottom = () => {
  const el = document.querySelector('.chat-window')
  if (el) el.scrollTop = el.scrollHeight
}

// --- 模拟面试：新手引导上下文（仅用于对话引导，不影响既有功能） ---
const interviewGuide = reactive({
  started: false,
  // 用于让 AI 知道面试方向（用户回答后会自动并入上下文发给 AI）
  targetRole: '',
  grade: '',
  targetType: '', // 实习/全职/未说明
  // 模板对话状态（用于保持连贯性）
  templateRole: '', // 当前选择的岗位模板
  templateIndex: 0, // 当前岗位模板的问题索引
  templateStage: 'common', // 当前阶段：common（通用引导）或具体岗位
  // 引导环节状态
  guideIndex: 0 // 引导环节模板索引
})

const _stripMarkdownToText = (mdText) => {
  if (!mdText) return ''
  return String(mdText)
    .replace(/```[\s\S]*?```/g, '') // 去掉代码块
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
    .replace(/\[[^\]]*\]\([^)]+\)/g, '$1')
    .replace(/[*_>#-]{1,3}\s?/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const _defaultInterviewTips = (question) => {
  const q = String(question || '')
  // 只给“逻辑框架”，避免给完整答案模板
  if (/项目|经历|挑战|难点|最难|你做了什么/i.test(q)) {
    return [
      '用 STAR 拆解：背景(S)→任务(T)→行动(A)→结果(R)。',
      '行动(A)强调“你做了什么、为什么这么做、你做了哪些取舍”。',
      '结果(R)尽量量化：指标/规模/时延/成本/效率/稳定性。',
    ].join('\n')
  }
  if (/缺点|不足|失败|挫折/i.test(q)) {
    return [
      '先给结论：选择一个“可改进且已在改善”的不足点。',
      '再讲证据：你如何发现问题（反馈/数据/复盘）。',
      '最后讲改进：采取了哪些行动、效果如何、后续计划。',
    ].join('\n')
  }
  if (/岗位|方向|为什么|动机/i.test(q)) {
    return [
      '一句话定位目标岗位与原因（兴趣/能力/经历匹配）。',
      '用 2-3 条证据支撑：项目/课程/实习/竞赛/成果。',
      '最后给“近期目标”：实习/校招的时间与行动。',
    ].join('\n')
  }
  return [
    '结构建议：先结论→再分点→最后补证据。',
    '每点尽量带"证据"：数据/例子/对比/结果。',
    '不确定时可以澄清问题边界（场景/指标/约束）。',
  ].join('\n')
}

// --- 模拟面试：引导环节模板库（降级备用方案，3-5轮通用引导） ---
const guideTemplates = [
  {
    user_input: /你好|开始|体验|面试/,
    template_reply: '你好呀！我是你的专属模拟面试官😊 在正式面试前，我们先轻松聊一聊，帮你梳理一下自己的情况～可以先简单说说你的学历阶段和想面试的岗位吗？',
    tip: '回答学历和岗位时，可以简洁明了：例如"我是大二，想体验前端工程师岗位"～'
  },
  {
    user_input: /(大一|大二|大三|大四|研一|研二|研三).*(前端|算法|后端|Java|Python|全栈)/,
    template_reply: '很好！那接下来聊聊你的经历～你目前有相关的项目经历、实习经历或者竞赛经历吗？有的话可以简单说说，没有也没关系，我们可以聊聊学习经历～',
    tip: '回答经历类问题时，可以用「一句话概括经历 + 核心做了什么 + 收获了什么」的逻辑，简洁明了哦～'
  },
  {
    user_input: /(项目|实习|竞赛|经历|做过|学过)/,
    template_reply: '听起来不错！那再问一个问题：你为什么想面试这个岗位呀？是对这个方向感兴趣，还是有其他的规划？',
    tip: '回答求职动机时，可以结合「岗位特点 + 自身兴趣/优势」来答，会更贴合HR的期待～'
  },
  {
    user_input: /(兴趣|喜欢|规划|目标|原因|为什么)/,
    template_reply: '目标很清晰！最后一个问题：如果拿到这个岗位的offer，你未来1-2年有什么样的学习和工作规划呢？',
    tip: '回答职业规划时，可以分短期（1年内）和中期（1-2年）来谈，结合岗位发展方向，会更具体哦～'
  },
  {
    user_input: /(规划|计划|目标|未来|学习|工作)/,
    template_reply: '好的，我大概了解你的情况啦！那我们现在开始正式的岗位面试吧，问题会贴合你刚才说的信息，不用紧张，大胆回答就好～',
    tip: '' // 最后一轮不需要提示，直接进入正式面试
  }
]

// --- 模拟面试：多岗位、全学历适配模板库（降级备用方案） ---
const interviewTemplates = {
  common: [
    {
      user_input: '你好',
      template_reply: '你好呀！我是你的专属模拟面试官😊 先轻松聊一聊～你想体验哪个岗位的面试呀？可选：前端工程师、算法工程师、全栈后端工程师、Java开发、Python开发'
    },
    {
      user_input: '我还没想好选哪个岗位',
      template_reply: '没关系～那你可以先告诉我你的学历阶段吗？比如大一大二/大三大四/研究生，我可以给你推荐适配的岗位体验哦！'
    },
    {
      user_input: /我是大一大二|大一大二|大一|大二/,
      template_reply: '超棒的！大一大二就开始准备面试啦～那我推荐你先体验基础版的Python开发或前端工程师哦，问题会偏基础，主打熟悉面试流程，要选其中一个吗？'
    },
    {
      user_input: /我是大三大四|大三大四|大三|大四.*找实习|找实习.*大三大四/,
      template_reply: '加油呀！实习面试会侧重基础+项目落地能力～那你确定要体验的岗位是？前端/算法/全栈后端/Java/Python'
    },
    {
      user_input: /我是研究生|研究生|研一|研二|研三.*找全职|找全职.*研究生|找实习.*研究生/,
      template_reply: '研究生面试会侧重专业深度+科研/项目成果哦～那你想体验的目标岗位是？算法/全栈后端/Java/Python（这些岗位更适配研究生求职哦）'
    },
    {
      user_input: /好的.*就选|选这个|确定.*岗位|就选.*岗位/,
      template_reply: '没问题！那我们正式开始面试啦～首先第一个基础问题：请做一个1-2分钟的自我介绍，包括你的学历、专业和相关的学习/项目/科研经历哦～'
    },
    {
      user_input: /我叫|来自|学历|专业|做过|学过/,
      template_reply: '非常清晰的自我介绍！接下来我们进入岗位相关的问题环节，问题会贴合你的学历阶段，不用紧张，大胆回答就好～'
    },
    {
      user_input: /没有.*项目|没有.*科研|没有.*经历/,
      template_reply: '没关系的！大一大二/零基础的同学都容易遇到这个问题～那我们重点聊聊你学过的核心知识点吧，这也是面试中很看重的部分～'
    }
  ],
  '前端工程师': [
    {
      user_input: /前端工程师|前端/,
      template_reply: '好的！那我们开始前端工程师的模拟面试～先问一个基础问题：你了解HTML、CSS、JavaScript的核心区别吗？分别说说它们的作用～'
    },
    {
      user_input: /HTML.*结构|CSS.*样式|JS.*交互|JavaScript.*交互/,
      template_reply: '回答很准确！那再问一个：你用过哪些前端框架？比如Vue/React/Angular，简单说说你最熟悉的那个框架的核心特点～'
    },
    {
      user_input: /Vue|React|Angular|双向数据绑定|组件化/,
      template_reply: '很棒！那你在使用Vue的时候，有没有遇到过跨域问题？你是怎么解决的？'
    },
    {
      user_input: /跨域|代理|JSONP|CORS/,
      template_reply: '方法很实用！那再问一个：你知道什么是虚拟DOM吗？它的作用是什么？'
    },
    {
      user_input: /不知道.*虚拟DOM|不太清楚.*虚拟DOM|虚拟DOM/,
      template_reply: '没关系，这个是前端中级考点～虚拟DOM是真实DOM的抽象副本，作用是减少真实DOM的操作，提升页面渲染效率，记下来以后学习哦～那我们换个基础问题：CSS中Flex布局的核心属性有哪些？'
    },
    {
      user_input: /大一大二.*没学过.*框架|没学过.*框架/,
      template_reply: '没问题！那我们聊基础～CSS中如何实现元素的水平垂直居中？说说你知道的方法～'
    },
    {
      user_input: /居中|margin.*auto|定位.*transform|Flex布局/,
      template_reply: '方法很全面！基础很扎实～那JS中let/var/const的区别是什么？这个是面试必考点哦～'
    },
    {
      user_input: /面试结束|结束吧/,
      template_reply: '好的！今天的前端工程师模拟面试就到这里啦～如果是大一大二，建议继续夯实HTML/CSS/JS基础；如果是找实习，建议多做一个完整的前端项目（比如博客/商城），加油！💪'
    }
  ],
  '算法工程师': [
    {
      user_input: /算法工程师|算法/,
      template_reply: '好的！算法工程师面试会侧重数据结构+算法+模型基础～第一个问题：你最熟悉的排序算法有哪些？说说快速排序的核心思路～'
    },
    {
      user_input: /快排|冒泡|归并|分治|基准值/,
      template_reply: '核心思路很准确！那快排的时间复杂度和空间复杂度分别是多少？最好/最坏情况呢？'
    },
    {
      user_input: /时间复杂度|O\(nlogn\)|O\(n²\)|空间复杂度/,
      template_reply: '回答完美！那再问一个：你了解什么是动态规划？它的核心解题步骤是什么？'
    },
    {
      user_input: /动态规划|重叠子问题|状态定义|状态转移/,
      template_reply: '很棒！那你用过哪些机器学习模型？比如线性回归/逻辑回归/决策树，说说其中一个的适用场景～'
    },
    {
      user_input: /研究生.*模型|科研.*模型|机器学习模型/,
      template_reply: '太优秀了！那你在做这个模型的时候，遇到过过拟合问题吗？你是怎么解决的？'
    },
    {
      user_input: /大三大四.*没做过.*算法|没做过.*算法项目/,
      template_reply: '没关系！那我们聊基础～数组和链表的核心区别是什么？分别适用于什么场景？'
    },
    {
      user_input: /不知道.*动态规划|没学过.*机器学习/,
      template_reply: '没关系～算法工程师对基础要求较高，建议先从数据结构（数组/链表/树）和基础算法（排序/查找）学起，研究生同学可以再补充机器学习/深度学习基础哦～那我们换个问题：二叉树的前序遍历有哪些方法？'
    },
    {
      user_input: /面试结束|结束吧/,
      template_reply: '好的！今天的算法工程师模拟面试就到这里啦～算法学习重在刷题+理解，建议多刷LeetCode（简单/中等题），结合项目/科研落地，加油！💪'
    }
  ],
  '全栈后端工程师': [
    {
      user_input: /全栈后端|全栈|后端工程师/,
      template_reply: '好的！全栈后端面试会侧重后端基础+前后端交互+项目架构～第一个问题：你了解什么是RESTful API？它的核心设计原则是什么？'
    },
    {
      user_input: /RESTful|接口设计|资源导向|HTTP方法|GET|POST|PUT|DELETE/,
      template_reply: '回答很专业！那你用过哪些后端框架？比如SpringBoot/Django/Flask，说说你最熟悉的框架的核心优势～'
    },
    {
      user_input: /SpringBoot|Django|Flask|自动配置|快速开发/,
      template_reply: '很棒！那你在项目中用到过数据库吗？比如MySQL，说说你知道的索引类型和作用～'
    },
    {
      user_input: /MySQL|索引|主键索引|普通索引|联合索引|查询效率/,
      template_reply: '非常准确！那数据库中什么是事务？ACID特性分别指什么？'
    },
    {
      user_input: /大一大二.*没学过.*后端框架|没学过后端框架/,
      template_reply: '没问题！那我们聊基础～HTTP协议的常用状态码有哪些？比如200/404/500，分别代表什么？'
    },
    {
      user_input: /状态码|200|404|500|302|401/,
      template_reply: '基础很扎实！那再问一个：什么是Cookie和Session？它们的区别是什么？'
    },
    {
      user_input: /不知道.*RESTful|没接触过.*数据库/,
      template_reply: '没关系～全栈后端需要兼顾前后端，建议先从一门后端语言（Java/Python）+ 基础数据库（MySQL）学起，再接触框架哦～那我们换个问题：GET和POST请求的核心区别是什么？'
    },
    {
      user_input: /面试结束|结束吧/,
      template_reply: '好的！今天的全栈后端工程师模拟面试就到这里啦～全栈开发重在"全"+"深"，建议多做一个前后端联动的项目（比如管理系统），夯实基础+了解架构，加油！💪'
    }
  ],
  'Java开发工程师': [
    {
      user_input: /Java开发|Java工程师|Java/,
      template_reply: '好的！Java开发面试核心侧重基础+JVM+框架+并发～第一个问题：Java中的面向对象三大特性是什么？分别说说含义～'
    },
    {
      user_input: /封装|继承|多态|面向对象/,
      template_reply: '回答很准确！那再问一个：Java中String、StringBuffer、StringBuilder的区别是什么？'
    },
    {
      user_input: /String|StringBuffer|StringBuilder|不可变|线程安全/,
      template_reply: '很棒！那你了解JVM的内存结构吗？说说堆、栈、方法区的作用～'
    },
    {
      user_input: /JVM|堆|栈|方法区|内存结构/,
      template_reply: '非常专业！那Java中的线程池有什么作用？核心参数有哪些？'
    },
    {
      user_input: /大三大四.*找Java实习|找Java实习.*没接触过JVM/,
      template_reply: '没关系！实习面试侧重基础+框架基础～那你用过SpringBoot吗？说说它的自动配置原理？'
    },
    {
      user_input: /大一大二.*刚学Java|刚学Java/,
      template_reply: '没问题！那我们聊基础～Java中int和Integer的区别是什么？什么是自动装箱和拆箱？'
    },
    {
      user_input: /不知道.*线程池|没学过JVM/,
      template_reply: '没关系～JVM和并发是Java高级考点，找实习可以先夯实基础（面向对象/集合/IO），再接触框架和JVM哦～那我们换个问题：Java中的集合框架有哪些？比如List/Set/Map，说说ArrayList和LinkedList的区别～'
    },
    {
      user_input: /面试结束|结束吧/,
      template_reply: '好的！今天的Java开发工程师模拟面试就到这里啦～Java学习重在基础扎实，建议多刷Java基础题，结合SpringBoot做实战项目，加油！💪'
    }
  ],
  'Python开发工程师': [
    {
      user_input: /Python开发|Python工程师|Python/,
      template_reply: '好的！Python开发面试侧重基础+库/框架+实战～第一个问题：Python中的列表（list）和元组（tuple）的核心区别是什么？'
    },
    {
      user_input: /list|tuple|可变|不可变/,
      template_reply: '回答很准确！那再问一个：Python中的装饰器是什么？它的作用是什么？'
    },
    {
      user_input: /装饰器|增强函数|开闭原则/,
      template_reply: '很棒！那你用过哪些Python框架？比如Django/Flask/FastAPI，说说它们的适用场景～'
    },
    {
      user_input: /Django|Flask|FastAPI|轻量级|全栈式/,
      template_reply: '非常专业！那Python中的GIL锁是什么？它对多线程有什么影响？'
    },
    {
      user_input: /大一大二.*刚学Python|刚学Python/,
      template_reply: '没问题！那我们聊基础～Python中的if __name__ == \'__main__\'的作用是什么？'
    },
    {
      user_input: /__name__|__main__|直接运行|导入/,
      template_reply: '基础很扎实！那再问一个：Python中的字典（dict）是什么数据结构？它的查询效率为什么高？'
    },
    {
      user_input: /不知道.*装饰器|不知道.*GIL/,
      template_reply: '没关系～装饰器和GIL是Python中级考点，零基础可以先夯实基础（数据类型/流程控制/函数），再接触进阶知识点哦～那我们换个问题：Python中如何实现列表去重？说说你知道的方法～'
    },
    {
      user_input: /面试结束|结束吧/,
      template_reply: '好的！今天的Python开发工程师模拟面试就到这里啦～Python上手快，建议结合实战（爬虫/数据分析/小项目）巩固，加油！💪'
    }
  ]
}

// --- 正式面试：问题池（按维度划分，至少 8-10 个问题，确保不重复） ---
const interviewQuestionPool = [
  {
    id: 'basic_1',
    dimension: '专业基础',
    text: '请用面试官能听懂的方式，概括一下你目前在本专业（或目标岗位方向）最扎实的三门课程或核心知识点，并简单说明理由。'
  },
  {
    id: 'basic_2',
    dimension: '专业基础',
    text: '回想你最近一次觉得“学得比较吃力”的专业知识或技术点，它是什么？你是通过哪些方式把它啃下来的？'
  },
  {
    id: 'project_1',
    dimension: '项目/实习经历',
    text: '请从你的课程作业、项目或实习中，选一个你最有成就感的经历，用 STAR 结构讲一讲（背景-任务-行动-结果）。'
  },
  {
    id: 'project_2',
    dimension: '项目/实习经历',
    text: '有没有一个项目/实习经历，是一开始推进得不顺利，但最后你找到解决方案的？请重点讲讲你具体做了什么。'
  },
  {
    id: 'motivation_1',
    dimension: '求职动机',
    text: '如果现在就要投递与你当前模拟方向最相关的岗位，你会怎么向面试官说明“为什么想做这个方向”？'
  },
  {
    id: 'motivation_2',
    dimension: '求职动机',
    text: '你觉得自己和其他同专业同学相比，在求职这件事上最大的优势和短板分别是什么？请各举 1-2 点。'
  },
  {
    id: 'future_1',
    dimension: '未来规划',
    text: '站在 1-2 年的时间尺度，如果拿到了理想岗位/方向的机会，你最希望自己在哪些方面有明显成长？'
  },
  {
    id: 'future_2',
    dimension: '未来规划',
    text: '假设你还有一年的在校时间，可以自主安排，你会如何在“课程、项目/科研、实习、竞赛/比赛”之间做时间分配？为什么？'
  },
  {
    id: 'scenario_1',
    dimension: '场景应变',
    text: '如果在真实面试中，面试官问了一个你完全不会的问题，你一般会怎么处理这种场景？请结合你真实的做法或想法来回答。'
  },
  {
    id: 'scenario_2',
    dimension: '场景应变',
    text: '假设你进入了一个新团队，前两周发现自己在知识和效率上都落后于同组同学，你会怎么做？请具体说说你的应对思路。'
  }
]

// 获取引导环节模板回复（降级备用方案）
const getGuideTemplateResponse = (userMsg) => {
  const msg = String(userMsg || '').trim()
  const currentIndex = interviewGuide.guideIndex
  
  // 如果已到最后一轮，返回过渡话术
  if (currentIndex >= guideTemplates.length - 1) {
    const lastTemplate = guideTemplates[guideTemplates.length - 1]
    return {
      reply: lastTemplate.template_reply,
      question: '',
      tips: '',
      tip: '', // 最后一轮不需要提示
      isTemplate: true,
      isGuide: true
    }
  }
  
  // 尝试匹配当前索引的模板
  const currentTemplate = guideTemplates[currentIndex]
  const inputPattern = currentTemplate.user_input
  let isMatch = false
  
  if (typeof inputPattern === 'string') {
    isMatch = msg.toLowerCase().includes(inputPattern.toLowerCase())
  } else if (inputPattern instanceof RegExp) {
    isMatch = inputPattern.test(msg)
  }
  
  // 如果匹配成功，返回下一个模板；否则返回当前模板
  if (isMatch && currentIndex < guideTemplates.length - 1) {
    interviewGuide.guideIndex = currentIndex + 1
    const nextTemplate = guideTemplates[currentIndex + 1]
    return {
      reply: nextTemplate.template_reply,
      question: '',
      tips: '',
      tip: nextTemplate.tip || '',
      isTemplate: true,
      isGuide: true
    }
  } else {
    // 未匹配或已到最后，返回当前模板
    return {
      reply: currentTemplate.template_reply,
      question: '',
      tips: '',
      tip: currentTemplate.tip || '',
      isTemplate: true,
      isGuide: true
    }
  }
}

// 获取模板回复（多岗位、全学历适配，基于用户输入和岗位匹配）
const getTemplateResponse = (userMsg) => {
  const msg = String(userMsg || '').trim()
  const msgLower = msg.toLowerCase()
  
  // 1. 确定当前使用的模板库（common 或 具体岗位）
  let currentTemplates = interviewTemplates.common
  let currentStage = interviewGuide.templateStage || 'common'
  
  // 2. 检测用户是否选择了岗位（从用户输入或 interviewGuide 中获取）
  const roleKeywords = {
    '前端工程师': /前端工程师|前端/,
    '算法工程师': /算法工程师|算法/,
    '全栈后端工程师': /全栈后端|全栈|后端工程师/,
    'Java开发工程师': /Java开发|Java工程师|Java/,
    'Python开发工程师': /Python开发|Python工程师|Python/
  }
  
  // 如果用户输入中包含岗位关键词，切换到对应岗位模板
  for (const [role, pattern] of Object.entries(roleKeywords)) {
    if (pattern.test(msg)) {
      interviewGuide.templateRole = role
      interviewGuide.templateStage = role
      interviewGuide.templateIndex = 0
      currentTemplates = interviewTemplates[role] || interviewTemplates.common
      currentStage = role
      break
    }
  }
  
  // 如果 interviewGuide 中已有岗位信息，使用对应岗位模板
  if (!currentTemplates || currentTemplates === interviewTemplates.common) {
    if (interviewGuide.templateRole && interviewTemplates[interviewGuide.templateRole]) {
      currentTemplates = interviewTemplates[interviewGuide.templateRole]
      currentStage = interviewGuide.templateRole
    }
  }
  
  // 3. 在当前模板库中匹配用户输入
  let matchedTemplate = null
  let matchedIndex = -1
  
  for (let i = 0; i < currentTemplates.length; i++) {
    const template = currentTemplates[i]
    const inputPattern = template.user_input
    
    let isMatch = false
    if (typeof inputPattern === 'string') {
      isMatch = msgLower.includes(inputPattern.toLowerCase())
    } else if (inputPattern instanceof RegExp) {
      isMatch = inputPattern.test(msg)
    }
    
    if (isMatch) {
      matchedTemplate = template
      matchedIndex = i
      break
    }
  }
  
  // 4. 如果匹配成功，返回对应回复
  if (matchedTemplate) {
    // 更新索引，用于下次匹配（如果继续在当前岗位模板中）
    if (currentStage !== 'common') {
      interviewGuide.templateIndex = (matchedIndex + 1) % currentTemplates.length
    }
    
    return {
      reply: matchedTemplate.template_reply,
      question: '', // 模板回复中已包含问题，不需要额外question
      tips: _defaultInterviewTips(matchedTemplate.template_reply),
      isTemplate: true
    }
  }
  
  // 5. 如果没有匹配，根据当前阶段返回默认回复
  if (currentStage === 'common') {
    // 通用阶段：返回第一个通用模板
    const defaultTemplate = interviewTemplates.common[0]
    return {
      reply: defaultTemplate.template_reply,
      question: '',
      tips: _defaultInterviewTips(defaultTemplate.template_reply),
      isTemplate: true
    }
  } else {
    // 岗位阶段：返回当前岗位模板的下一个问题（按索引）
    const roleTemplates = interviewTemplates[currentStage] || interviewTemplates.common
    const nextIndex = interviewGuide.templateIndex % roleTemplates.length
    const nextTemplate = roleTemplates[nextIndex]
    interviewGuide.templateIndex = (nextIndex + 1) % roleTemplates.length
    
    return {
      reply: nextTemplate.template_reply,
      question: '',
      tips: _defaultInterviewTips(nextTemplate.template_reply),
      isTemplate: true
    }
  }
}

// 调用后端已接入 DeepSeek 的接口（引导环节专用）
const callDeepSeekGuide = async ({ userMsg }) => {
  const guidePrompt = `你是一个亲切友好的面试引导者，面向新手用户（大一大二/面试零基础）。你的任务是帮助用户梳理自身经历、明确面试方向，传递基础回答技巧。

当前阶段：引导环节（面试前的准备阶段）
用户画像：${interviewGuide.grade || '未说明'}，目标岗位：${interviewGuide.targetRole || '未确定'}

请围绕以下方向提问（3-5轮即可）：
1. 破冰类：了解用户的学历阶段和想面试的岗位
2. 经历类：了解用户的项目/实习/竞赛/学习经历
3. 求职动机类：了解用户为什么想面试这个岗位
4. 职业规划类：了解用户未来1-2年的学习和工作规划

要求：
- 问题要新手友好，不涉及专业技术，无专业门槛
- 每次只问一个问题，语气亲切自然
- 在回复末尾可以给一个简短的回答技巧提示（仅文字，不语音播报）
- 如果已完成3-5轮引导，在最后回复中说明"好的，我大概了解你的情况啦！那我们现在开始正式的岗位面试吧"`

  const instruction = `
你将进行"面试前引导环节"对话。请严格输出一个 JSON 对象（可以放在 Markdown 中，但 JSON 必须完整可解析），不要输出多余的文字。

JSON 结构：
{
  "reply": "对用户刚才回答的简短反馈（1-2句）+ 你的下一个引导问题（只问一个问题）",
  "tip": "给用户的【回答技巧轻提示】（仅文字展示，不语音播报，教用户基础的回答逻辑/语言组织技巧，而非直接给回答模板）"
}

要求：
- 引导者语气亲切、友好，问题贴合新手水平
- tip 仅给方法论（如"可以用「一句话概括经历 + 核心做了什么 + 收获了什么」的逻辑"），不要给成段模板答案
- 如果已完成3-5轮引导，在reply中说明"好的，我大概了解你的情况啦！那我们现在开始正式的岗位面试吧"
`

  const res = await axios.post(`${API_BASE}/api/analyze-experiment`, {
    career: '模拟面试（引导环节）',
    answers: {
      system_prompt: guidePrompt,
      guide: interviewGuide,
      history: (chatHistory.value || [])
        .filter(m => m && m.role && typeof m.content === 'string' && !m._isLoading)
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content })),
      user_message: userMsg,
      instruction
    }
  })

  const markdown = res?.data?.markdown || ''
  const parsed = _extractJsonObject(markdown)
  const reply = (parsed?.reply && String(parsed.reply).trim()) || _stripMarkdownToText(markdown) || '（未返回内容）'
  const tip = (parsed?.tip && String(parsed.tip).trim()) || ''

  return { reply, tip }
}

// 调用后端已接入 DeepSeek 的接口（复用 axios + API_BASE，不改后端）
const callDeepSeekInterview = async ({ userMsg }) => {
  const defaultInterviewPrompt = `你是一个严厉但公正的技术面试官。请根据用户的求职意向提出有深度的问题；每次只问一个问题，并在用户回答后追问。`
  const interviewPrompt = localStorage.getItem('admin_ai_interview') || defaultInterviewPrompt

  // 精简历史上下文：只保留最近3轮对话（6条消息），减少传输和计算量
  const compactHistory = (chatHistory.value || [])
    .filter(m => m && m.role && typeof m.content === 'string' && !m._isLoading)
    .slice(-6)
    .map(m => ({ role: m.role, content: m.content }))

  const instruction = `
你将进行“模拟面试”对话。请严格输出一个 JSON 对象（可以放在 Markdown 中，但 JSON 必须完整可解析），不要输出多余的文字。

JSON 结构：
{
  "reply": "对用户刚才回答的简短反馈（1-3句）",
  "question": "你的下一道追问/新问题（只问一个问题）",
  "tips": "给用户的【话术建议与逻辑拆解】（只给框架，不要给可直接照抄的完整回答）"
}

要求：
- 面试官语气专业、真实，问题要结合上下文
- tips 仅给方法论（STAR/MECE/结构化表达/边界条件等），不要给成段模板答案
`

  const res = await axios.post(`${API_BASE}/api/analyze-experiment`, {
    career: '模拟面试（真实对话）',
    answers: {
      system_prompt: interviewPrompt,
      guide: interviewGuide,
      history: compactHistory,
      user_message: userMsg,
      instruction
    }
  })

  const markdown = res?.data?.markdown || ''
  const parsed = _extractJsonObject(markdown)
  const reply = (parsed?.reply && String(parsed.reply).trim()) || _stripMarkdownToText(markdown) || '（未返回内容）'
  const question = (parsed?.question && String(parsed.question).trim()) || ''
  const tips = (parsed?.tips && String(parsed.tips).trim()) || _defaultInterviewTips(question || reply)

  return { reply, question, tips }
}

const fetchJobsData = async () => {
  try {
    const res = await axios.post(`${API_BASE}/api/recommend`)
    if (res.data.success) jobsData.value = res.data.data
  } catch (e) { console.error(e) }
}

// --- 模拟面试优化：本地缓存（高频问题） ---
const getCachedResponse = (userMsg) => {
  try {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}')
    const normalizedMsg = userMsg.trim().toLowerCase()
    // 检查常见问题关键词
    const commonQuestions = [
      '自我介绍', '优缺点', '为什么选择', '职业规划', '项目经历',
      '自我介绍', '优缺点', '为什么', '规划', '项目'
    ]
    const isCommonQuestion = commonQuestions.some(q => normalizedMsg.includes(q))
    if (!isCommonQuestion) return null
    
    const cacheKey = Object.keys(cache).find(k => {
      const cachedMsg = k.toLowerCase()
      return cachedMsg.includes(normalizedMsg) || normalizedMsg.includes(cachedMsg)
    })
    if (!cacheKey) return null
    
    const cached = cache[cacheKey]
    const expireTime = cached.timestamp + (CACHE_EXPIRE_DAYS * 24 * 60 * 60 * 1000)
    if (Date.now() > expireTime) {
      delete cache[cacheKey]
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
      return null
    }
    return cached.response
  } catch (e) {
    return null
  }
}

const setCachedResponse = (userMsg, response) => {
  try {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}')
    cache[userMsg.trim()] = {
      response,
      timestamp: Date.now()
    }
    // 限制缓存大小（最多保留50条）
    const keys = Object.keys(cache)
    if (keys.length > 50) {
      const sorted = keys.sort((a, b) => cache[a].timestamp - cache[b].timestamp)
      sorted.slice(0, keys.length - 50).forEach(k => delete cache[k])
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
  } catch (e) {
    // 忽略缓存错误
  }
}

// --- 打字机效果（逐字显示） ---
const typewriterEffect = (targetMsgId, fullText, onComplete) => {
  if (typingTimer.value) clearInterval(typingTimer.value)
  let index = 0
  const msg = chatHistory.value.find(m => m._id === targetMsgId)
  if (!msg) return
  
  typingTimer.value = setInterval(() => {
    if (index < fullText.length) {
      msg.content = fullText.substring(0, index + 1)
      index++
      scrollChatToBottom()
    } else {
      clearInterval(typingTimer.value)
      typingTimer.value = null
      if (onComplete) onComplete()
    }
  }, 30) // 每30ms显示一个字符
}

// --- 带超时和重试的 API 调用（AI优先模式） ---
const callDeepSeekWithTimeout = async (userMsg, retryCount = 0) => {
  return new Promise(async (resolve, reject) => {
    const timeoutId = setTimeout(() => {
      if (retryCount < MAX_RETRY) {
        ElMessage.warning('网络有点慢，我再想想~')
        // 自动重试一次
        callDeepSeekWithTimeout(userMsg, retryCount + 1).then(resolve).catch(reject)
      } else {
        reject(new Error('请求超时'))
      }
    }, TIMEOUT_MS)
    
    try {
      const result = await callDeepSeekInterview({ userMsg })
      clearTimeout(timeoutId)
      resolve(result)
    } catch (e) {
      clearTimeout(timeoutId)
      if (retryCount < MAX_RETRY) {
        // 重试一次
        setTimeout(() => {
          callDeepSeekWithTimeout(userMsg, retryCount + 1).then(resolve).catch(reject)
        }, 1000)
      } else {
        reject(e)
      }
    }
  })
}

// --- AI优先模式：8秒内获取AI回复，超时则返回null触发降级（引导环节专用） ---
const callDeepSeekGuideWithFastTimeout = async (userMsg) => {
  return new Promise(async (resolve) => {
    const timeoutId = setTimeout(() => {
      resolve(null) // 超时返回null，触发模板降级
    }, AI_TIMEOUT_MS)
    
    try {
      const result = await callDeepSeekGuide({ userMsg })
      clearTimeout(timeoutId)
      resolve(result) // 成功返回结果
    } catch (e) {
      clearTimeout(timeoutId)
      resolve(null) // 失败返回null，触发模板降级
    }
  })
}

// --- AI优先模式：8秒内获取AI回复，超时则返回null触发降级 ---
const callDeepSeekWithFastTimeout = async (userMsg) => {
  return new Promise(async (resolve) => {
    const timeoutId = setTimeout(() => {
      resolve(null) // 超时返回null，触发模板降级
    }, AI_TIMEOUT_MS)
    
    try {
      const result = await callDeepSeekInterview({ userMsg })
      clearTimeout(timeoutId)
      resolve(result) // 成功返回结果
    } catch (e) {
      clearTimeout(timeoutId)
      resolve(null) // 失败返回null，触发模板降级
    }
  })
}

// --- 发送消息 (已集成语音 + 优化响应速度) ---
const sendMessage = async () => {
  if (!chatInput.value || chatSending.value) return
  if (isInterviewEnded.value) {
    ElMessage.warning('面试已终止，无法继续发送消息')
    return
  }
  const userMsg = chatInput.value

  // 记录面试开始时间：第一条用户回答发送时
  if (!interviewStartTime.value) {
    interviewStartTime.value = Date.now()
  }
  
  chatHistory.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  await nextTick()
  scrollChatToBottom()

  try {
    chatSending.value = true
    
    // 新手引导信息：仅作为上下文供 AI 更好地追问，不改变交互
    if (!interviewGuide.started) interviewGuide.started = true
    
    // 检测是否是第一次用户回复（且还在引导环节），如果是则发送引导话术
    if (isGuidingPhase.value && chatHistory.value.filter(m => m.role === 'user').length === 1) {
      // 用户第一次回复，隐藏性别选择，发送引导话术（仅文本，避免表情说明被语音朗读）
      genderSelectionVisible.value = false
      const guideText = '你好呀，我是你的专属 AI 模拟面试官。在正式面试前，我们先轻松聊一聊，帮你梳理一下自己的情况。可以先简单说说你的学历阶段和想面试的岗位吗？'
      const guideTip = '回答学历和岗位时，可以简洁明了：例如“我是大二，想体验前端工程师岗位”。'
      
      // 在用户消息后添加引导消息
      chatHistory.value.push({
        role: 'ai',
        content: guideText,
        tip: guideTip,
        _isGuide: true,
        _isLoading: false,
        _isTemplate: false
      })
      
      // 触发语音播报（不播报tip）
      speakText(guideText)
      await nextTick()
      scrollChatToBottom()
      
      // 直接返回，不继续处理用户消息的AI回复
      chatSending.value = false
      return
    }
    
    // 识别岗位（用于模板匹配）
    const roleKeywords = {
      '前端工程师': /前端工程师|前端/,
      '算法工程师': /算法工程师|算法/,
      '全栈后端工程师': /全栈后端|全栈|后端工程师/,
      'Java开发工程师': /Java开发|Java工程师|Java/,
      'Python开发工程师': /Python开发|Python工程师|Python/
    }
    for (const [role, pattern] of Object.entries(roleKeywords)) {
      if (pattern.test(userMsg) && !interviewGuide.targetRole) {
        interviewGuide.targetRole = role
        interviewGuide.templateRole = role
        interviewGuide.templateStage = role
        break
      }
    }
    
    // 识别学历阶段
    if (!interviewGuide.grade && /(大一|大二|大三|大四|研一|研二|研三)/.test(userMsg)) {
      const m = userMsg.match(/(大一|大二|大三|大四|研一|研二|研三)/)
      if (m) interviewGuide.grade = m[1]
    }
    
    // 识别目标类型（实习/全职）
    if (!interviewGuide.targetType && /(实习|日常|暑期|秋招|校招|全职)/.test(userMsg)) {
      if (/实习|日常|暑期/.test(userMsg)) interviewGuide.targetType = '实习'
      else if (/全职|秋招|校招/.test(userMsg)) interviewGuide.targetType = '全职'
    }

    // ✅ 立即显示加载状态（让用户感知到系统在处理）
    const loadingMsgId = `loading_${Date.now()}`
    const loadingMsg = {
      _id: loadingMsgId,
      role: 'ai',
      content: '面试官正在思考...',
      _isLoading: true
    }
    chatHistory.value.push(loadingMsg)
    aiThinkingMsgId.value = loadingMsgId
    interviewerState.value = 'talking'
    await nextTick()
    scrollChatToBottom()

    // ✅ 判断当前是否在引导环节
    let finalText = ''
    let tips = ''
    let tip = '' // 回答技巧轻提示（仅引导环节使用）
    let isTemplate = false
    let isGuide = false
    
    if (isGuidingPhase.value) {
      // ========== 引导环节：仅用于收集年级 & 意向岗位等基础信息 ==========
      if (useTemplateMode.value) {
        // 用户主动选择模板模式
        const templateRes = getGuideTemplateResponse(userMsg)
        finalText = templateRes.reply
        tip = templateRes.tip || ''
        isTemplate = true
        isGuide = true
      } else {
        // AI优先：8秒内尝试获取AI回复
        const aiResult = await callDeepSeekGuideWithFastTimeout(userMsg)
        
        if (aiResult) {
          // AI成功返回
          finalText = aiResult.reply
          tip = aiResult.tip || ''
        } else {
          // AI超时或失败，降级到模板
          const templateRes = getGuideTemplateResponse(userMsg)
          finalText = templateRes.reply
          tip = templateRes.tip || ''
          isTemplate = true
          isGuide = true
          finalText += '\n\n[模拟回复]'
        }
      }
      
      // 引导轮次计数（仅作兜底保护）
      guideRoundCount.value++

      // 引导完成条件：
      // 1）已成功识别出年级 & 岗位；或
      // 2）达到安全轮数上限
      const hasGrade = !!interviewGuide.grade
      const hasRole = !!(interviewGuide.targetRole || interviewGuide.templateRole)
      const shouldFinishGuide =
        (hasGrade && hasRole) ||
        guideRoundCount.value >= guideMaxRounds ||
        finalText.includes('开始正式的岗位面试')

      if (shouldFinishGuide) {
        isGuidingPhase.value = false
        guideRoundCount.value = 0
        interviewGuide.guideIndex = 0
      }
    } else {
      // ========== 正式面试环节：问题池 + AI 优先，模板兜底 ==========
      // 先从问题池中选择一个不重复、维度不同的问题，作为本轮核心问题
      const pickQuestionFromPool = () => {
        const usedIds = usedQuestionIds.value
        const usedDims = usedDimensions.value

        // 过滤掉已使用的问题，并优先选择“本轮尚未用过维度”的题目
        const unused = interviewQuestionPool.filter(q => !usedIds.has(q.id))
        if (!unused.length) return null

        const candidatesDiffDim = unused.filter(q => !usedDims.has(q.dimension))
        const candidates = candidatesDiffDim.length ? candidatesDiffDim : unused

        // 简单随机选一个
        const idx = Math.floor(Math.random() * candidates.length)
        return candidates[idx]
      }

      const nextQuestion = pickQuestionFromPool()

      // 如果问题池已经耗尽，则触发提前终止
      if (!nextQuestion) {
        isInterviewEnded.value = true
        if (!interviewEndTime.value) {
          interviewEndTime.value = Date.now()
        }
        chatHistory.value.push({
          role: 'ai',
          content: '本次模拟面试已完成核心问题考察，感谢你的认真作答～欢迎稍后再来练习其它方向或更多轮次的面试。',
          _isGuide: false,
          _isLoading: false,
          _isTemplate: false
        })
        chatSending.value = false
        await nextTick()
        scrollChatToBottom()
        return
      }

      // 标记问题已使用
      usedQuestionIds.value.add(nextQuestion.id)
      usedDimensions.value.add(nextQuestion.dimension)

      // 如果用户主动选择模板模式，直接使用模板为当前问题生成“折叠提示”（不内嵌在问题文本里）
      if (useTemplateMode.value) {
        let templateRes = getTemplateResponse(userMsg)
        finalText = nextQuestion.text
        tips = templateRes?.tips || _defaultInterviewTips(nextQuestion.text)
        isTemplate = true
        lastInterviewQuestionText.value = nextQuestion.text
      } else {
        // 检查本地缓存（高频问题）
        let cachedResponse = getCachedResponse(userMsg)
        
        if (cachedResponse) {
          // 使用缓存
          finalText = cachedResponse.content
          tips = cachedResponse.tips || ''
        } else {
          // ✅ AI优先：8秒内尝试获取AI回复
          const aiResult = await callDeepSeekWithFastTimeout(userMsg)
          
          if (aiResult) {
            // AI成功返回：让 AI 结合问题池中的问题生成更贴合的问题话术
            tips = aiResult.tips || ''

            let replyText = aiResult.reply || ''
            // 问题以池中问题为主，若 AI 也返回了 question，则只在非重复时附加
            let baseQuestionText = nextQuestion.text
            let extraQuestionText = aiResult.question || ''

            // 重复检测：如果 AI 给的 question 与上一次或当前问题文案重复，则忽略 AI 的 question
            if (extraQuestionText && (extraQuestionText === lastInterviewQuestionText.value || extraQuestionText === baseQuestionText)) {
              extraQuestionText = ''
            }

            let finalQuestionText = baseQuestionText
            if (extraQuestionText) {
              finalQuestionText = `${baseQuestionText}\n追问：${extraQuestionText}`
            }

            finalText = `${replyText}\n\n👉 ${finalQuestionText}`
            lastInterviewQuestionText.value = finalQuestionText

            if (jobsData.value.length > 0 && Math.random() > 0.5) { 
              const randomJob = jobsData.value[Math.floor(Math.random() * jobsData.value.length)]
              finalText += `\n\n💼 推荐：${randomJob['岗位']} - ${randomJob['平均薪资']}`
            }
            
            // 缓存高频问题的回答
            setCachedResponse(userMsg, { content: finalText, tips })
          } else {
            // AI超时或失败，降级到模板（问题文本不带提示，提示仅在下方折叠区展示）
            let templateRes = getTemplateResponse(userMsg)
            finalText = `${nextQuestion.text}\n\n[模拟回复]`
            tips = templateRes?.tips || _defaultInterviewTips(nextQuestion.text)
            isTemplate = true
            lastInterviewQuestionText.value = nextQuestion.text
          }
        }
      }
    }

    // ✅ 移除加载消息，添加真实回复（使用打字机效果）
    const loadingIndex = chatHistory.value.findIndex(m => m._id === loadingMsgId)
    if (loadingIndex > -1) {
      chatHistory.value.splice(loadingIndex, 1)
    }
    
    const aiMsgId = `ai_${Date.now()}`
    const aiMsg = {
      _id: aiMsgId,
      role: 'ai',
      content: '', // 初始为空，打字机效果会逐步填充
      tips: isGuide ? '' : tips, // 引导环节不使用tips，使用tip
      tip: isGuide ? tip : '', // 引导环节专用的回答技巧轻提示
      _isLoading: false,
      _isTemplate: isTemplate, // 标记是否为模板回复
      _isGuide: isGuide // 标记是否为引导环节
    }
    chatHistory.value.push(aiMsg)
    aiThinkingMsgId.value = null
    await nextTick()
    scrollChatToBottom()

    // ✅ 打字机效果（逐字显示，增强实时感）
    // 准备语音播报内容（去除模板提示标记）
    const speakContent = finalText.replace(/\n\n\[模拟回复\]/g, '').trim()
    typewriterEffect(aiMsgId, finalText, () => {
      // 打字完成后触发语音播报（不播报"[模拟回复]"提示）
      if (speakContent) speakText(speakContent)
      interviewerState.value = 'neutral'
    })

  } catch (e) {
    // 移除加载消息
    const loadingIndex = chatHistory.value.findIndex(m => m._id === aiThinkingMsgId.value)
    if (loadingIndex > -1) {
      chatHistory.value.splice(loadingIndex, 1)
    }
    aiThinkingMsgId.value = null
    interviewerState.value = 'neutral'
    
    chatHistory.value.push({ role: 'ai', content: '连接后端失败，请稍后重试' })
    ElMessage.error('网络连接失败')
  } finally {
    chatSending.value = false
  }
}

// --- 选择面试官性别 ---
const selectInterviewerGender = (gender) => {
  interviewerGender.value = gender
  localStorage.setItem('interviewer_gender', gender)
  genderSelectionVisible.value = false
  ElMessage.success(`已选择${gender === 'female' ? '女性' : '男性'}面试官`)
}

// --- 提前结束引导，开始正式面试 ---
const skipGuideAndStartInterview = () => {
  // 检查用户是否已选择岗位
  if (!interviewGuide.targetRole && !interviewGuide.templateRole) {
    ElMessage.warning('请先告诉我你想面试的岗位哦～')
    return
  }
  
  // 切换到正式面试环节
  isGuidingPhase.value = false
  guideRoundCount.value = 0
  interviewGuide.guideIndex = 0
  // 重置正式面试问题跟踪
  usedQuestionIds.value = new Set()
  usedDimensions.value = new Set()
  
  // 发送过渡消息
  const transitionText = '好的，我大概了解你的情况啦！那我们现在开始正式的岗位面试吧，问题会贴合你刚才说的信息，不用紧张，大胆回答就好～'
  chatHistory.value.push({
    role: 'ai',
    content: transitionText,
    _isGuide: false,
    _isLoading: false,
    _isTemplate: false
  })
  
  // 触发语音播报
  speakText(transitionText)
  nextTick(() => scrollChatToBottom())
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

// --- 面试终止功能 ---
const endInterview = () => {
  ElMessageBox.confirm(
    '确定要终止本次面试吗？终止后将无法继续对话，但可以生成面试分析报告。',
    '确认终止面试',
    {
      confirmButtonText: '确定终止',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(() => {
    isInterviewEnded.value = true
    // 记录终止时间
    if (!interviewEndTime.value) {
      interviewEndTime.value = Date.now()
    }
    // 清理本轮问题跟踪，避免下一次面试被上一次残留影响
    usedQuestionIds.value = new Set()
    usedDimensions.value = new Set()
    chatSending.value = false
    // 添加终止消息
    chatHistory.value.push({
      role: 'ai',
      content: '面试已终止。您可以点击下方按钮生成面试分析报告，查看详细评价和改进建议。',
      _isGuide: false,
      _isLoading: false,
      _isTemplate: false
    })
    ElMessage.success('面试已终止')
    nextTick(() => scrollChatToBottom())
  }).catch(() => {
    // 用户取消，不做任何操作
  })
}

// --- 元信息提取：面试方向 / 身份 / 时长 / 生成时间 ---
const buildInterviewMeta = (history) => {
  const allText = history.map(m => String(m.content || '')).join('\n')

  // 面试方向：优先使用已有结构化字段，其次从文本中粗略推断，最后给默认值
  let direction =
    interviewGuide.targetRole ||
    interviewGuide.templateRole ||
    (currentUser.value && currentUser.value.target_role) ||
    ''
  if (!direction) {
    if (/前端|前端工程师/i.test(allText)) direction = '前端相关岗位'
    else if (/算法|算法工程师/i.test(allText)) direction = '算法相关岗位'
    else if (/后端|Java|Python/i.test(allText)) direction = '后端/开发相关岗位'
    else direction = '专业相关岗位'
  }

  // 面试者身份：本科生 / 研究生（如均未明显出现则留空）
  let identity = ''
  const bachelorPattern = /(大一|大二|大三|大四|本科|本科学历)/
  const masterPattern = /(研一|研二|研三|研究生|硕士|博士)/
  const isBachelor = bachelorPattern.test(allText)
  const isMaster = masterPattern.test(allText)
  if (isMaster) {
    identity = '研究生'
  } else if (isBachelor) {
    identity = '本科生'
  } else {
    identity = ''
  }

  // 面试时长：从开始/结束时间计算，至少 1 分钟
  let durationMinutes = 0
  if (interviewStartTime.value) {
    const endTs = interviewEndTime.value || Date.now()
    const diff = endTs - interviewStartTime.value
    if (diff > 0) {
      durationMinutes = Math.max(1, Math.round(diff / 60000))
    }
  }

  // 报告生成时间
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const generatedAt = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`

  return {
    direction,
    identity,
    durationMinutes,
    generatedAt
  }
}

// --- 通用面试分析模板（降级模式，自动填充大学生场景） ---
const buildFallbackInterviewReport = (history) => {
  const meta = buildInterviewMeta(history)
  const userAnswers = history
    .filter(m => m.role === 'user')
    .map((m, idx) => ({
      index: idx + 1,
      content: String(m.content || '').trim()
    }))

  const answersMd = userAnswers.length
    ? userAnswers.map(a => `### 题目 ${a.index} · 回答表现\n\n- 用户原始回答：\n\n${a.content || '（无内容）'}\n\n- 逻辑性：整体结构基本清晰，可进一步使用「总—分—总」或 STAR 结构强化层次感。\n- 内容完整性：建议补充更具体的课程/项目/实践细节，以及可量化的结果。\n- 表达清晰度：表达大体清楚，如能适当分点、控制语速，会更利于面试官理解。\n- 针对性：可更多结合目标岗位/方向的核心能力要求来组织回答。\n`).join('\n')
    : '当前对话记录中没有检测到清晰的回答内容。建议下次面试时使用完整句子作答，并尽量围绕“是什么 / 为什么 / 怎么做 / 结果如何”来组织回答。\n'

  const standardMd = userAnswers.length
    ? userAnswers.map(a => `### 题目 ${a.index} · 参考作答结构（大学生通用）\n\n- 开场结论：先用 1–2 句话给出核心观点或结果。\n- 背景（Situation）：交代时间、场景、身份（如大几/研究生阶段）、任务目标。\n- 任务（Task）：说明你在这件事中的具体职责或要解决的问题。\n- 行动（Action）：分点描述你做了哪些关键动作、做出过哪些权衡或思考。\n- 结果（Result）：用数据或具体变化说明效果，可以补充个人收获与反思。\n`).join('\n')
    : '你可以为常见高频题（如自我介绍、项目经历、实习经历、失败经历、优缺点等）分别准备一套 STAR 结构的回答草稿，在面试前多次演练。\n'

  const isBachelor = meta.identity === '本科生'
  const isMaster = meta.identity === '研究生'

  return [
    '# 大学生模拟面试分析报告（通用模板）',
    '',
    '> 由于当前网络或服务异常，本报告基于通用模板自动生成，并已尽可能结合本次对话内容进行填充，供你进行自我复盘。',
    '',
    '---',
    '',
    '## 一、基本信息',
    '',
    `- 面试方向：${meta.direction || '专业相关岗位'}`,
    `- 面试时长：${meta.durationMinutes ? meta.durationMinutes + ' 分钟' : '未统计（建议下次完整体验一次流程）'}`,
    `- 面试者身份：${isBachelor ? '☑ 本科生' : '☐ 本科生'} / ${isMaster ? '☑ 研究生' : '☐ 研究生'}（如均未勾选，说明在对话中未明确提及）`,
    `- 报告生成时间：${meta.generatedAt}`,
    '',
    '---',
    '',
    '## 二、回答质量概览（通用分析）',
    '',
    answersMd,
    '',
    '---',
    '',
    '## 三、通用参考作答模板（结构示例）',
    '',
    standardMd,
    '',
    '---',
    '',
    '## 四、综合评分与通用建议（示例）',
    '',
    '- 综合得分（示例）：**75 / 100**（该分数主要用于帮助你感受大致区间，实际水平请结合自身情况与多次面试体验综合判断）；',
    '- 逻辑表达：建议在回答重要问题时，先给结论再展开分点说明，避免信息堆叠在一个长句中；',
    '- 内容充实度：可以从课程作业、课程设计、科研/项目实践、学生工作等角度挖掘更多具体素材；',
    '- 岗位匹配度：建议结合目标岗位 JD 总结 3–5 个关键能力点，并逐一准备对应的案例。',
    '',
    '**后续练习建议：**',
    '',
    '- 选取 3–5 个你最有代表性的项目/经历，按照 STAR 结构写成完整回答稿，多次朗读与演练；',
    '- 针对目标方向（如前端/算法/研究生科研方向），整理至少 10 个高频面试题，并为每个问题准备 1 套主回答 + 1 套补充回答；',
    '- 建议与同学或学长学姐安排 1–2 次线下或线上模拟面试，从第三方视角获得更加具体的反馈。'
  ].join('\n')
}

// --- 生成面试分析报告 ---
const generateInterviewReport = async () => {
  if (interviewReportLoading.value) return
  
  if (!isInterviewEnded.value) {
    ElMessage.warning('请先终止面试后再生成报告')
    return
  }
  
  if (chatHistory.value.length <= 1) {
    ElMessage.warning('对话记录为空，无法生成报告')
    return
  }
  
  interviewReportLoading.value = true
  ElMessage.closeAll()
  ElMessage.info('正在生成个性化面试分析报告，请稍候...')
  
  // 记录报告生成开始时间：优先使用面试真实开始时间，否则使用当前时间（用于计算 API 请求耗时）
  const startedAt = interviewStartTime.value || Date.now()
  
  try {
    const targetRole = currentUser.value?.target_role || interviewGuide.targetRole || interviewGuide.templateRole || '未指定'
    const meta = buildInterviewMeta(chatHistory.value)
    
    const res = await axios.post(
      `${API_BASE}/api/generate-interview-report`,
      {
        chat_history: chatHistory.value,
        target_role: targetRole,
        meta
      },
      {
        timeout: 10000 // 10 秒超时，超时进入降级模式
      }
    )

    const elapsed = Date.now() - startedAt
    console.debug('[InterviewReport] API 响应状态：', {
      status: res.status,
      elapsedMs: elapsed,
      success: res.data?.success
    })
    console.debug('[InterviewReport] API 响应数据：', res.data)

    if (res.data?.success && res.data.markdown) {
      interviewReportMarkdown.value = res.data.markdown
      ElMessage.closeAll()
      ElMessage.success('报告生成成功！')
      return
    }

    console.warn('[InterviewReport] DeepSeek 返回非成功状态：', res.data)

    // 开启 “不降级” 开关时，直接提示错误，不切换到通用模板（方便开发/测试验证）
    if (INTERVIEW_REPORT_NO_FALLBACK) {
      ElMessage.error('报告生成失败（已关闭降级模式，请检查控制台日志）')
      return
    }

    // 未成功返回，走降级模板
    interviewReportMarkdown.value = buildFallbackInterviewReport(chatHistory.value)
    ElMessage.closeAll()
    ElMessage.warning('网络问题，无法生成个性化报告，已为您生成适配本次面试的通用模板报告')
  } catch (e) {
    // startedAt 已在 try 块之前定义，直接使用即可
    const elapsed = Date.now() - startedAt
    const status = e?.response?.status
    console.error('[InterviewReport] 调用 DeepSeek 失败：', {
      status,
      elapsedMs: elapsed,
      error: e
    })

    if (INTERVIEW_REPORT_NO_FALLBACK) {
      ElMessage.error('报告生成失败（已关闭降级模式，请检查控制台日志）')
      return
    }

    // 任何异常都切换到通用模板，避免用户侧体验中断
    interviewReportMarkdown.value = buildFallbackInterviewReport(chatHistory.value)
    ElMessage.closeAll()
    ElMessage.warning('网络问题，无法生成个性化报告，已为您生成适配本次面试的通用模板报告')
  } finally {
    interviewReportLoading.value = false
  }
}

// --- 下载面试报告 ---
const downloadInterviewReport = () => {
  if (!interviewReportMarkdown.value) {
    ElMessage.warning('请先生成报告')
    return
  }
  
  const blob = new Blob([interviewReportMarkdown.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  link.href = url
  link.download = `面试分析报告_${timestamp}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('报告下载成功')
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

// 竞争力沙盘：AI 自动量化（允许自然语言自由输入；不做格式校验）
const _clamp100 = (n) => Math.max(0, Math.min(100, n))
const _toFiniteNumber = (v, fallback) => {
  const n = typeof v === 'number' ? v : parseFloat(String(v ?? '').trim())
  return Number.isFinite(n) ? n : fallback
}
const _extractJsonObject = (text) => {
  if (!text) return null
  const s = String(text)
  // 先取 ```json ... ``` 包裹内容
  const fenced = s.match(/```json\s*([\s\S]*?)\s*```/i)
  if (fenced && fenced[1]) {
    try { return JSON.parse(fenced[1]) } catch (_) {}
  }
  // 再尝试抓取第一个 JSON 对象
  const obj = s.match(/\{[\s\S]*\}/)
  if (obj && obj[0]) {
    try { return JSON.parse(obj[0]) } catch (_) {}
  }
  return null
}

/**
 * 调用项目现有 AI 接口（沿用 axios + API_BASE）对自然语言进行量化。
 * 约束：不改后端/不引入新依赖，因此复用后端已存在的 `/api/analyze-experiment`（返回 markdown）。
 * 做法：让 AI 在 markdown 文本中包含一个可解析的 JSON 对象，我们从返回文本中提取并更新雷达图。
 */
const aiQuantizeSandboxInputs = async () => {
  const nl = {
    gpa: sandboxForm.gpa,
    project: sandboxForm.project,
    intern: sandboxForm.intern,
    competition: sandboxForm.competition,
    english: sandboxForm.english,
    leader: sandboxForm.leader,
  }

  const instruction = `
你现在的任务是：把“个人竞争力沙盘”的 6 项自然语言描述量化到 0-100 分，并返回 JSON。

【输出要求：必须包含且仅包含一个 JSON 对象（可以放在 Markdown 中，但 JSON 必须完整可解析）】
{
  "scores": {
    "gpa": 0-100,
    "project": 0-100,
    "intern": 0-100,
    "competition": 0-100,
    "english": 0-100,
    "leader": 0-100
  },
  "reasoning": "用 3-6 句话解释量化依据（可选）"
}

【量化规则提示】
- 允许缺失：若用户写“无/没有/暂未”，给 10-30 的合理分
- 若描述很强（名企实习、国奖、顶会论文等），给 80-100
- 若描述一般（校级奖/普通项目），给 50-75
- GPA：3.8/4.0 大约 90-98；3.0/4.0 大约 70-80；2.5/4.0 大约 55-70
`

  // 复用现有 AI 调用方式：走后端 analyze-experiment（返回 markdown 文本）
  const res = await axios.post(`${API_BASE}/api/analyze-experiment`, {
    career: '个人竞争力沙盘量化',
    answers: {
      instruction,
      inputs: nl
    }
  })

  const markdown = res?.data?.markdown || ''
  const parsed = _extractJsonObject(markdown)
  const scores = parsed?.scores || {}

  // 即使 AI 未返回可解析 JSON，也要保证功能可用：做温和兜底（保持原值，不弹“格式不正确”）
  const next = {
    gpa: _clamp100(_toFiniteNumber(scores.gpa, radarValues.gpa)),
    project: _clamp100(_toFiniteNumber(scores.project, radarValues.project)),
    intern: _clamp100(_toFiniteNumber(scores.intern, radarValues.intern)),
    competition: _clamp100(_toFiniteNumber(scores.competition, radarValues.competition)),
    english: _clamp100(_toFiniteNumber(scores.english, radarValues.english)),
    leader: _clamp100(_toFiniteNumber(scores.leader, radarValues.leader)),
  }

  return { markdown, next }
}

// 点击「生成雷达图」：调用 AI 自动量化 -> 写回 radarValues -> 触发原有 watch/raf 渲染（雷达图视觉不变）
const generateSandboxRadar = async () => {
  try {
    const { next } = await aiQuantizeSandboxInputs()
    radarValues.gpa = next.gpa
    radarValues.project = next.project
    radarValues.intern = next.intern
    radarValues.competition = next.competition
    radarValues.english = next.english
    radarValues.leader = next.leader
    ElMessage.success('雷达图已更新')
  } catch (e) {
    console.error(e)
    // 不再提示“格式不正确”，仅提示服务不可用；并保持旧雷达值不变
    ElMessage.error('量化失败：请确认后端服务与 AI 接口可用')
  }
}

// 点击「生成AI分析报告」：复用项目现有 API_BASE + axios 调用方式，调用后端已有的 /api/analyze-experiment（返回 Markdown）
const generateSandboxAiReport = async () => {
  sandboxReportLoading.value = true
  sandboxReportMarkdown.value = ''
  try {
    const payload = {
      // 原始输入（便于 AI 理解）
      'GPA（绩点）': sandboxForm.gpa,
      '项目实战经验': sandboxForm.project,
      '名企实习经历': sandboxForm.intern,
      '竞赛获奖情况': sandboxForm.competition,
      '英语学术能力': sandboxForm.english,
      '领导力与协作': sandboxForm.leader,
      // 量化后的雷达数据（用于分析）
      '雷达图量化数据(0-100)': {
        gpa: radarValues.gpa,
        project: radarValues.project,
        intern: radarValues.intern,
        competition: radarValues.competition,
        english: radarValues.english,
        leader: radarValues.leader,
      }
    }

    const res = await axios.post(`${API_BASE}/api/analyze-experiment`, {
      answers: payload,
      career: '个人竞争力沙盘分析'
    })

    sandboxReportMarkdown.value = res?.data?.markdown || ''
    if (!sandboxReportMarkdown.value) ElMessage.warning('AI 未返回报告内容，请稍后重试')
    else ElMessage.success('AI 分析报告已生成')
  } catch (e) {
    console.error(e)
    ElMessage.error('生成失败：请确认后端服务已启动且 AI 接口可用')
  } finally {
    sandboxReportLoading.value = false
  }
}

const downloadSandboxReport = () => {
  if (!sandboxReportMarkdown.value) return ElMessage.warning('暂无报告可下载')
  const blob = new Blob([sandboxReportMarkdown.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '个人竞争力分析报告.md'
  a.click()
  URL.revokeObjectURL(url)
}

// ==========================================
// 6. 生命周期 & 辅助 (Lifecycle)
// ==========================================
const handleSelect = (key) => {
  activeMenu.value = key
  if (key === '3') nextTick(() => initSandboxChart())
  if (key === '1') nextTick(() => initResumeRadar())
  if (key === '7') router.push('/virtual-experiment')
  // 模拟面试：进入页面时初始化引导环节状态
  if (key === '2') {
    // 如果聊天历史只有初始消息，重置引导环节状态并显示性别选择
    if (chatHistory.value && chatHistory.value.length === 1 && chatHistory.value[0].content === '你好，我是AI模拟面试官😊') {
      isGuidingPhase.value = true
      guideRoundCount.value = 0
      interviewGuide.guideIndex = 0
      genderSelectionVisible.value = true
    }
  }
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
  
  // 检查是否有自动导航标记（从一键登录链接或二维码进入）
  const autoNavigate = localStorage.getItem('activeMenu')
  if (autoNavigate) {
    activeMenu.value = autoNavigate
    localStorage.removeItem('activeMenu')
    // 如果是模拟面试，确保初始化
    if (autoNavigate === '2') {
      nextTick(() => {
        // 模拟面试相关初始化已在 handleSelect 中处理
      })
    }
  }
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
        <!-- 退出登录按钮（用户端） -->
        <el-button
          type="link"
          size="small"
          @click="handleLogout"
          class="logout-button"
          style="color: rgba(255,255,255,0.7); margin-top: 8px; width: 100%;"
        >
          <el-icon style="margin-right: 4px; color: rgba(255,255,255,0.7)">
            <ArrowRight />
          </el-icon>
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

            <!-- 面试官性别选择（引导环节开始时显示） -->
            <div v-if="genderSelectionVisible && isGuidingPhase && chatHistory.length <= 1" class="gender-selection-area">
              <div class="gender-selection-title">请选择面试官性别</div>
              <div class="gender-selection-buttons">
                <el-button 
                  :type="interviewerGender === 'female' ? 'primary' : 'default'"
                  :plain="interviewerGender !== 'female'"
                  @click="selectInterviewerGender('female')"
                  class="gender-button"
                >
                  👩 女性面试官
                </el-button>
                <el-button 
                  :type="interviewerGender === 'male' ? 'primary' : 'default'"
                  :plain="interviewerGender !== 'male'"
                  @click="selectInterviewerGender('male')"
                  class="gender-button"
                >
                  👨 男性面试官
                </el-button>
              </div>
            </div>

            <!-- 数字人展示区 -->
            <div class="digital-human-section">
              <DigitalHuman :isTalking="interviewerState === 'talking'" :gender="interviewerGender" />
            </div>

            <div class="chat-shell">
              <div class="chat-window chat-window-el">
                <div v-for="(msg, i) in chatHistory" :key="i" class="msg-row" :class="msg.role">
                  <div class="avatar" v-if="msg.role === 'ai'">
                    <el-avatar :size="36" class="avatar-ai">AI</el-avatar>
                  </div>
                  <div class="bubble">
  <div class="bubble-name">{{ msg.role === 'ai' ? 'AI 面试官' : '我' }}</div>
  <div class="bubble-text" :class="{ 'thinking-text': msg._isLoading, 'template-text': msg._isTemplate }">
    {{ msg.content }}
    <span v-if="msg._isLoading" class="thinking-dots">
      <span>.</span><span>.</span><span>.</span>
    </span>
  </div>

  <!-- 新增：回答技巧轻提示（仅引导环节显示，不语音播报） -->
  <div v-if="msg.role === 'ai' && msg._isGuide && msg.tip" class="guide-tip-box">
    <div class="guide-tip-content">
      <el-icon class="guide-tip-icon"><InfoFilled /></el-icon>
      <span>{{ msg.tip }}</span>
    </div>
  </div>

  <!-- 新增：话术建议与逻辑拆解（仅正式面试显示，不语音播报） -->
  <div v-if="msg.role === 'ai' && !msg._isGuide && msg.tips" style="margin-top: 10px;">
    <el-collapse accordion>
      <el-collapse-item title="话术建议与逻辑拆解（点击展开）" name="tips">
        <div style="white-space: pre-wrap; color: rgba(15,23,42,0.72); line-height: 1.7;">
          {{ msg.tips }}
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>

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
                <!-- 新增：提前结束引导，开始正式面试按钮（仅引导环节显示） -->
                <div v-if="isGuidingPhase && !isInterviewEnded" style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                  <el-button 
                    type="primary" 
                    plain
                    @click="skipGuideAndStartInterview"
                    class="skip-guide-button"
                  >
                    ⚡ 提前结束引导，开始正式面试
                  </el-button>
                </div>
                
                <!-- 新增：面试终止按钮（面试进行中显示） -->
                <div v-if="!isGuidingPhase && !isInterviewEnded" style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                  <el-button 
                    type="danger" 
                    plain
                    @click="endInterview"
                    class="end-interview-button"
                  >
                    ⛔ 终止面试
                  </el-button>
                </div>
                
                <!-- 新增：使用模拟模式开关（可选功能） -->
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 12px; color: rgba(15,23,42,0.65);">
                  <el-switch
                    v-model="useTemplateMode"
                    size="small"
                    active-text="使用模拟模式"
                    inactive-text="AI优先模式"
                    style="--el-switch-on-color: #409EFF;"
                  />
                  <span v-if="useTemplateMode" style="color: rgba(64,158,255,0.85);">当前：模板对话模式</span>
                </div>
                
                <div class="input-row">
                  <el-input
                    v-model="chatInput"
                    placeholder="输入你的回答…（Enter 发送）"
                    @keyup.enter="sendMessage"
                    size="large"
                    class="full-width-input"
                    :disabled="isInterviewEnded"
                  >
                    <template #prepend>
                      <div class="voice-control">
                        <el-button 
                          @click="toggleVoiceInput"
                          :class="{ 'recording-active': isRecording }"
                          :title="isRecording ? '点击停止' : '点击说话'"
                        >
                          <el-icon :class="{ 'mic-pulse': isRecording }" :size="20">
                            <Microphone />
                          </el-icon>
                        </el-button>
                        <div class="voice-status">
                          <span class="voice-lang-toggle" @click="voiceLang = voiceLang === 'zh-CN' ? 'en-US' : 'zh-CN'">
                            {{ voiceLang === 'zh-CN' ? '中文' : 'EN' }}
                          </span>
                          <span v-if="isRecording" class="voice-timer">
                            · {{ voiceSeconds }}s
                          </span>
                        </div>
                      </div>
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

                <div class="agent-action">
                  <el-button 
                    v-if="!isInterviewEnded"
                    type="success" 
                    :loading="agentCalling" 
                    @click="callAgent" 
                    class="agent-button"
                  >
                    ⚡ 召唤 Agent 智能推荐
                  </el-button>
                  
                  <!-- 新增：面试报告生成按钮（面试终止后显示） -->
                  <div v-if="isInterviewEnded" style="display: flex; flex-direction: column; gap: 12px; width: 100%; max-width: 400px;">
                    <el-button 
                      type="primary" 
                      :loading="interviewReportLoading" 
                      @click="generateInterviewReport" 
                      class="report-button"
                    >
                      📊 生成面试分析报告
                    </el-button>
                    
                    <!-- 报告下载按钮（报告生成后显示） -->
                    <el-button 
                      v-if="interviewReportMarkdown"
                      type="success" 
                      @click="downloadInterviewReport" 
                      class="download-button"
                    >
                      💾 下载报告
                    </el-button>
                  </div>
                </div>
                
                <!-- 新增：面试报告显示区域 -->
                <div v-if="interviewReportMarkdown" class="report-display-area">
                  <div class="report-header">
                    <h3>📄 面试分析报告</h3>
                  </div>
                  <div class="report-content" v-html="md.render(interviewReportMarkdown)"></div>
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
                  <!-- 输入区域改造：移除滑块，替换为表单输入（布局位置保持不变） -->
                  <div class="slider-item">
                    <span>GPA（绩点）</span>
                    <el-input v-model="sandboxForm.gpa" placeholder="示例：3.6（0-4）或 85（0-100）" />
                  </div>
                  <div class="slider-item">
                    <span>项目实战经验</span>
                    <el-input v-model="sandboxForm.project" placeholder="示例：8（0-10）或 80（0-100）/ 或简述关键项目" />
                  </div>
                  <div class="slider-item">
                    <span>名企实习经历</span>
                    <el-input v-model="sandboxForm.intern" placeholder="示例：2（段）或 70（0-100）/ 或简述公司与岗位" />
                  </div>
                  <div class="slider-item">
                    <span>竞赛获奖情况</span>
                    <el-input v-model="sandboxForm.competition" placeholder="示例：省二/国奖/Top% 或 75（0-100）" />
                  </div>
                  <div class="slider-item">
                    <span>英语学术能力</span>
                    <el-input v-model="sandboxForm.english" placeholder="示例：六级 520/雅思 7/论文海报 或 85（0-100）" />
                  </div>
                  <div class="slider-item">
                    <span>领导力与协作</span>
                    <el-input v-model="sandboxForm.leader" placeholder="示例：社团干部/组长经历 或 80（0-100）" />
                  </div>

                  <div class="card-actions" style="justify-content: flex-start;">
                    <el-button type="primary" @click="generateSandboxRadar">
                      生成雷达图
                    </el-button>
                  </div>
                </div>
              </el-col>
  
              <el-col :span="16">
                <div class="glass-card chart-wrap">
                  <div class="chart-title">ECharts · Radar (Smooth Update)</div>
                  <div class="chart-container" ref="sandboxChartRef"></div>

                  <!-- AI 分析（按钮样式与左侧一致，布局紧贴雷达图下方） -->
                  <div class="card-actions" style="justify-content: flex-start; gap: 10px;">
                    <el-button type="primary" :loading="sandboxReportLoading" @click="generateSandboxAiReport">
                      {{ sandboxReportLoading ? '生成中...' : '生成AI分析报告' }}
                    </el-button>
                  </div>

                  <!-- 报告展示与下载（Markdown 渲染风格复用现有 markdown-body） -->
                  <el-divider />
                  <div class="glass-card report-card" style="padding: 14px; margin-top: 0;">
                    <div class="card-title" style="margin-bottom: 10px; justify-content: space-between;">
                      <span>📄 AI 分析报告（Markdown）</span>
                      <el-button type="success" plain :disabled="!sandboxReportMarkdown" @click="downloadSandboxReport">
                        下载报告
                      </el-button>
                    </div>

                    <div v-if="sandboxReportMarkdown" class="markdown-body" v-html="sandboxReportHtml"></div>
                    <div v-else class="empty-hint">
                      提示：请先填写左侧 6 项信息并点击「生成AI分析报告」。
                    </div>
                  </div>
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
    overflow-y: auto;   /* 允许整体区域滚动，报告较长时不被裁剪 */
    overflow-x: hidden;
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
  /* 性别选择区域样式 */
  .gender-selection-area {
    margin-bottom: 20px;
    padding: 20px;
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    border: 1px solid rgba(15,23,42,0.08);
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    text-align: center;
  }
  .gender-selection-title {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 16px;
  }
  .gender-selection-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    align-items: center;
  }
  .gender-button {
    min-width: 160px;
    height: 44px;
    font-weight: 600;
    font-size: 14px;
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  .gender-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64,158,255,0.3);
  }
  .input-row {
    margin-bottom: 10px;
  }
  /* 提前结束引导按钮样式 */
  .skip-guide-button {
    background: linear-gradient(135deg, rgba(64,158,255,0.95), rgba(64,158,255,0.75));
    color: #fff;
    border: 1px solid rgba(64,158,255,0.40);
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 20px;
    transition: all 0.3s ease;
  }
  .skip-guide-button:hover {
    background: linear-gradient(135deg, rgba(64,158,255,1), rgba(64,158,255,0.85));
    filter: brightness(1.1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64,158,255,0.3);
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
  .voice-control {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .voice-status {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: rgba(15,23,42,0.65);
  }
  .voice-lang-toggle {
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 10px;
    background: rgba(64,158,255,0.08);
    border: 1px solid rgba(64,158,255,0.28);
    color: rgba(37,99,235,0.9);
    font-weight: 500;
    transition: all 0.2s ease;
  }
  .voice-lang-toggle:hover {
    background: rgba(64,158,255,0.16);
    box-shadow: 0 0 0 1px rgba(64,158,255,0.12);
  }
  .voice-timer {
    color: rgba(15,23,42,0.55);
  }

  /* 侧边栏退出按钮样式：背景透明，与深蓝侧边栏融为一体 */
  .logout-button {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-left: 0;
    padding-right: 0;
  }
  .logout-button :deep(.el-button__inner) {
    background-color: transparent;
  }
  .logout-button:hover {
    background-color: transparent !important;
    color: #ffffff !important;
  }
  /* 面试终止按钮样式 */
  .end-interview-button {
    background: linear-gradient(135deg, rgba(245,108,108,0.95), rgba(245,108,108,0.75));
    color: #fff;
    border: 1px solid rgba(245,108,108,0.40);
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 20px;
    transition: all 0.3s ease;
  }
  .end-interview-button:hover {
    background: linear-gradient(135deg, rgba(245,108,108,1), rgba(245,108,108,0.85));
    filter: brightness(1.1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245,108,108,0.3);
  }
  /* 报告生成按钮样式 */
  .report-button {
    width: 100%;
    max-width: 400px;
    height: 40px;
    font-weight: 600;
    font-size: 14px;
    background: linear-gradient(135deg, rgba(64,158,255,0.95), rgba(64,158,255,0.75));
    border: 1px solid rgba(64,158,255,0.40);
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  .report-button:hover {
    background: linear-gradient(135deg, rgba(64,158,255,1), rgba(64,158,255,0.85));
    filter: brightness(1.1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64,158,255,0.3);
  }
  /* 下载按钮样式 */
  .download-button {
    width: 100%;
    max-width: 400px;
    height: 40px;
    font-weight: 600;
    font-size: 14px;
    background: linear-gradient(135deg, #67C23A, #85CE61);
    border: 1px solid #85CE61;
    border-radius: 8px;
    transition: all 0.3s ease;
  }
  .download-button:hover {
    background: linear-gradient(135deg, #85CE61, #67C23A);
    filter: brightness(1.1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(103,194,58,0.3);
  }
  /* 报告显示区域样式 */
  .report-display-area {
    margin-top: 20px;
    padding: 20px;
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    border: 1px solid rgba(15,23,42,0.08);
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }
  .report-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(64,158,255,0.2);
  }
  .report-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
  }
  .report-content {
    line-height: 1.8;
    color: #0f172a;
  }
  .report-content :deep(h1),
  .report-content :deep(h2),
  .report-content :deep(h3) {
    margin-top: 24px;
    margin-bottom: 12px;
    font-weight: 700;
    color: #0f172a;
  }
  .report-content :deep(h1) { font-size: 24px; }
  .report-content :deep(h2) { font-size: 20px; }
  .report-content :deep(h3) { font-size: 18px; }
  .report-content :deep(p) {
    margin-bottom: 12px;
    color: rgba(15,23,42,0.85);
  }
  .report-content :deep(ul),
  .report-content :deep(ol) {
    margin-bottom: 12px;
    padding-left: 24px;
  }
  .report-content :deep(li) {
    margin-bottom: 8px;
    color: rgba(15,23,42,0.85);
  }
  .report-content :deep(strong) {
    color: #0f172a;
    font-weight: 700;
  }
  .report-content :deep(code) {
    background: rgba(15,23,42,0.06);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
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
  .thinking-text { color: rgba(64,158,255,0.85); font-style: italic; }
  .thinking-dots { display: inline-block; margin-left: 4px; }
  .thinking-dots span {
    display: inline-block;
    animation: thinking-dot 1.4s infinite;
    animation-delay: 0s;
  }
  .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
  .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes thinking-dot {
    0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
    30% { opacity: 1; transform: translateY(-4px); }
  }
  .template-text { position: relative; }
  .template-text::after {
    content: '';
    display: block;
    margin-top: 4px;
    font-size: 11px;
    color: rgba(15,23,42,0.45);
  }
  /* 回答技巧轻提示样式（引导环节专用） */
  .guide-tip-box {
    margin-top: 10px;
    padding: 8px 12px;
    background: rgba(64,158,255,0.08);
    border-left: 3px solid rgba(64,158,255,0.35);
    border-radius: 6px;
    font-size: 12px;
    line-height: 1.6;
    color: rgba(15,23,42,0.75);
  }
  .guide-tip-content {
    display: flex;
    align-items: flex-start;
    gap: 6px;
  }
  .guide-tip-icon {
    color: #409EFF;
    font-size: 14px;
    margin-top: 2px;
    flex-shrink: 0;
  }
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