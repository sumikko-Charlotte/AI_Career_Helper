<script setup>
  // -----------------------------
  // 中文注释：组件顶部导入与全局常量
  // 该文件为单文件组件（SFC），包含四个核心功能模块：
  // 1) AI 简历医生  2) 模拟面试  3) 竞争力雷达（沙盘）  4) 生涯路径规划
  // 为便于新手开发者阅读，我将按模块分组变量/方法，并在每个模块前添加注释。
  // -----------------------------
  import { ref, reactive, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
// 1. 引入 ECharts
import * as echarts from 'echarts' 
import { ElMessage } from 'element-plus'
// 2. 引入所有用到的图标 (补全了 Trophy, Loading 等)
import { 
  Monitor, ChatDotRound, DocumentChecked, User, Odometer, MagicStick, 
  Calendar, SwitchButton, CircleCheck, Reading, Trophy, Loading, Compass, Aim
} from '@element-plus/icons-vue'

// 引入组
import Login from './components/Login.vue'
import ResumeDoctor from './components/ResumeDoctor.vue'
import DigitalHuman from './components/DigitalHuman.vue'
 
  // 后端基础地址
  const API_BASE = 'http://127.0.0.1:8000'

  // 用户登录状态
  const currentUser = ref(null)
  
  // -----------------------------
  // 菜单与页面状态
  // activeMenu: 控制左侧菜单与主区展示（'0' ~ '3'）
  // -----------------------------
  const activeMenu = ref('0')
  
  // -----------------------------
  // 生涯路径规划（Career Roadmap） 状态
  // roadmapGrade / roadmapRole: 用户选择的年级与目标方向
  // roadmapLoading: 请求中状态
  // roadmapData: 后端返回的时间轴数据数组
  // -----------------------------
  const roadmapGrade = ref('大一')
  const roadmapRole = ref('算法')
  const roadmapLoading = ref(false)
  const roadmapData = ref([])
  const roadmapRadar = ref(null) // 存放雷达图数据
const roadmapComment = ref('') // AI 寄语
const radarChartRef = ref(null) // DOM 引用
  const roadmapScore = ref(0)
const roadmapSkills = ref([])
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]
  
  // --- 👇 修改部分：更丰富的选项数据 ---

// 1. 年级选项 (扩充了研究生)
const gradeOptions = [
  '大一', '大二', '大三', '大四',
  '研一', '研二', '研三', '博士'
]

