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

// --- 核心状态 ---
const currentMode = ref('basic')
const API_BASE = 'http://127.0.0.1:8000'
const fileList = ref([])                 // ✅ 保留你的结构
const displayFileName = ref('')          // ✅ 新增：用于展示已选择的文件名
const isAnalyzing = ref(false)
const result = ref(null)

// --- 新增状态 ---
const activeTab = ref('diagnosis')
const isGenerating = ref(false)
const optimizedResume = ref('')

// --- 方法 ---
const handleChange = (file) => {
  // ✅ 你原来的逻辑保留
  fileList.value = [file]

  // ✅ 新增：显示文件名（关键修复）
  displayFileName.value = file?.name || file?.raw?.name || ''

  // ✅ 你原来的逻辑保留
  result.value = null
  optimizedResume.value = ''
  activeTab.value = 'diagnosis'
}

const startAnalyze = async () => {
  if (fileList.value.length === 0) return ElMessage.warning('请先选择简历')
  isAnalyzing.value = true
  result.value = null

  const formData = new FormData()
  // 注意：这里必须和后端参数名一致，后端我写的是 'file'
  formData.append('file', fileList.value[0].raw)

  try {
    // 1. 原有的核心逻辑：调用 AI 分析接口
    const res = await axios.post(`${API_BASE}/api/resume/analyze`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
    activeTab.value = 'diagnosis'
    ElMessage.success('诊断完成！')

    // 👇👇👇 新增：诊断成功后，自动保存到历史记录 👇👇👇
    try {
      // 获取当前用户名 (如果没有登录就默认叫"游客")
      const currentUser = localStorage.getItem('remembered_username') || '游客'
      
      // 简单的日期格式化 YYYY-M-D
      const now = new Date()
      const dateStr = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}`

      // 调用后端新增的 history 接口
      await axios.post(`${API_BASE}/api/history/add`, {
        username: currentUser,
        action_type: '简历诊断',
        title: '简历深度评估报告', // 你也可以改成 fileList.value[0].name 来显示文件名
        score: result.value.score || 0, // 拿到 AI 给的分数
        date: dateStr,
        status: '已完成'
      })
      console.log('✅ 历史记录已自动归档')
    } catch (historyErr) {
      // 如果保存历史失败（比如后端没写好），不要让用户报错，默默在控制台记录即可
      console.warn('历史记录保存失败 (不影响主流程):', historyErr)
    }
    // 👆👆👆 新增部分结束 👆👆👆

  } catch (e) {
    console.error(e)
    ElMessage.error('连接后端失败，请确保 main.py 已启动')
  } finally {
    isAnalyzing.value = false
  }
}

const generateResume = async () => {
  if (!result.value) return ElMessage.warning('请先完成诊断')
  isGenerating.value = true

  try {
    const res = await axios.post(`${API_BASE}/api/resume/generate`, {
      focus_direction: '全栈开发', // 你原来的逻辑
      diagnosis: result.value
    })
    // 渲染 Markdown 为 HTML
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
            accept=".pdf,.doc,.docx"
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
            {{ isAnalyzing ? '诊断中...' : '✨ 开始深度诊断' }}
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

    <div v-show="currentMode === 'vip'" class="vip-container">
      <iframe
        src="http://localhost:8501/?embed=true"
        class="streamlit-iframe"
        title="AI Resume VIP"
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
.vip-text { font-weight: 800; background: linear-gradient(135deg, #D4AF37 0%, #F59E0B 100%); -webkit-background-clip: text; color: transparent; }
:deep(.vip-btn-wrapper.is-active .el-radio-button__inner) { border-color: #D4AF37 !important; background-color: #FFFBEB !important; box-shadow: -1px 0 0 0 #D4AF37 !important; color: #333 !important; }
@keyframes floatRocket { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
</style>
