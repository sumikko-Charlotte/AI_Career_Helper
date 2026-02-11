<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
// 需要安装: npm install markdown-it
import MarkdownIt from 'markdown-it'
import {
  UploadFilled, DataAnalysis, CircleCheck, Warning, Promotion,
  MagicStick, DocumentCopy, InfoFilled
} from '@element-plus/icons-vue'

const md = new MarkdownIt() // 初始化渲染器

// --- 预设模板（降级备用） ---
const FALLBACK_DIAGNOSIS_REPORT = {
  score: 82,
  summary: "简历结构清晰，技术栈覆盖全面，但「量化成果」有待提升。",
  score_details: [
    "✅ 基础分70。因项目使用了STAR法则+5分，技术栈匹配+10分；❌ 但缺少GitHub链接-3分。"
  ],
  highlights: [
    "教育背景优秀",
    "两段相关实习",
    "技术栈命中率高"
  ],
  weaknesses: [
    "缺乏具体性能数据",
    "自我评价泛泛",
    "无开源贡献"
  ]
}

const FALLBACK_OPTIMIZED_RESUME = `# 优化简历（降级模式）

## 💡 AI优化摘要
优化重点: 基于原始简历内容进行结构化优化，突出技术能力和项目成果。

## 🎓 教育背景
（请根据实际简历内容填写）

## 💻 项目经历 (精修版)
（请使用STAR法则重构项目描述）

## 🛠️ 技能清单
（请列出核心技术栈和工具）

## 📄 自我评价
（请补充具体的能力描述和职业目标）`

// --- 核心状态 ---
const currentMode = ref('basic')
const API_BASE = import.meta.env.VITE_API_BASE ?? ''
// 简历医生 URL：部署时通过 Vercel 环境变量 VITE_RESUME_DOCTOR_URL 设置
const resumeDoctorUrl = import.meta.env.VITE_RESUME_DOCTOR_URL || 'https://ai-career-apper-resume-doctor-69etycfa4ohbkxndweoawk.streamlit.app'
console.debug('[ResumeDoctor] API_BASE ->', API_BASE)
console.debug('[ResumeDoctor] resumeDoctorUrl ->', resumeDoctorUrl)
const fileList = ref([])                 // ✅ 保留你的结构
const displayFileName = ref('')          // ✅ 新增：用于展示已选择的文件名
const isAnalyzing = ref(false)
const result = ref(null)

// --- 新增状态 ---
const activeTab = ref('diagnosis')
const isGenerating = ref(false)
const optimizedResume = ref('')
// 预留：如未来支持纯文本输入，可通过该变量传给后端的 resume_text
const resumeText = ref('')

// --- 方法 ---
const handleChange = (file) => {
  // ✅ 你原来的逻辑保留
  fileList.value = [file]

  // ✅ 新增：显示文件名（关键修复）
  displayFileName.value = file?.name || file?.raw?.name || ''

  // ✅ 文件格式验证
  const fileName = displayFileName.value.toLowerCase()
  const allowedExtensions = ['.pdf', '.docx', '.txt']
  const isValidFormat = allowedExtensions.some(ext => fileName.endsWith(ext))
  
  if (displayFileName.value && !isValidFormat) {
    ElMessage.warning('仅支持 PDF、DOCX、TXT 格式的简历文件')
    fileList.value = []
    displayFileName.value = ''
    return
  }

  // ✅ 你原来的逻辑保留
  result.value = null
  optimizedResume.value = ''
  activeTab.value = 'diagnosis'
}

