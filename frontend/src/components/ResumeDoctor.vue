<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, DataAnalysis, CircleCheck, Warning, Promotion, 
  MagicStick, DocumentCopy, Refresh, InfoFilled 
} from '@element-plus/icons-vue'

// --- 状态变量 ---
const currentMode = ref('basic') 
const API_BASE = 'http://127.0.0.1:8000'
const fileList = ref([])
const isAnalyzing = ref(false)
const result = ref(null)

// --- 新增状态 ---
const activeTab = ref('diagnosis') 
const isGenerating = ref(false)    
const optimizedResume = ref('')    

// --- 方法 ---
const handleExceed = (files) => { fileList.value = [files[0]] }

const handleChange = (file) => {
  fileList.value = [file]
  result.value = null 
  optimizedResume.value = ''
  activeTab.value = 'diagnosis'
}

// 1. 诊断
const startAnalyze = async () => {
  if (fileList.value.length === 0) return ElMessage.warning('请先选择一份简历文件')
  isAnalyzing.value = true
  result.value = null
  
  const formData = new FormData()
  formData.append('file', fileList.value[0].raw)

  try {
    const res = await axios.post(`${API_BASE}/api/resume/analyze`, formData)
    result.value = res.data
    activeTab.value = 'diagnosis'
    ElMessage.success('诊断完成！')
  } catch (e) {
    ElMessage.error('服务未启动，请检查后端 main.py')
  } finally {
    isAnalyzing.value = false
  }
}

// 2. 生成简历
const generateResume = async () => {
  if (!result.value) return ElMessage.warning('请先完成诊断')
  isGenerating.value = true
  
  try {
    const res = await axios.post(`${API_BASE}/api/resume/generate`, {
      focus_direction: "全栈开发",
      diagnosis: result.value
    })
    optimizedResume.value = res.data.content
    activeTab.value = 'resume' // 自动切Tab
    ElMessage.success('简历优化完成！')
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    isGenerating.value = false
  }
}