// 2. 岗位方向 (按 CSV 数据进行了分组整理)
// --- 👇 替换原有的 roleOptions 变量 ---
const roleOptions = [
  {
    label: '互联网/AI',
    options: ['互联网', '电子商务', '计算机软件', '生活服务', '企业服务', '医疗健康', '游戏', '社交网络与媒体', '人工智能', '云计算', '在线教育', '计算机服务', '大数据', '广告营销', '物联网新零售', '信息安全']
  },
  {
    label: '电子/通信/半导体',
    options: ['半导体', '电子', '通信', '智能硬件', '运营商', '计算机硬件', '硬件开发', '芯片', '集成电路', '消费电子', '网路设备', '增值服务']
  },
  {
    label: '金融',
    options: ['互联网金融', '银行', '投资', '融资', '证券', '期货基金', '保险', '租赁', '拍卖', '典当', '担保信托', '财富管理']
  },
  {
    label: '专业服务',
    options: ['咨询财务', '审计', '税务', '人力资源服务', '法律检测', '知识产权', '翻译']
  },
  {
    label: '制造业',
    options: ['电器器械', '金属制品', '非金属矿物制品', '橡胶塑料制品', '化学原料', '化学制品', '仪器仪表', '自动化设备', '印刷', '包装', '造纸', '铁路', '船舶', '航空航天材料', '电子设备', '新材料', '机械设备', '重工', '工业自动化', '原材料加工', '摸具']
  },
  {
    label: '房地产/建筑',
    options: ['装修装饰', '建筑工程', '土木工程', '机电工程', '物业管理', '房地产中介', '租赁', '建筑材料', '房地产开发经营', '建筑设计', '建筑工程咨询服务', '土地与公共设施管理', '工程施工']
  },
  {
    label: '交通运输/物流',
    options: ['即时配送', '快递', '公路', '物流', '同城货运', '跨境物流', '装卸搬运', '仓储业', '客运服务', '铁路', '机场']
  },
  {
    label: '制药/医疗',
    options: ['医疗服务', '医美服务', '医疗器械', 'IVD生物', '制药', '药物批发', '医疗研发外包']
  },
  {
    label: '消费品/批发/零售',
    options: ['批发', '零食进出口贸易', '食品/饮料/烟酒', '服装', '纺织', '家具', '家电', '珠宝首饰']
  },
  {
    label: '广告/传媒/文化/体育',
    options: ['文化艺术', '娱乐体育', '广告', '公关', '会展', '广播', '影视新闻', '出版社']
  },
  {
    label: '教育培训',
    options: ['辅导机构', '职业培训', '学前教育学校', '学历教育', '学士研究']
  },
  {
    label: '服务业',
    options: ['餐饮', '休闲', '娱乐运动', '健身保健', '养生', '景区', '摄影', '美容', '美发', '宠物服务', '婚庆', '家政服务', '旅游', '酒店']
  },
  {
    label: '汽车',
    options: ['新能源汽车', '汽车智能网联', '汽车经销商', '汽车后市场', '汽车研发', '制造汽车零件', '摩托车/自行车之制造', '4S店']
  },
  {
    label: '能源/化工/环保',
    options: ['光伏', '储能', '电池', '风电', '新能源环保', '电力', '热力', '水利', '石油', '石化', '矿产', '地质采掘', '冶炼']
  },
  {
    label: '政府/非盈利机构/其他',
    options: ['公共事业', '农业', '林业', '牧业', '渔业', '政府']
  }
]
  
  // -----------------------------
  // AI 简历医生模块
  // 说明：
  // - `resumeText`：绑定用户输入的简历文本
  // - `resumeResult`：后端返回的诊断结构化结果，用于渲染评分与雷达图
  // - `resumeAnalyzing` / `resumeProgress`：控制前端进度条与 loading 状态
  // 关键函数：`analyzeResume()` 会调用 `/api/analyze_resume` 接口
  // -----------------------------
  const resumeText = ref('')
  const resumeResult = ref(null)
  const resumeAnalyzing = ref(false)
  const resumeProgress = ref(0)
  let resumeProgressTimer = null
  
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
  
  // 诊断报告雷达图
  const resumeRadarRef = ref(null)
  let resumeRadarChart = null
  
  const resumeRadarIndicator = computed(() => {
    const dims = resumeResult.value?.dimensions || []
    return dims.map((d) => ({ name: d.name, max: 100 }))
  })
  const resumeRadarValue = computed(() => {
    const dims = resumeResult.value?.dimensions || []
    return dims.map((d) => d.score)
  })
  
  const renderResumeRadar = () => {
    if (!resumeRadarChart || !resumeResult.value?.dimensions?.length) return
    const option = {
      tooltip: { trigger: 'item' },
      radar: {
        indicator: resumeRadarIndicator.value,
        radius: '70%',
        center: ['50%', '54%'],
        splitNumber: 4,
        axisName: { color: 'rgba(31,47,61,0.85)', fontSize: 12 },
        splitLine: { lineStyle: { color: 'rgba(64,158,255,0.12)' } },
        splitArea: { areaStyle: { color: ['rgba(64,158,255,0.03)', 'rgba(64,158,255,0.01)'] } },
        axisLine: { lineStyle: { color: 'rgba(64,158,255,0.18)' } }
      },
      animationDurationUpdate: 260,
      animationEasingUpdate: 'cubicOut',
      series: [
        {
          type: 'radar',
          data: [
            {
              value: resumeRadarValue.value,
              name: '诊断维度',
              areaStyle: { color: 'rgba(64,158,255,0.18)' },
              lineStyle: { width: 2, color: 'rgba(64,158,255,0.95)' },
              itemStyle: { color: '#409EFF' }
            }
          ]
        }
      ]
    }
    resumeRadarChart.setOption(option, { notMerge: true, lazyUpdate: true })
  }
  

  const initResumeRadar = () => {
    if (!resumeRadarRef.value || !resumeResult.value?.dimensions?.length) return
    if (!resumeRadarChart) resumeRadarChart = echarts.init(resumeRadarRef.value)
    renderResumeRadar()
  }

  watch(
    () => resumeResult.value,
    async () => {
      await nextTick()
      initResumeRadar()
    }
  )
  
  // 中文注释：analyzeResume
  // 作用：发送用户输入的简历文本到后端 `/api/analyze_resume`，
  // 并处理加载进度、接收结构化诊断结果（用于渲染雷达图和建议列表）。
  const analyzeResume = async () => {
    if (!resumeText.value) return ElMessage.warning('请输入简历内容')
    resumeAnalyzing.value = true
    resumeProgress.value = 0
    if (resumeProgressTimer) clearInterval(resumeProgressTimer)
  
    // 2 秒模拟进度条（AI 思考）
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
      ElMessage.error('请检查后端 main.py 是否启动')
    } finally {
      if (resumeProgressTimer) clearInterval(resumeProgressTimer)
      resumeProgressTimer = null
      resumeAnalyzing.value = false
    }
  }
  
  // -----------------------------
  // 模拟面试模块（Chat / Mock 面试官）
  // 说明：
  // - `chatHistory` 保存对话记录，role: 'ai' | 'user'
  // - `sendMessage()` 负责将用户问题发送到 `/api/chat`，并将回复添加到对话中
  // - 后端返回的回复在此处以气泡样式展示
  // - `interviewerState` 控制数字人状态：'neutral'(待机) 或 'talking'(说话)
  // - `callAgent()` 触发 Agent 智能推荐流程
  // -----------------------------
  const chatInput = ref('')
  const chatSending = ref(false)
  const interviewerState = ref('neutral')
  const agentCalling = ref(false)
