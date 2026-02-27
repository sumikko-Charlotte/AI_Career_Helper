<script setup>
import { computed, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

// Use Vite env variable to configure backend base URL to avoid hard-coding ports.
// 部署时通过 Vercel 环境变量 VITE_API_BASE 设置，格式：https://your-backend.onrender.com
// Changes made: switched to `VITE_API_BASE`, added debug logs, improved error handling for requests. (Modified: 2026-01-30)
const API_BASE = import.meta.env.VITE_API_BASE || ''
const md = new MarkdownIt()

// Debug helper: expose resolved API endpoint in console
console.debug('[VirtualExperiment] API_BASE ->', API_BASE)
if (!import.meta.env.VITE_API_BASE) console.debug('[VirtualExperiment] VITE_API_BASE not set, using default fallback:', API_BASE) 

const careers = ref([
  { name: '产品经理', desc: '需求挖掘、体验设计、项目推进、跨团队协作' },
  { name: '全栈开发', desc: '前后端一把抓，业务开发 + 工程化 + 部署运维' },
  { name: 'UI 设计师', desc: '视觉设计、交互体验、品牌统一与落地' },
  { name: '运营', desc: '用户增长、活动策划、数据分析与转化优化' },
  { name: '测试工程师', desc: '测试用例设计、自动化测试、质量保障' },
  { name: '算法工程师', desc: '模型训练、特征工程、效果评估与优化' },
  { name: '数据分析师', desc: '数据清洗、可视化分析、业务指标洞察' },
  { name: '市场营销', desc: '品牌传播、市场投放、活动策划与复盘' },
  { name: '新媒体运营', desc: '内容策划、账号增长、用户互动与私域运营' },
  { name: '销售', desc: '客户沟通、需求挖掘、成交与关系维护' },
  { name: '教师', desc: '课程设计、课堂教学、学习效果追踪' },
  { name: '医生', desc: '临床诊疗、病情评估、患者沟通与随访' },
  { name: '人力资源', desc: '招聘面试、组织发展、绩效与员工关系管理' },
  { name: '项目经理', desc: '进度把控、风险管理、跨团队协同推进' },
  { name: '客服专员', desc: '问题受理、情绪安抚、反馈闭环与满意度提升' }
])

/* per-career SVG icons (keeps style consistent and uses blue tones) */
const icons = {
  '产品经理': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 21l4.5-1.5L21 6l-3.5-3.5L3 21z" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <circle cx="7.5" cy="17.5" r="1.2" fill="#3B82F6"/>
    </svg>
  `,
  '全栈开发': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="5" width="20" height="14" rx="2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M8 9l-4 3 4 3M16 9l4 3-4 3" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `,
  'UI 设计师': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="9" r="3" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M4 20c4-2 8-2 16 0" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round"/>
      <rect x="3" y="3" width="6" height="3" rx="0.6" fill="#fff" opacity="0"/>
    </svg>
  `,
  '运营': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M6 15l3-4 4 5 5-8" stroke="#3B82F6" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>
  `,
  '测试工程师': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="11" cy="11" r="3" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M21 21l-4.35-4.35" stroke="#3B82F6" stroke-width="1.4" stroke-linecap="round"/>
      <path d="M9 11l1.5 1.5L14 9" stroke="#10B981" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `,
  '算法工程师': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 3c-2.8 0-5 2.2-5 5 0 3 5 7 5 7s5-4 5-7c0-2.8-2.2-5-5-5z" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M8 8h8M9 11h6" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round"/>
    </svg>
  `,
  '市场营销': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 11h12l6-5v10l-6-5H3z" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M15 19v-2m4 2v-4" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round"/>
    </svg>
  `,
  '教师': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="6" width="18" height="12" rx="1.2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M7 9h10M7 12h10" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round"/>
    </svg>
  `,
  '医生': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="3" width="12" height="18" rx="2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M12 7v10M9 10h6" stroke="#3B82F6" stroke-width="1.4" stroke-linecap="round"/>
    </svg>
  `,
  '人力资源': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="8.5" cy="9" r="2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <circle cx="15.5" cy="10" r="1.6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/>
      <path d="M3 19c1.5-3 6-4 9-4s7.5 1 9 4" stroke="#3B82F6" stroke-width="1.2" stroke-linecap="round"/>
    </svg>
  `,
  'default': `
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="7" width="18" height="12" rx="2" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2" />
    </svg>
  `,
}


const searchKeyword = ref('')
const currentCareer = ref('')
const questions = ref([])
const answers = ref({})
const submitting = ref(false)
const loadingCareer = ref('')
const loadingCustomCareer = ref(false) // 新增：自定义职业生成中的 loading 状态
const markdownRaw = ref('')
// markdownProcessed: markdown with injected icons and small transforms for rendering
const markdownProcessed = ref('')

// 新增：前端 HTML 标签净化函数，防止职业匹配分析报告中混入 HTML / SVG / <span> 片段
// 只对 HTML 标签做删除，不会修改 Markdown 语法字符（#、*、- 等）
const cleanHtmlTags = (text) => {
  if (!text) return ''
  return text.replace(/<[^>]+>/g, '')
}

// Inject colored icons for specific section headings to enhance readability
const ICONS_HTML = {
  overall: `<span class="md-icon overall" aria-hidden="true">\
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
      <path d="M12 2l3 6 6 .5-4.5 3.5L19 20 12 16 5 20l2.5-7.9L3 8.5 9 8 12 2z" fill="#165DFF"/>\
    </svg>\
  </span>`,
  strengths: `<span class="md-icon strength" aria-hidden="true">\
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
      <path d="M9 12l2 2 4-4" stroke="#00B42A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>\
      <circle cx="12" cy="12" r="8" stroke="#00B42A" stroke-width="1.2" fill="none"/>\
    </svg>\
  </span>`,
  suitable: `<span class="md-icon suitable" aria-hidden="true">\
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
      <path d="M2 12l4 2 4-6 6 8 6-10" stroke="#FF7D00" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>\
    </svg>\
  </span>`,
  unsuitable: `<span class="md-icon unsuitable" aria-hidden="true">\
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
      <path d="M6 6l12 12M18 6L6 18" stroke="#86909C" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>\
    </svg>\
  </span>`
}

// transformMarkdown: insert icons before headings that contain certain keywords
function transformMarkdown(mdText) {
  if (!mdText) return ''
  let s = mdText
  try {
    // Order matters: try to match more specific phrases first
    s = s.replace(/(^\s*#{1,6}\s*)(.*(整体匹配度|匹配度|匹配度标题).*?$)/gim, (m, p1, p2) => `${p1}${ICONS_HTML.overall} ${p2}`)
    s = s.replace(/(^\s*#{1,6}\s*)(.*(优势分析|关键优势|优势).*?$)/gim, (m, p1, p2) => `${p1}${ICONS_HTML.strengths} ${p2}`)
    s = s.replace(/(^\s*#{1,6}\s*)(.*(适合职业|推荐职业|建议方向).*?$)/gim, (m, p1, p2) => `${p1}${ICONS_HTML.suitable} ${p2}`)
    s = s.replace(/(^\s*#{1,6}\s*)(.*(不适合职业|不适合|风险|潜在风险).*?$)/gim, (m, p1, p2) => `${p1}${ICONS_HTML.unsuitable} ${p2}`)
  } catch (err) {
    console.warn('transformMarkdown failed', err)
  }
  return s
}

// Render processed markdown (with icons) to HTML
const markdownHtml = computed(() => {
  if (!markdownProcessed.value) return ''
  // 在渲染前做一次前端净化，双保险去除 HTML / SVG / <span> 等标签，但保留 Markdown 语法
  const cleaned = cleanHtmlTags(markdownProcessed.value)
  return md.render(cleaned)
})

const filteredCareers = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) return careers.value
  return careers.value.filter(c =>
    c.name.toLowerCase().includes(kw) ||
    c.desc.toLowerCase().includes(kw)
  )
})

const allAnswered = computed(
  () => questions.value.length > 0 && questions.value.every(q => answers.value[q.id])
)

// loadQuestions: POST /api/virtual-career/questions
// - 仅用于「示例职业卡片」；逻辑保持不变，保证原有流程 100% 不受影响
// - Verified backend route exists and expects { career: string } in POST body
// - Improved error handling: distinguishes network errors, 404 and 5xx; shows friendly messages
const loadQuestions = async (careerName) => {
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

  currentCareer.value = careerName
  loadingCareer.value = careerName
  markdownRaw.value = ''
  try {
    const url = `${API_BASE}/api/virtual-career/questions`
    console.debug('[VirtualExperiment] POST', url, { career: careerName })
    // 从 Admin 配置读取系统提示词（localStorage），key: admin_ai_virtual_career
    const defaultVirtualPrompt = `你是一个沉浸式体验脚本生成器。根据用户选择的职业（例如“产品经理”），生成一套 15 道情景模拟题目，覆盖真实工作场景，句式简洁明了，便于用户做出选择题回答。每题给出 3 个选项。`
    const virtualPrompt = localStorage.getItem('admin_ai_virtual_career') || defaultVirtualPrompt

    // 请求方法：POST（后端定义为 POST /api/virtual-career/questions，body: { career, system_prompt })
    const res = await axios.post(url, { career: careerName, system_prompt: virtualPrompt })
    console.debug('[VirtualExperiment] RESPONSE', res.status, res.data)

    // 如果后端成功返回但题目为空，保持友好提示
    const qs = res?.data?.questions || []
    if (!qs.length) {
      ElMessage.error('AI 暂未返回题目，请稍后重试')
      return
    }

    questions.value = qs
    answers.value = Object.fromEntries(qs.map(q => [q.id, '']))
    ElMessage.success(`已为「${careerName}」生成体验题目`)
  } catch (e) {
    // 友好错误提示：区分网络错误、404 与 5xx
    if (!e.response) {
      ElMessage.error('网络异常或无法连接后端，请检查后端是否已启动并确认 VITE_API_BASE 环境变量指向正确地址')
    } else if (e.response.status === 404) {
      ElMessage.error('题目生成接口不存在（404）。请确认后端是否包含 POST /api/virtual-career/questions 或更新前端配置')
    } else if (e.response.status >= 500) {
      ElMessage.error('后端出现异常（5xx），请稍后重试或查看后端日志')
    } else {
      ElMessage.error('生成题目失败，请稍后重试')
    }
    console.warn('virtual-career/questions request failed:', e)
  } finally {
    loadingCareer.value = ''
  }
}

// startBySearch: 顶部搜索/输入职业入口
// - 第一步：先判断是否在示例职业列表中，是的话复用原有 loadQuestions 流程
// - 第二步：不在示例列表，则调用 /api/generate-job-test 生成 15 题
// - 注意：只改「题目获取」这一步，后续做题 / 分析 / 下载逻辑完全复用原有代码
const startBySearch = async () => {
  const kw = searchKeyword.value.trim()
  if (!kw) {
    return ElMessage.warning('请先输入一个想体验的职业，例如：律师、医生、产品经理等')
  }

  // 1) 先看是否属于示例职业：优先精确匹配，再做包含/被包含匹配
  const lowerKw = kw.toLowerCase()
  const exact = careers.value.find(c => c.name === kw)
  const fuzzy =
    exact ||
    careers.value.find(
      c =>
        c.name.toLowerCase() === lowerKw ||
        c.name.toLowerCase().includes(lowerKw) ||
        lowerKw.includes(c.name.toLowerCase())
    )

  if (fuzzy) {
    // 命中示例职业：完全走原有流程
    await loadQuestions(fuzzy.name)
    return
  }

  // 2) 非示例职业：调用后端 /api/generate-job-test 获取 AI 生成题目
  console.debug('[VirtualExperiment] startBySearch -> custom career', kw)
  loadingCustomCareer.value = true
  currentCareer.value = kw
  markdownRaw.value = ''
  markdownProcessed.value = ''

  try {
    const url = `${API_BASE}/api/generate-job-test`
    console.debug('[VirtualExperiment] POST', url, { jobName: kw })

    const res = await axios.post(url, { jobName: kw })
    const data = res?.data || {}

    // 后端约定的业务错误结构：{code, msg}
    if (data.code && data.code !== 200 && !data.questions && !data.testQuestions) {
      throw new Error(data.msg || 'AI生成失败，请稍后重试')
    }

    // 新版后端已对齐原有接口格式：优先使用 data.questions
    const rawQuestions = Array.isArray(data.questions)
      ? data.questions
      : Array.isArray(data.testQuestions)
        ? data.testQuestions
        : []

    if (!rawQuestions.length) {
      throw new Error('AI 暂未返回题目，请稍后重试')
    }

    // 统一成现有 questions 结构：[{ id, title, options }]；
    // 若后端已经返回 id/title/options，则直接复用，避免重复包装
    const qs = rawQuestions.slice(0, 15).map((q, idx) => {
      const baseId = q.id || `q${idx + 1}`
      const title = q.title || q.question || q.stem || `第 ${idx + 1} 题`
      const options = Array.isArray(q.options)
        ? q.options.map(o => String(o))
        : []
      return {
        id: String(baseId),
        title,
        options,
      }
    })

    if (!qs.length) {
      throw new Error('AI 生成的题目结构异常，请稍后重试')
    }

    questions.value = qs
    answers.value = Object.fromEntries(qs.map(q => [q.id, '']))

    ElMessage.success(`已为「${kw}」生成 AI 体验题目`)
  } catch (e) {
    console.warn('generate-job-test request failed:', e)
    const msg =
      e.response?.data?.msg ||
      e.message ||
      'AI生成失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loadingCustomCareer.value = false
  }
}

const submitAnswers = async () => {
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

  if (!currentCareer.value) return ElMessage.warning('请先选择一个想体验的职业')
  if (!allAnswered.value) return ElMessage.warning('请先完成 15 题再提交')
  submitting.value = true
  markdownRaw.value = ''
  try {
    const url = `${API_BASE}/api/analyze-experiment`
    console.debug('[VirtualExperiment] POST', url, { answers: answers.value, career: currentCareer.value })
    // 附带虚拟体验的系统提示词（localStorage）
    const defaultVirtualPrompt = `你是一个沉浸式体验脚本生成器。根据用户选择的职业（例如“产品经理”），生成一套 15 道情景模拟题目，覆盖真实工作场景，句式简洁明了，便于用户做出选择题回答。每题给出 3 个选项。`
    const virtualPrompt = localStorage.getItem('admin_ai_virtual_career') || defaultVirtualPrompt

    const res = await axios.post(url, {
      answers: answers.value,
      career: currentCareer.value,
      system_prompt: virtualPrompt
    })
    console.debug('[VirtualExperiment] RESPONSE', res.status, res.data)
    markdownRaw.value = res?.data?.markdown || ''
    // apply transformations (inject icons, enforce simple structure) and set processed markdown for rendering
    markdownProcessed.value = transformMarkdown(markdownRaw.value)
    ElMessage.success('职业匹配度分析已生成')
  } catch (e) {
    if (!e.response) {
      ElMessage.error('网络异常或无法连接后端，请检查后端是否已启动并确认 VITE_API_BASE 指向正确地址')
    } else if (e.response.status === 404) {
      ElMessage.error('分析接口不存在（404）。请确认后端是否包含 POST /api/analyze-experiment 或更新前端配置')
    } else if (e.response.status >= 500) {
      ElMessage.error('后端出现异常（5xx），请稍后重试或查看后端日志')
    } else {
      ElMessage.error('接口请求失败，请稍后重试')
    }
    console.warn('analyze-experiment request failed:', e)
  } finally {
    submitting.value = false
  }
}

const downloadMd = () => {
  if (!markdownRaw.value) return ElMessage.warning('暂无报告可下载')
  const filenameCareer = currentCareer.value || '职业体验'
  const blob = new Blob([markdownRaw.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `虚拟职业体验_${filenameCareer}_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="ve-page">
    <div class="page-header">
      <h2>🧭 虚拟职业体验</h2>
      <p>先选一个想体验的职业，再通过 15 道情景题，快速评估与你的匹配度</p>
    </div>

    <el-card class="career-card-wrapper" shadow="hover">
      <div class="career-header">
        <div>
          <div class="career-title">选择一个职业，开始一场“沉浸式体验”</div>
          <div class="career-subtitle">支持搜索冷门职业，AI 将为你即时生成体验脚本与题目</div>
        </div>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索或输入职业，如：产品经理 / 算法工程师 / 律师"
          clearable
          class="career-search"
          :prefix-icon="Search"
          @keyup.enter="startBySearch"
        >
          <template #append>
            <el-button
              type="primary"
              size="small"
              :loading="loadingCustomCareer"
              @click="startBySearch"
            >
              {{ loadingCustomCareer ? '生成中...' : '开始体验' }}
            </el-button>
          </template>
        </el-input>
      </div>

      <div class="career-grid">
        <el-card
          v-for="c in filteredCareers"
          :key="c.name"
          class="career-card"
          :class="{ active: currentCareer === c.name }"
          shadow="hover"
        >
          <div class="career-icon" aria-hidden="true" v-html="icons[c.name] || icons['default']"></div>

          <div class="career-name">{{ c.name }}</div>
          <div class="career-desc">{{ c.desc }}</div>

          <div class="card-footer">
            <el-button
              size="small"
              class="career-btn"
              :loading="loadingCareer === c.name"
              @click="loadQuestions(c.name)"
            >
              {{ currentCareer === c.name ? '重新生成题目' : '开始体验' }}
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>

    <el-card v-if="questions.length" class="question-card" shadow="hover">
      <div class="q-header">
        <div class="q-title-main">
          当前体验职业：<span class="q-career">{{ currentCareer }}</span>
        </div>
        <div class="q-subtitle">请根据自己的真实偏好作答，每道题只能选择一个最符合的选项</div>
      </div>

      <div v-for="q in questions" :key="q.id" class="q-item">
        <div class="q-title">{{ q.id.toUpperCase() }} · {{ q.title }}</div>
        <el-radio-group v-model="answers[q.id]" class="q-options">
          <el-radio
            v-for="(opt, idx) in q.options"
            :key="idx"
            :value="opt"
          >
            {{ String.fromCharCode(65 + idx) }}. {{ opt }}
          </el-radio>
        </el-radio-group>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" :loading="submitting" @click="submitAnswers">
          {{ submitting ? '提交中...' : '提交答案，查看匹配度报告' }}
        </el-button>
        <el-button type="success" size="large" plain :disabled="!markdownRaw" @click="downloadMd">
          下载报告
        </el-button>
      </div>
    </el-card>

    <el-card v-else class="question-card empty-card" shadow="hover">
      <div class="empty-tip">请先在上方选择或搜索一个职业，然后点击「开始体验」生成题目</div>
    </el-card>

    <el-card v-if="markdownRaw" class="report-card" shadow="hover">
      <div class="report-header">
        <div class="report-title">📄 AI 职业匹配度分析（Markdown 渲染）</div>
      </div>
      <div class="markdown-body" v-html="markdownHtml"></div>
    </el-card>
  </div>
</template>

<style scoped>
.ve-page { padding: 20px 12px 40px; }
.page-header { margin: 8px 0 18px; text-align: center; }
.page-header h2 { margin: 0 0 6px; font-size: 22px; }
.page-header p { margin: 0; color: #6b7280; }

.career-card-wrapper { border-radius: 12px; margin-bottom: 20px; max-width: 1100px; margin-left: auto; margin-right: auto; padding: 18px; }
.career-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.career-title { font-weight: 700; font-size: 18px; color: #0f172a; text-align: center; }
.career-subtitle { font-size: 13px; color: #6b7280; margin-top: 4px; text-align: center; }
.career-search { max-width: 420px; width: 100%; }

/* 固定三列布局，卡片在容器中水平居中；在窄屏下允许水平滚动以保证始终显示为三列 */
.career-grid {
  display: grid;
  grid-template-columns: repeat(3, 300px);
  gap: 20px;
  justify-content: center;
  width: 100%;
  overflow-x: auto;
  padding-bottom: 6px;
}
.career-card {
  background: #FFFFFF;
  color: #0f172a;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(16,24,40,0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 18px;
  height: 240px;
  text-align: center;
}
.career-card.active { outline: 2px solid rgba(59,130,246,0.12); box-shadow: 0 10px 26px rgba(59,130,246,0.08); }

.career-icon { margin-top: 6px; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; }
.career-name { font-weight: 700; margin-bottom: 6px; font-size: 16px; color: #0f172a; }
.career-desc { font-size: 13px; color: #9ca3af; min-height: 40px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-clamp: 2; }

.card-footer { width: 100%; display: flex; justify-content: center; }
.career-btn {
  background: #EFF6FF; /* 浅蓝 */
  color: #3B82F6;
  border: none;
  width: 140px;
  border-radius: 8px;
}

/* 当前卡片为已选中时按钮为主题色 */
.career-card.active .career-btn { background: #3B82F6; color: #fff; }

/* 悬停卡片按钮变为深蓝色 */
.career-card:hover .career-btn { background: #3B82F6; color: #fff; }

/* 保持题目/报告区样式不变 */
.question-card { border-radius: 14px; margin-top: 16px; }
.empty-card { text-align: center; padding: 32px 16px; }
.empty-tip { color: #9ca3af; font-size: 14px; }

.q-header { margin-bottom: 10px; }
.q-title-main { font-weight: 700; color: #0f172a; }
.q-career { color: #3B82F6; }
.q-subtitle { font-size: 13px; color: #9ca3af; margin-top: 4px; }

.q-item { padding: 14px 0; border-bottom: 1px dashed rgba(0,0,0,0.06); }
.q-item:last-child { border-bottom: none; }
.q-title { font-weight: 700; color: #0f172a; margin-bottom: 10px; }
.q-options { display: grid; gap: 8px; }

.actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 16px; }

.report-card { margin-top: 16px; border-radius: 14px; background: #ffffff; padding: 12px; box-shadow: 0 6px 18px rgba(16,24,40,0.06); }
.report-title { font-weight: 800; color: #0f172a; }

/* Markdown 渲染区样式优化：白色背景、深灰文字、padding、行高和响应式适配 */
.markdown-body {
  background: #FFFFFF !important;
  color: #000000 !important; /* 强制纯黑文本 */
  padding: 20px !important;
  border-radius: 8px !important;
  line-height: 1.7 !important;
  max-width: 940px;
  margin: 0 auto;
  overflow-wrap: break-word;
  word-break: break-word;
}

/* 让容器内所有元素继承黑白配色，避免深色遮挡 */
.markdown-body, .markdown-body * {
  color: #000000 !important;
  background: transparent !important;
}

/* 但为代码块保留浅色背景以便区分 */
.markdown-body :deep(code) {
  background: #f6f8fa !important;
  color: #000 !important;
  padding: 2px 4px !important;
  border-radius: 4px !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
  font-size: 0.95em;
}
.markdown-body :deep(pre) {
  background: #f6f8fa !important;
  color: #000 !important;
  padding: 12px !important;
  border-radius: 8px !important;
  overflow: auto;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 18px 0 10px;
  color: #000000 !important;
  font-weight: 800;
}

.markdown-body :deep(p) { margin: 8px 0; color: #000000 !important; }
.markdown-body :deep(a) { color: #165DFF !important; text-decoration: underline; }
.markdown-body :deep(li) { margin: 8px 0; }
.markdown-body :deep(ul),
.markdown-body :deep(ol) { padding-left: 1.25em; }

/* 图标样式（和文本垂直居中、颜色鲜明） */
.md-icon { display: inline-flex; align-items: center; vertical-align: middle; margin-right: 8px; }
.md-icon svg { display: block; }

.md-icon.overall svg { filter: none; }
.md-icon.strength svg { filter: none; }
.md-icon.suitable svg { filter: none; }
.md-icon.unsuitable svg { filter: none; }

/* 响应式适配 */
@media (max-width: 768px) {
  .markdown-body { padding: 16px !important; max-width: calc(100% - 32px); }
}
</style>