const startAnalyze = async () => {
  if (fileList.value.length === 0) return ElMessage.warning('请先选择简历')
  
  // 禁用用户检查（读取 competition_banned_user_ids）
  try {
    const banned = JSON.parse(localStorage.getItem('competition_banned_user_ids') || '[]')
    const username = localStorage.getItem('remembered_username') || ''
    const users = JSON.parse(localStorage.getItem('competition_user_list') || '[]')
    const me = users.find(u => u.username === username)
    if (me && banned.includes(me.id)) {
      return ElMessage.error('您的账号已被管理员禁用，无法使用该功能')
    }
  } catch (e) {}

  isAnalyzing.value = true
  result.value = null
  optimizedResume.value = ''

  // 在开始诊断时：先在本地任务队列中创建一个"诊断中"任务
  const TASK_KEY = 'competition_resume_task_list'
  const username = localStorage.getItem('remembered_username') || '访客'
  let userId = null
  try {
    const users = JSON.parse(localStorage.getItem('competition_user_list') || '[]')
    const found = users.find(u => u.username === username)
    if (found) userId = found.id
  } catch (e) {}

  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const idStr = `T-${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}-${Math.floor(Math.random()*900+100)}`
  const task = {
    id: idStr,
    user: username || '访客',
    user_id: userId,
    filename: displayFileName.value || (fileList.value[0]?.raw?.name || '未命名简历.pdf'),
    submit_time: `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`,
    score: 0,
    status: 'processing',
    report: ''
  }

  try {
    const existing = JSON.parse(localStorage.getItem(TASK_KEY) || '[]')
    existing.unshift(task)
    localStorage.setItem(TASK_KEY, JSON.stringify(existing))
    window.dispatchEvent(new Event('competitionDataChanged'))
  } catch (e) { console.warn('写入本地任务失败', e) }

  // 调用新的 /api/analyze_resume 接口
  try {
    const selectedFile = fileList.value[0]?.raw
    if (!selectedFile) {
      throw new Error('未找到有效的简历文件，请重新上传')
    }

    const formData = new FormData()
    // 字段名必须与后端保持一致：resume_file
    formData.append('resume_file', selectedFile)
    console.log('✅ 准备上传的文件:', selectedFile.name, '字段名: resume_file')

    const baseUrl = API_BASE || 'https://ai-career-helper-backend-u1s0.onrender.com'
    const res = await axios.post(`${baseUrl}/api/analyze_resume`, formData, {
      // 不手动设置 Content-Type，交给浏览器自动生成 boundary
      timeout: 60000
    })

    // 处理接口返回
    if (res.data && res.data.success) {
      const { diagnosis_report, optimized_resume: optResume, fallback } = res.data

      if (fallback) {
        // 降级模式：使用预设模板
        console.warn('⚠️ [ResumeDoctor] 接口返回 fallback=true，使用预设模板')
        ElMessage.warning('AI分析失败，使用默认报告')
        result.value = {
          score: FALLBACK_DIAGNOSIS_REPORT.score,
          summary: FALLBACK_DIAGNOSIS_REPORT.summary,
          score_rationale: FALLBACK_DIAGNOSIS_REPORT.score_details.join(' '),
          strengths: FALLBACK_DIAGNOSIS_REPORT.highlights,
          weaknesses: FALLBACK_DIAGNOSIS_REPORT.weaknesses
        }
        optimizedResume.value = md.render(FALLBACK_OPTIMIZED_RESUME)
      } else {
        // AI 生成成功：使用接口返回的数据
        console.log('✅ [ResumeDoctor] AI 生成成功，使用接口返回数据')
        result.value = {
          score: diagnosis_report?.score || 0,
          summary: diagnosis_report?.summary || '',
          score_rationale: Array.isArray(diagnosis_report?.score_details) 
            ? diagnosis_report.score_details.join(' ') 
            : (diagnosis_report?.score_details || ''),
          strengths: diagnosis_report?.highlights || [],
          weaknesses: diagnosis_report?.weaknesses || []
        }
        // 优化简历直接渲染（已经是 Markdown 格式）
        if (optResume) {
          optimizedResume.value = md.render(optResume)
        }
      }
    } else {
      // 接口返回 success: false 或其他错误
      throw new Error(res.data?.error || 'AI分析失败，使用默认报告')
    }

    activeTab.value = 'diagnosis'

    // 更新本地任务：设置为已完成
    try {
      const tasksRaw = JSON.parse(localStorage.getItem(TASK_KEY) || '[]')
      const tIdx = tasksRaw.findIndex(t => t.id === task.id)
      if (tIdx > -1) {
        const aiScore = result.value?.score || 0
        tasksRaw[tIdx].status = 'completed'
        tasksRaw[tIdx].score = aiScore
        tasksRaw[tIdx].report = `# 诊断报告\n\n评分：${aiScore}分\n\n${result.value?.summary || ''}`
        localStorage.setItem(TASK_KEY, JSON.stringify(tasksRaw))
        window.dispatchEvent(new Event('competitionDataChanged'))
      }
    } catch (e) { console.warn('更新本地任务失败', e) }

    ElMessage.success('诊断完成！')

    // 真实用户上报：通知用户统计
    try {
      const currentUser = localStorage.getItem('remembered_username') || ''
      if (currentUser) {
        const SERVER_API = import.meta.env.VITE_API_BASE ?? ''
        await axios.post(`${SERVER_API}/api/user/addTask`, { username: currentUser })
      }
    } catch (e) { console.warn('上报任务统计到用户服务失败', e) }

    // 保存到历史记录
    try {
      const currentUser = localStorage.getItem('remembered_username') || '游客'
      const now2 = new Date()
      const dateStr = `${now2.getFullYear()}-${now2.getMonth() + 1}-${now2.getDate()} ${now2.getHours()}:${now2.getMinutes()}`

      await axios.post(`${API_BASE}/api/history/add`, {
        username: currentUser,
        action_type: '简历诊断',
        title: '简历深度评估报告',
        score: result.value.score || 0,
        date: dateStr,
        status: '已完成'
      })
      console.log('✅ 历史记录已自动归档')
    } catch (historyErr) {
      console.warn('历史记录保存失败 (不影响主流程):', historyErr)
    }

  } catch (e) {
    console.error('❌ [ResumeDoctor] 接口调用失败:', e)

    // 适配后端 400/422/5xx 错误，并启用前端降级模板
    if (e.response?.status === 400) {
      ElMessage.error(e.response.data?.error || '请提供简历文件或文本内容')
    } else if (e.response?.status === 422) {
      ElMessage.error('参数格式错误，请检查文件类型（支持PDF/DOCX/TXT）')
    } else if (e.response?.status >= 500) {
      ElMessage.error(e.response.data?.error || '服务器错误，已启用降级模式')
    } else if (e.request) {
      ElMessage.error('网络请求失败，请检查网络连接或后端服务是否正常运行')
    } else {
      ElMessage.error(e.message || 'AI分析失败，使用默认报告')
    }

    // 错误处理：使用预设模板
    result.value = {
      score: FALLBACK_DIAGNOSIS_REPORT.score,
      summary: FALLBACK_DIAGNOSIS_REPORT.summary,
      score_rationale: FALLBACK_DIAGNOSIS_REPORT.score_details.join(' '),
      strengths: FALLBACK_DIAGNOSIS_REPORT.highlights,
      weaknesses: FALLBACK_DIAGNOSIS_REPORT.weaknesses
    }
    optimizedResume.value = md.render(FALLBACK_OPTIMIZED_RESUME)
    activeTab.value = 'diagnosis'
  } finally {
    isAnalyzing.value = false
  }
}