const chatHistory = ref([
  {
    role: 'ai',
    content:
      '你好，我是 AI 面试官。我们从工程化开始：请你简述一下你对 RESTful API 的理解，并说明你会如何做版本管理与错误码设计。'
  }
])

// 职位数据缓存
const jobsData = ref([])
  
const scrollChatToBottom = () => {
  const el = document.querySelector('.chat-window')
  if (el) el.scrollTop = el.scrollHeight
}

// 获取职位数据
const fetchJobsData = async () => {
  try {
    const res = await axios.post(`${API_BASE}/api/recommend`)
    if (res.data.success) {
      jobsData.value = res.data.data
    }
  } catch (e) {
    console.error('获取职位数据失败:', e)
  }
}
  
  // 中文注释：sendMessage
  // 作用：将用户输入发送至后端 `/api/chat`，处理 loading 与异常，并将 AI 回复追加到 `chatHistory`。
  const sendMessage = async () => {
    if (!chatInput.value || chatSending.value) return
    const userMsg = chatInput.value
    chatHistory.value.push({ role: 'user', content: userMsg })
    chatInput.value = ''
    await nextTick()
    scrollChatToBottom()
  
  try {
    chatSending.value = true
    const res = await axios.post(`${API_BASE}/api/chat`, { message: userMsg })
    let reply = res.data?.reply || res.data?.reply_text || '（未返回内容）'

    // 如果有职位数据，随机添加一些职位推荐信息
    if (jobsData.value.length > 0 && Math.random() > 0.5) { // 50%概率添加职位信息
      const randomJob = jobsData.value[Math.floor(Math.random() * jobsData.value.length)]
      const jobInfo = `\n\n💼 相关职位推荐：${randomJob['岗位']} (${randomJob['职业分类']})\n关键词：${randomJob['关键词']}\n平均薪资：${randomJob['平均薪资']}`
      reply += jobInfo
    }

    chatHistory.value.push({ role: 'ai', content: reply })
    await nextTick()
    scrollChatToBottom()
  } catch (e) {
    chatHistory.value.push({ role: 'ai', content: '连接后端失败：请确认 FastAPI 已启动。' })
  } finally {
    chatSending.value = false
  }
  }
  
  // 中文注释：callAgent
  // 作用：触发 Agent 智能推荐流程
  // 1) 设置 interviewerState 为 'talking'（数字人开始说话）
  // 2) 调用后端 `/api/agent` 接口（参数：grade 和 target_job）
  // 3) 将回复内容添加到 chatHistory
  // 4) 延迟 3 秒后将 interviewerState 设回 'neutral'（数字人恢复待机）
  // --- 修改后的 callAgent 函数 (支持显示投递按钮) ---