// 3. 复制
const copyContent = async () => {
  if (!optimizedResume.value) return
  try {
    await navigator.clipboard.writeText(optimizedResume.value)
    ElMessage.success('已复制到剪贴板')
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
            :on-exceed="handleExceed"
            :limit="1"
            :file-list="fileList"
            accept=".pdf,.doc,.docx"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">将简历拖到此处，或 <em>点击上传</em></div>
          </el-upload>

          <el-button type="primary" size="large" class="analyze-btn" :loading="isAnalyzing" @click="startAnalyze">
            {{ isAnalyzing ? 'AI 正在诊断中...' : '✨ 开始深度诊断' }}
          </el-button>
        </div>

        <div v-if="result" class="result-section animate-fade-in">
          <el-tabs v-model="activeTab" type="border-card" class="custom-tabs-container">
            
            <el-tab-pane name="diagnosis">
              <template #label><span class="custom-tab-label"><el-icon><DataAnalysis /></el-icon> 诊断报告</span></template>

              <div class="summary-card">
                <div class="card-header-row">
                  <div class="score-box">
                    <span class="score-num">{{ result.score }}</span>
                    <span class="score-unit">分</span>
                  </div>
                  <div class="summary-text">
                    <div class="card-title"><el-icon><DataAnalysis /></el-icon> 综合评价</div>
                    <p>{{ result.summary }}</p>
                  </div>
                </div>

                <div class="rationale-box" v-if="result.score_rationale">
                  <div class="rationale-title"><el-icon><InfoFilled /></el-icon> 评分依据：</div>
                  <p>{{ result.score_rationale }}</p>
                </div>
                <el-button type="success" plain class="generate-btn-main" :loading="isGenerating" @click="generateResume">
                  <el-icon style="margin-right: 5px"><MagicStick /></el-icon> 基于此诊断一键生成优化简历
                </el-button>
              </div>

              <div class="details-row">
                <div class="detail-col strength">
                  <div class="col-header"><el-icon><CircleCheck /></el-icon> 简历亮点</div>
                  <ul><li v-for="(item, i) in result.strengths" :key="i">{{ item }}</li></ul>
                </div>
                <div class="detail-col weakness">
                  <div class="col-header"><el-icon><Warning /></el-icon> 待改进</div>
                  <ul><li v-for="(item, i) in result.weaknesses" :key="i">{{ item }}</li></ul>
                </div>
              </div>

              <div class="suggestion-card">
                <div class="card-title">💡 AI 修改建议</div>
                <div class="suggestion-list">
                  <div v-for="(s, i) in result.suggestions" :key="i" class="suggestion-item">
                    <span class="index">{{ i + 1 }}</span>
                    <span class="text">{{ s }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane name="resume">
              <template #label><span class="custom-tab-label"><el-icon><MagicStick /></el-icon> 优化后简历</span></template>

              <div v-if="!optimizedResume" class="empty-state-box">
                <el-empty description="请先点击诊断报告页的“一键生成”按钮" />
                <el-button type="primary" @click="generateResume" :loading="isGenerating">立即生成</el-button>
              </div>

              <div v-else class="resume-preview-wrapper">
                <div class="preview-toolbar">
                  <span class="tips">Markdown 格式预览</span>
                  <div class="actions">
                    <el-button size="small" :icon="Refresh" @click="generateResume">重新生成</el-button>
                    <el-button size="small" type="primary" :icon="DocumentCopy" @click="copyContent">复制内容</el-button>
                  </div>
                </div>
                <div class="markdown-body"><pre>{{ optimizedResume }}</pre></div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

      </div>
    </div>

    <div v-show="currentMode === 'vip'" class="vip-container">
      <iframe src="http://localhost:8501/?embed=true" class="streamlit-iframe" title="AI Resume VIP"></iframe>
    </div>
  </div>
</template>

<style scoped>
/* 基础容器 */
.page-wrapper { padding: 20px; }
.mode-switch-header { text-align: center; margin-bottom: 30px; }
.doctor-container { max-width: 800px; margin: 0 auto; padding-bottom: 50px; }

/* 头部 */
.header-section { text-align: center; margin-bottom: 30px; }
.header-section h2 { color: #303133; margin-bottom: 10px; }
.header-section p { color: #909399; font-size: 14px; }

/* 上传 */
.upload-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; }
.analyze-btn { margin-top: 20px; width: 200px; font-weight: bold; background: linear-gradient(135deg, #409EFF, #337ecc); border: none; }

/* 结果卡片 */
.result-section { margin-top: 30px; }
.summary-card, .suggestion-card, .detail-col { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }

/* 分数与评价布局 */
.card-header-row { display: flex; align-items: flex-start; gap: 20px; margin-bottom: 15px; }
.score-box { background: #f0f9eb; color: #67C23A; padding: 10px 20px; border-radius: 12px; text-align: center; min-width: 80px; }
.score-num { font-size: 32px; font-weight: bold; display: block; line-height: 1; }
.score-unit { font-size: 12px; }
.summary-text { flex: 1; }

/* 🔥 评分依据样式 (你要找的那个) 🔥 */
.rationale-box {
  background: #fdf6ec; border: 1px solid #faecd8; 
  padding: 12px 16px; border-radius: 8px; margin-bottom: 15px;
}
.rationale-title { color: #E6A23C; font-weight: bold; font-size: 13px; margin-bottom: 5px; display: flex; align-items: center; gap: 5px; }
.rationale-box p { color: #d48806; font-size: 13px; margin: 0; line-height: 1.5; }

.card-title, .col-header { font-weight: bold; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; color: #303133; }
.strength .col-header { color: #67C23A; }
.weakness .col-header { color: #E6A23C; }
.generate-btn-main { width: 100%; font-weight: bold; margin-top: 10px; }

.details-row { display: flex; gap: 20px; margin-top: 20px; }
.detail-col { flex: 1; }
ul { padding-left: 20px; margin: 0; }
li { margin-bottom: 8px; color: #606266; font-size: 14px; line-height: 1.6; }

.suggestion-card { margin-top: 20px; }
.suggestion-item { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
.suggestion-item .index { background: #EBF5FF; color: #409EFF; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0; }
.suggestion-item .text { color: #606266; font-size: 14px; line-height: 1.6; }

/* Tabs */
.custom-tabs-container { min-height: 500px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); border-radius: 8px; background: white; }
.custom-tab-label { display: flex; align-items: center; gap: 6px; font-weight: bold; }

/* 简历预览 */
.empty-state-box { text-align: center; padding: 60px 0; }
.resume-preview-wrapper { border: 1px solid #dcdfe6; border-radius: 8px; overflow: hidden; background: white; }
.preview-toolbar { background: #f5f7fa; padding: 10px 20px; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; }
.markdown-body { padding: 30px; font-family: 'Courier New', Courier, monospace; white-space: pre-wrap; line-height: 1.7; color: #333; max-height: 600px; overflow-y: auto; font-size: 14px; }

/* VIP & 动画 */
.vip-container { height: 85vh; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.streamlit-iframe { width: 100%; height: 100%; border: none; }
.vip-content { display: flex; align-items: center; gap: 6px; }
.rocket-icon { font-size: 18px; color: #F59E0B; animation: floatRocket 2s ease-in-out infinite; margin-right: 4px; }
.vip-text { font-weight: 800; background: linear-gradient(135deg, #D4AF37 0%, #F59E0B 100%); -webkit-background-clip: text; color: transparent; }
:deep(.vip-btn-wrapper.is-active .el-radio-button__inner) { border-color: #D4AF37 !important; background-color: #FFFBEB !important; box-shadow: -1px 0 0 0 #D4AF37 !important; color: #333 !important; }
@keyframes floatRocket { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
.animate-fade-in { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>