<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { UploadFilled, DataAnalysis, CircleCheck, Warning, Promotion } from '@element-plus/icons-vue'


// 👇👇👇 新增：控制当前显示 "Vue版" 还是 "Streamlit版"
const currentMode = ref('basic') 
// 👆👆👆 新增结束

const API_BASE = 'http://127.0.0.1:8000'
const fileList = ref([])
const isAnalyzing = ref(false)
const result = ref(null)

const handleExceed = (files) => { fileList.value = [files[0]] }

const handleChange = (file) => {
  fileList.value = [file]
  result.value = null 
}

const startAnalyze = async () => {
  if (fileList.value.length === 0) return ElMessage.warning('请先选择一份简历文件')
  isAnalyzing.value = true
  result.value = null
  const formData = new FormData()
  formData.append('file', fileList.value[0].raw)

  try {
    const res = await axios.post(`${API_BASE}/api/resume/analyze`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
    ElMessage.success('诊断完成！')
  } catch (e) {
    console.error(e)
    ElMessage.error('上传失败，请检查后端是否启动')
  } finally {
    isAnalyzing.value = false
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
            <el-icon class="el-icon--upload">
  <UploadFilled />
</el-icon>

            <div class="el-upload__text">
              将简历拖到此处，或 <em>点击上传</em>
            </div>
          </el-upload>

          <el-button 
            type="primary" 
            size="large" 
            class="analyze-btn"
            :loading="isAnalyzing"
            @click="startAnalyze"
          >
            {{ isAnalyzing ? 'AI 正在诊断中...' : '✨ 开始深度诊断' }}
          </el-button>
        </div>

        <div v-if="result" class="result-section animate-fade-in">
          <div class="summary-card">
            <div class="card-title"><el-icon><DataAnalysis /></el-icon> 综合评价</div>
            <p>{{ result.summary }}</p>
          </div>

          <div class="details-row">
            <div class="detail-col strength">
              <div class="col-header"><el-icon><CircleCheck /></el-icon> 简历亮点</div>
              <ul>
                <li v-for="(item, i) in result.strengths" :key="i">{{ item }}</li>
              </ul>
            </div>

            <div class="detail-col weakness">
              <div class="col-header"><el-icon><Warning /></el-icon> 待改进</div>
              <ul>
                <li v-for="(item, i) in result.weaknesses" :key="i">{{ item }}</li>
              </ul>
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
/* 👇 新增的布局样式 👇 */
.page-wrapper {
  padding: 20px;
}
.mode-switch-header {
  text-align: center;
  margin-bottom: 30px;
}
.vip-container {
  height: 85vh; /* 保证 iframe 够高 */
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.streamlit-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* 👇 下面是你原来的样式 (保持不变) 👇 */
.doctor-container { max-width: 800px; margin: 0 auto; padding-bottom: 50px; }
.header-section { text-align: center; margin-bottom: 30px; }
.header-section h2 { color: #303133; margin-bottom: 10px; }
.header-section p { color: #909399; font-size: 14px; }
.upload-section { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center; }
.analyze-btn { margin-top: 20px; width: 200px; font-weight: bold; background: linear-gradient(135deg, #409EFF, #337ecc); border: none; }
.analyze-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(64,158,255,0.4); }
.result-section { margin-top: 30px; display: flex; flex-direction: column; gap: 20px; }
.summary-card, .suggestion-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.card-title { font-weight: bold; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; color: #303133; }
.details-row { display: flex; gap: 20px; }
.detail-col { flex: 1; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.col-header { font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; gap: 6px; }
.strength .col-header { color: #67C23A; }
.weakness .col-header { color: #E6A23C; }
ul { padding-left: 20px; margin: 0; }
li { margin-bottom: 8px; color: #606266; font-size: 14px; line-height: 1.6; }
.suggestion-item { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
.suggestion-item .index { background: #EBF5FF; color: #409EFF; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0; }
.suggestion-item .text { color: #606266; font-size: 14px; line-height: 1.6; }
.animate-fade-in { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
/* --- 👇 把下面这些加到你的 style 最底下 👇 --- */

.vip-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 小火箭动画 */
.rocket-icon {
  font-size: 18px;
  color: #F59E0B;
  animation: floatRocket 2s ease-in-out infinite;
  margin-right: 4px;
}

/* 文字渐变 */
.vip-text {
  font-weight: 800;
  background: linear-gradient(135deg, #D4AF37 0%, #F59E0B 100%);
  -webkit-background-clip: text;
  color: transparent; 
}

/* 🔥 核心修复：镶金边样式 🔥 */
/* 解释：当 vip-btn-wrapper 处于激活(is-active)状态时，修改它内部的 inner 样式 */
:deep(.vip-btn-wrapper.is-active .el-radio-button__inner) {
  border-color: #D4AF37 !important;
  background-color: #FFFBEB !important;
  box-shadow: -1px 0 0 0 #D4AF37 !important; 
  color: #333 !important; /* 防止文字变白看不清 */
}

@keyframes floatRocket {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
  </style>