// --- 1. 修改后的 callAgent (支持传递岗位数据) ---
const callAgent = async () => {
  if (agentCalling.value) return
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }

  agentCalling.value = true
  interviewerState.value = 'talking' 
  
  // 先发一条等待消息
  chatHistory.value.push({ role: 'ai', content: 'Agent 正在分析您的画像并匹配岗位...' })
  scrollChatToBottom()

  try {
    const res = await axios.post(`${API_BASE}/api/agent`, {
      grade: currentUser.value.grade || '大一',
      target_job: currentUser.value.target_role || currentUser.value.target_job || '算法'
    })
    
    // 延迟 2 秒模拟说话
    setTimeout(() => {
       const replyText = res.data.reply || '为您找到以下推荐岗位：'
       const jobList = res.data.data || []

       // 🔥 关键修改：把 jobList 放入消息对象
       chatHistory.value.push({ 
         role: 'ai', 
         content: replyText, 
         jobs: jobList 
       })
       
       interviewerState.value = 'neutral'
       agentCalling.value = false
       scrollChatToBottom()
    }, 2000)
    
  } catch (e) {
    console.error(e)
    chatHistory.value.push({ role: 'ai', content: 'Agent 掉线了，请检查后端。' })
    interviewerState.value = 'neutral'
    agentCalling.value = false
  }
}

// --- 2. 新增 handleApply (处理一键投递) ---
const handleApply = async (job) => {
  // 给当前点击的按钮加 loading 状态
  job._loading = true
  
  try {
    ElMessage.info(`正在通过 Agent 对接 ${job['岗位']} 的 HR...`)
    
    // 模拟 1.5 秒的网络请求延迟
    await sleep(1500) 

    // 调用后端存储投递记录
    await axios.post(`${API_BASE}/api/apply`, {
      username: currentUser.value ? currentUser.value.username : '游客',
      job_name: job['岗位'],
      salary: job['平均薪资'] || '面议'
    })

    ElMessage.success(`✅ 投递成功！简历已发送至 HR 邮箱。`)
    
    // 标记为已投递 (让按钮变灰)
    job._applied = true 

  } catch (e) {
    console.error(e)
    ElMessage.error('投递失败，请稍后重试')
  } finally {
    job._loading = false
  }
}
  // -----------------------------
  // 竞争力沙盘（Radar）模块
  // 说明：通过 6 个滑块实时更新 radarValues，使用 ECharts 渲染雷达图并做平滑动画。
  // 关键函数：initSandboxChart() / renderSandboxChart()，并通过 requestAnimationFrame 做性能优化。
  // -----------------------------
  const sandboxChartRef = ref(null)
  let sandboxChart = null
  let sandboxRafId = 0
  let sandboxPending = false
  
  const radarValues = reactive({
    gpa: 85,
    project: 70,
    intern: 60,
    competition: 80,
    english: 90,
    leader: 75
  })
  
  const sandboxIndicator = [
    { name: '学业成绩 (GPA)', max: 100 },
    { name: '项目实战', max: 100 },
    { name: '实习经验', max: 100 },
    { name: '竞赛获奖', max: 100 },
    { name: '英语能力', max: 100 },
    { name: '领导协作', max: 100 }
  ]
  
  const sandboxSeriesValue = () => [
    radarValues.gpa,
    radarValues.project,
    radarValues.intern,
    radarValues.competition,
    radarValues.english,
    radarValues.leader
  ]
  
  const renderSandboxChart = (isInit = false) => {
    if (!sandboxChart) return
    const option = {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      radar: {
        indicator: sandboxIndicator,
        radius: '68%',
        center: ['50%', '56%'],
        splitNumber: 5,
        axisName: { color: 'rgba(31,47,61,0.85)', fontSize: 12 },
        splitLine: { lineStyle: { color: 'rgba(64,158,255,0.12)' } },
        splitArea: { areaStyle: { color: ['rgba(64,158,255,0.03)', 'rgba(64,158,255,0.01)'] } },
        axisLine: { lineStyle: { color: 'rgba(64,158,255,0.18)' } }
      },
      animation: true,
      animationDuration: isInit ? 350 : 0,
      animationDurationUpdate: 320,
      animationEasingUpdate: 'cubicOut',
      series: [
        {
          name: '核心竞争力',
          type: 'radar',
          symbol: 'circle',
          symbolSize: 6,
          data: [
            {
              value: sandboxSeriesValue(),
              name: '当前状态',
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(64,158,255, 0.65)' },
                  { offset: 1, color: 'rgba(64,158,255, 0.12)' }
                ])
              },
              itemStyle: { color: '#409EFF', borderColor: '#fff', borderWidth: 1 },
              lineStyle: { width: 3, color: 'rgba(64,158,255,0.95)' }
            }
          ]
        }
      ]
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
  
  watch(radarValues, () => {
    scheduleSandboxUpdate()
  })
  
  // -----------------------------
  // 生涯路径规划：generateRoadmap
  // 说明：调用后端 `/api/generate_roadmap`，并将返回的时间轴数据绑定到 `roadmapData`。
  // 前端显示 loading 状态并对异常进行友好提示。
  // -----------------------------
  // 修改 generateRoadmap 内部接收数据的逻辑