const generateResume = async () => {
  if (!result.value) return ElMessage.warning('请先完成诊断')
  
  // 如果已经有优化简历（从接口返回），直接显示
  if (optimizedResume.value) {
    activeTab.value = 'resume'
    ElMessage.success('优化简历已生成！')
    return
  }

  // 否则调用生成接口（兼容旧逻辑）
  isGenerating.value = true

  try {
    const defaultResumePrompt = `你是一个专业的简历优化专家。请根据用户的简历内容，从"格式规范"、"内容完整性"、"STAR法则应用"三个维度进行打分（满分100）。\n并给出具体的修改建议。输出格式必须为 JSON。`
    const resumePrompt = localStorage.getItem('admin_ai_resume_doctor') || defaultResumePrompt

    const res = await axios.post(`${API_BASE}/api/resume/generate`, {
      focus_direction: '全栈开发',
      diagnosis: result.value,
      system_prompt: resumePrompt
    })
    optimizedResume.value = md.render(res.data.content)
    activeTab.value = 'resume'
    ElMessage.success('简历生成成功！')
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    isGenerating.value = false
  }
}

const copyContent = async () => {
  // 复制纯文本而不是 HTML
  if (!optimizedResume.value) return
  try {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = optimizedResume.value
    await navigator.clipboard.writeText(tempDiv.textContent || tempDiv.innerText)
    ElMessage.success('已复制内容')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="mode-switch-header">
      <el-radio-group v-model="currentMode" size="large">
        <el-radio-button label="basic">普通诊断 (标准版)</el-radio-button>
        <el-radio-button label="vip" class="vip-btn-wrapper">
          <div class="vip-content">
            <el-icon class="rocket-icon"><Promotion /></el-icon>
            <span class="vip-text">DeepSeek 深度精修 (VIP)</span>
          </div>
        </el-radio-button>
      </el-radio-group>
    </div>

    <div v-show="currentMode === 'basic'">
      <div class="doctor-container">

        <div class="header-section">
          <h2>📄 AI 简历全科医生</h2>
          <p>上传 PDF/Word 简历，AI 自动进行 360° 深度诊断</p>
        </div>

        <div class="upload-section">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleChange"
            :show-file-list="false"
            :limit="1"
            accept=".pdf,.docx,.txt"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">点击或拖拽上传简历</div>

            <!-- ✅ 新增：上传后显示文件名（你想要的效果） -->
            <div v-if="displayFileName" class="picked-file">
              已选择：{{ displayFileName }}
            </div>
          </el-upload>

          <el-button
            type="primary"
            size="large"
            class="analyze-btn"
            :loading="isAnalyzing"
            @click="startAnalyze"
          >
            {{ isAnalyzing ? 'AI分析中...' : '✨ 开始深度诊断' }}
          </el-button>
        </div>

        <div v-if="result" class="result-section animate-fade-in">
          <el-tabs v-model="activeTab" type="border-card" class="custom-tabs">

            <el-tab-pane name="diagnosis" label="诊断报告">
              <div class="summary-card">
                <div class="card-title"><el-icon><DataAnalysis /></el-icon> 综合评价 ({{ result.score }}分)</div>
                <p>{{ result.summary }}</p>

                <div class="rationale-box" v-if="result.score_rationale">
                  <div class="rationale-title"><el-icon><InfoFilled /></el-icon> 评分依据：</div>
                  <p>{{ result.score_rationale }}</p>
                </div>

                <el-button type="success" plain class="gen-btn" :loading="isGenerating" @click="generateResume">
                  <el-icon style="margin-right: 5px"><MagicStick /></el-icon>
                  基于此诊断一键生成优化简历
                </el-button>
              </div>

              <div class="details-row">
                <div class="detail-col strength">
                  <div class="col-header"><el-icon><CircleCheck /></el-icon> 亮点</div>
                  <ul><li v-for="s in result.strengths" :key="s">{{ s }}</li></ul>
                </div>
                <div class="detail-col weakness">
                  <div class="col-header"><el-icon><Warning /></el-icon> 不足</div>
                  <ul><li v-for="w in result.weaknesses" :key="w">{{ w }}</li></ul>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane name="resume" label="优化后简历">
              <div v-if="!optimizedResume" class="empty-box">
                <el-empty description="请先点击诊断页的“一键生成”" />
              </div>
              <div v-else class="resume-preview">
                <div class="toolbar">
                  <span>Markdown 预览</span>
                  <el-button size="small" type="primary" @click="copyContent">
                    <el-icon style="margin-right: 5px"><DocumentCopy /></el-icon>
                    复制内容
                  </el-button>
                </div>
                <div class="markdown-body" v-html="optimizedResume"></div>
              </div>
            </el-tab-pane>

          </el-tabs>
        </div>

      </div>
    </div>

    <!--
      VIP 模式：内嵌加载本地 Streamlit（AI简历医生）
      说明：
      - 使用 embed=true 更贴近 Streamlit 的嵌入展示效果
      - 使用 :key 让切换到 VIP 时强制刷新 iframe，避免缓存/空白
    -->
    <div v-show="currentMode === 'vip'" class="vip-container">
      <iframe
        :key="currentMode"
        :src="`${resumeDoctorUrl}?embed=true`"
        class="streamlit-iframe"
        title="AI简历医生（可运行版）"
        loading="lazy"
        referrerpolicy="no-referrer"
        allow="clipboard-read; clipboard-write"
      ></iframe>
    </div>
  </div>
</template>

<style scoped>
/* 保持你的原样式不变，只增加显示文件名的样式 */
.page-wrapper { padding: 20px; }
.mode-switch-header { text-align: center; margin-bottom: 20px; }
.doctor-container { max-width: 800px; margin: 0 auto; padding-bottom: 50px; }
.header-section { text-align: center; margin-bottom: 20px; }
.upload-section { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.analyze-btn { margin-top: 15px; width: 200px; }
.result-section { margin-top: 20px; }
.custom-tabs { min-height: 500px; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.summary-card { background: #fafafa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.card-title { font-weight: bold; font-size: 16px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.rationale-box { background: #fdf6ec; border: 1px solid #faecd8; padding: 10px; border-radius: 6px; margin-top: 10px; }
.rationale-title { color: #E6A23C; font-weight: bold; font-size: 13px; margin-bottom: 5px; }
.rationale-box p { color: #d48806; font-size: 13px; margin: 0; }
.gen-btn { width: 100%; margin-top: 15px; font-weight: bold; }
.details-row { display: flex; gap: 15px; }
.detail-col { flex: 1; background: #fafafa; padding: 15px; border-radius: 8px; }
.col-header { font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; }
.strength .col-header { color: #67C23A; }
.weakness .col-header { color: #E6A23C; }
ul { padding-left: 20px; margin: 0; }
li { font-size: 13px; color: #666; margin-bottom: 5px; }
.empty-box { padding: 50px; text-align: center; }
.resume-preview { border: 1px solid #eee; border-radius: 8px; overflow: hidden; }
.toolbar { background: #f5f7fa; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }
.markdown-body { padding: 20px; line-height: 1.6; max-height: 600px; overflow-y: auto; background: white; }

/* ✅ 新增：显示“已选择文件名” */
.picked-file {
  margin-top: 10px;
  font-size: 13px;
  color: #606266;
}

/* 简单的 markdown 样式补充 */
.markdown-body :deep(h2) { border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 20px; }
.markdown-body :deep(strong) { color: #333; font-weight: bold; }
.markdown-body :deep(ul) { padding-left: 20px; margin: 10px 0; }

.vip-container { height: 85vh; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.streamlit-iframe { width: 100%; height: 100%; border: none; }
.vip-content { display: flex; align-items: center; gap: 6px; }
.rocket-icon { font-size: 18px; color: #F59E0B; animation: floatRocket 2s ease-in-out infinite; margin-right: 4px; }
.vip-text { font-weight: 800; background: linear-gradient(135deg, #D4AF37 0%, #F59E0B 100%); background-clip: text; -webkit-background-clip: text; color: transparent; }
:deep(.vip-btn-wrapper.is-active .el-radio-button__inner) { border-color: #D4AF37 !important; background-color: #FFFBEB !important; box-shadow: -1px 0 0 0 #D4AF37 !important; color: #333 !important; }
@keyframes floatRocket { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
</style>