const generateRoadmap = async () => {
  if (!roadmapGrade.value || !roadmapRole.value) return ElMessage.warning('请先选择年级和方向')
  roadmapLoading.value = true
  
  try {
    const res = await axios.post(`${API_BASE}/api/generate_roadmap`, {
      current_grade: roadmapGrade.value,
      target_role: roadmapRole.value
    })

    // 接收数据
    roadmapData.value = res.data.roadmap
    roadmapRadar.value = res.data.radar_chart
    roadmapComment.value = res.data.ai_comment
    
    ElMessage.success('规划生成成功')
    
    // 🔥 渲染雷达图 (一定要在 DOM 更新后)
    setTimeout(() => {
      initRadarChart()
    }, 100)

  } catch (error) {
    console.error(error)
    ElMessage.error('生成失败')
  } finally {
    roadmapLoading.value = false
  }
}

// 🔥 新增：初始化雷达图函数
const initRadarChart = () => {
  if (!radarChartRef.value || !roadmapRadar.value) return
  
  const myChart = echarts.init(radarChartRef.value)
  const option = {
    radar: {
      indicator: roadmapRadar.value.indicators,
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#666' },
      splitArea: {
        areaStyle: {
          color: ['rgba(64,158,255, 0.1)', 'rgba(64,158,255, 0.2)', 'rgba(64,158,255, 0.3)', 'rgba(64,158,255, 0.4)'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
      }
    },
    series: [
      {
        name: '能力模型',
        type: 'radar',
        data: [
          {
            value: roadmapRadar.value.values,
            name: '当前能力',
            itemStyle: { color: '#409EFF' },
            areaStyle: { opacity: 0.3 }
          }
        ]
      }
    ]
  }
  myChart.setOption(option)
}
  
const handleSelect = (key) => {
  activeMenu.value = key
  if (key === '3') nextTick(() => initSandboxChart())
  if (key === '1') nextTick(() => initResumeRadar())
}

// 登录成功处理
const handleLoginSuccess = (userData) => {
  currentUser.value = userData
  ElMessage.success(`欢迎回来，${userData.username}！`)
}

// 退出登录
const handleLogout = () => {
  currentUser.value = null
  ElMessage.info('已退出登录')
}
  
  // -----------------------------
  // 生命周期钩子：onMounted / onBeforeUnmount
  // 说明：注册窗口 resize 事件以确保 ECharts 在容器变化时正确 resize，
  // 并在组件卸载时清理定时器与动画帧，避免内存泄漏。
  // -----------------------------
  onMounted(() => {
    const onResize = () => {
      sandboxChart && sandboxChart.resize()
      resumeRadarChart && resumeRadarChart.resize()
    }
    window.addEventListener('resize', onResize)
    if (activeMenu.value === '3') nextTick(() => initSandboxChart())
    // 获取职位数据
    fetchJobsData()
  })
  
  onBeforeUnmount(() => {
    if (resumeProgressTimer) clearInterval(resumeProgressTimer)
    resumeProgressTimer = null
    if (sandboxRafId) cancelAnimationFrame(sandboxRafId)
    sandboxRafId = 0
    if (sandboxChart) sandboxChart.dispose()
    sandboxChart = null
    if (resumeRadarChart) resumeRadarChart.dispose()
    resumeRadarChart = null
  })
  </script>
  
<template>
   <!-- 新增：路由出口，用于显示 SLOGAN 页和登录页 -->
  <router-view />
  <!-- 登录组件 -->
  <!-- 只在路由不是 / 和 /login 时才显示（避免冲突） -->
<Login v-if="!currentUser && $route.path !== '/' && $route.path !== '/login'" @login-success="handleLoginSuccess" />

  <!-- 主应用界面 -->
  <el-container v-else class="app-shell">
      <el-aside width="260px" class="app-aside">
        <div class="brand">
          <div class="brand-icon">
            <el-icon :size="22"><Monitor /></el-icon>
          </div>
          <div class="brand-text">
            <div class="brand-title">职航——AI辅助的大学生生涯成长平台</div>
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
          <el-menu-item index="2">
            <el-icon><ChatDotRound /></el-icon>
            <span>模拟面试</span>
          </el-menu-item>
          <el-menu-item index="3">
            <el-icon><Odometer /></el-icon>
            <span>竞争力沙盘</span>
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
                activeMenu === '0'
                  ? '生涯路径规划'
                  : activeMenu === '1'
                    ? 'AI 简历医生'
                    : activeMenu === '2'
                      ? '模拟面试'
                      : '竞争力沙盘'
              }}
            </div>
            <div class="topbar-tag">科技蓝 · 商业级演示</div>
          </div>
          <div class="topbar-right">
            <el-button type="primary" plain>
              <el-icon style="margin-right: 6px"><MagicStick /></el-icon>
              一键演示
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

  <div class="glass-card control-bar-pro">
  <div class="control-left">
    <div class="control-title">
      <el-icon class="icon-pulse"><Compass /></el-icon>
      <span>规划导航</span>
    </div>
    <div class="control-subtitle">定制你的专属成长路线图</div>
  </div>

  <div class="control-right">
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
                  <span class="time-tag">{{ item.timestamp }}</span>
                  <span class="node-title">{{ item.title }}</span>
                  <el-tag v-if="item.status === 'done'" type="success" size="small" effect="dark">已完成</el-tag>
                  <el-tag v-else-if="item.status === 'process'" type="primary" size="small" effect="dark">进行中</el-tag>
                </div>
                
                <p class="node-content">{{ item.content }}</p>
                
                <div class="node-resources" v-if="item.resources && item.resources.length">
                  <div class="res-label">📚 推荐资源：</div>
                  <div class="res-chips">
                    <span v-for="(r, idx) in item.resources" :key="idx" class="res-chip">
                      {{ r }}
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
<div v-if="activeMenu === '1'" class="animate-fade">
  <ResumeDoctor />
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
                  >
                    <template #append>
                      <el-button type="primary" :loading="chatSending" @click="sendMessage">发送</el-button>
                    </template>
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

.node-resources { display: flex; align-items: center; gap: 10px; border-top: 1px dashed #e4e7ed; padding-top: 8px; }
.res-label { font-size: 12px; color: #909399; }
.res-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.res-chip {
  font-size: 12px; color: #606266; background: white; border: 1px solid #dcdfe6;
  padding: 2px 8px; border-radius: 12px;
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