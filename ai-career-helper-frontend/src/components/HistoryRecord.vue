<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Clock, Document, Star, View, Delete, Download, Refresh, Collection } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const loading = ref(false)
const historyList = ref([])
const uploadedKeys = ref([])
const UP_KEY = 'uploaded_resume_tasks'
const API_BASE = import.meta.env.VITE_API_BASE ?? 'https://ai-career-helper-backend-u1s0.onrender.com'
console.debug('[HistoryRecord] API_BASE ->', API_BASE)

// 简历历史记录相关状态
const resumeHistoryList = ref([])
const resumeHistoryLoading = ref(false)
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentDetail = ref({})
const activeTab = ref('resume') // 'resume' 或 'old'，默认显示简历历史记录

// 加载本地上传记录
const loadUploadedLocal = () => {
  try {
    const raw = localStorage.getItem(UP_KEY)
    uploadedKeys.value = raw ? JSON.parse(raw) : []
  } catch (e) { uploadedKeys.value = [] }
}

const saveUploadedLocal = () => {
  localStorage.setItem(UP_KEY, JSON.stringify(uploadedKeys.value))
}

const findUploaded = (item) => {
  // 匹配策略：优先匹配 task_id，如果历史项里无 task_id，则用 username+title+date
  const key = item.task_id || `${(localStorage.getItem('remembered_username') || 'unknown')}_${item.title}_${item.date}`
  return uploadedKeys.value.find(u => u.task_id === key || (u._local_key && u._local_key === key))
}

// 获取旧版历史数据（保留原有功能）
const fetchHistory = async () => {
  loading.value = true
  const username = localStorage.getItem('remembered_username') || '测试用户'
  
  try {
    const res = await axios.get(`${API_BASE}/api/history`, { params: { username } })
    if (res.data.success) {
      historyList.value = res.data.data
    }
  } catch (error) {
    console.error('获取历史失败', error)
  } finally {
    loadUploadedLocal()
    loading.value = false
  }
}

// 获取简历历史记录列表（新增功能）
const getResumeHistoryList = async () => {
  const username = getCurrentUsername()
  if (!username) {
    ElMessage.warning('请先登录')
    return
  }

  resumeHistoryLoading.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/resume/history`, {
      params: { username }
    })
    
    if (res.data.code === 200) {
      resumeHistoryList.value = res.data.data || []
      if (resumeHistoryList.value.length === 0 && activeTab.value === 'resume') {
        ElMessage.info('暂无简历历史记录')
      }
    } else {
      ElMessage.error(res.data.msg || '获取简历历史记录失败')
    }
  } catch (err) {
    console.error('[HistoryRecord] 获取简历历史记录失败:', err)
    if (err.response?.status === 404) {
      ElMessage.error('用户不存在，请重新登录')
    } else if (err.response?.status === 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else {
      ElMessage.error('获取简历历史记录失败，请检查网络连接')
    }
  } finally {
    resumeHistoryLoading.value = false
  }
}

// 获取当前登录用户名
const getCurrentUsername = () => {
  try {
    const loginUserStr = localStorage.getItem('login_user') || sessionStorage.getItem('login_user')
    if (loginUserStr) {
      const loginUser = JSON.parse(loginUserStr)
      return loginUser.username || localStorage.getItem('remembered_username')
    }
    return localStorage.getItem('remembered_username')
  } catch (e) {
    console.warn('[HistoryRecord] 获取用户名失败:', e)
    return localStorage.getItem('remembered_username')
  }
}

// 查看简历历史记录详情
const viewResumeDetail = async (row) => {
  const username = getCurrentUsername()
  if (!username) {
    ElMessage.warning('请先登录')
    return
  }

  detailLoading.value = true
  detailVisible.value = true
  currentDetail.value = {}

  try {
    const res = await axios.get(`${API_BASE}/api/resume/history/${row.id}`, {
      params: { username }
    })
    
    if (res.data.code === 200) {
      currentDetail.value = res.data.data || {}
    } else {
      ElMessage.error(res.data.msg || '获取详情失败')
      detailVisible.value = false
    }
  } catch (err) {
    console.error('[HistoryRecord] 获取详情失败:', err)
    if (err.response?.status === 404) {
      ElMessage.error('记录不存在或无权访问')
    } else if (err.response?.status === 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else {
      ElMessage.error('获取详情失败，请检查网络连接')
    }
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

// 下载简历
const downloadResume = (url) => {
  if (!url || url.startsWith('text_input_')) {
    ElMessage.warning('该记录为文本输入，无文件可下载')
    return
  }

  try {
    // 如果是相对路径，拼接 API_BASE
    const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = fullUrl
    link.download = `简历_${new Date().getTime()}.pdf`
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('下载已开始')
  } catch (err) {
    console.error('[HistoryRecord] 下载失败:', err)
    ElMessage.error('下载失败，请稍后重试')
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
}

// 获取文件名
const getFileName = (url) => {
  if (!url) return '-'
  try {
    const parts = url.split('/')
    return parts[parts.length - 1] || url
  } catch (e) {
    return url
  }
}

// 格式化 AI 分析内容
const formatAnalysis = (analysis) => {
  if (!analysis) {
    return '<p style="color: #999;">暂无分析内容</p>'
  }

  try {
    // 如果 ai_analysis 是对象，尝试提取内容
    if (typeof analysis === 'object') {
      const diagnosis = analysis.diagnosis_report || {}
      const optimized = analysis.optimized_resume || ''
      
      let html = ''
      
      // 诊断报告
      if (diagnosis.score !== undefined) {
        html += `<div class="diagnosis-report">
          <h4 style="color: #165DFF; margin: 15px 0 10px;">📊 诊断报告</h4>
          <p><strong>综合评分：</strong><span style="color: #F56C6C; font-size: 20px; font-weight: bold;">${diagnosis.score}</span> / 100</p>
          <p><strong>综合评价：</strong>${diagnosis.summary || '暂无'}</p>
          ${diagnosis.highlights?.length ? `<p><strong>亮点：</strong>${diagnosis.highlights.join('、')}</p>` : ''}
          ${diagnosis.weaknesses?.length ? `<p><strong>不足：</strong>${diagnosis.weaknesses.join('、')}</p>` : ''}
        </div>`
      }
      
      // 优化简历
      if (optimized) {
        html += `<div class="optimized-resume">
          <h4 style="color: #165DFF; margin: 15px 0 10px;">✨ 优化简历</h4>
          <div>${md.render(optimized)}</div>
        </div>`
      }
      
      return html || '<p style="color: #999;">分析内容格式异常</p>'
    }
    
    // 如果是字符串，尝试解析 JSON
    if (typeof analysis === 'string') {
      try {
        const parsed = JSON.parse(analysis)
        return formatAnalysis(parsed)
      } catch (e) {
        // 如果不是 JSON，直接渲染为 Markdown
        return md.render(analysis)
      }
    }
    
    return md.render(String(analysis))
  } catch (e) {
    console.error('[HistoryRecord] 格式化分析内容失败:', e)
    return `<pre style="white-space: pre-wrap; word-break: break-all;">${String(analysis)}</pre>`
  }
}

// 刷新列表
const refreshList = () => {
  if (activeTab.value === 'resume') {
    getResumeHistoryList()
  } else {
    fetchHistory()
  }
}

// 切换标签页
const handleTabChange = (tab) => {
  activeTab.value = tab
  if (tab === 'resume') {
    getResumeHistoryList()
  } else {
    fetchHistory()
  }
}

const confirmUploadToggle = async (item, toOn) => {
  const username = localStorage.getItem('remembered_username') || '测试用户'
  if (toOn) {
    try {
      await ElMessageBox.confirm('确认将该记录上传至 Admin？上传后会在 Admin 端展示，并在 CSV 中计入统计。', '确认上传', { type: 'warning' })
    } catch { return }

    // 构造上传记录
    const localKey = item.task_id || `${username}_${item.title}_${item.date}`
    const payload = {
      username,
      task_id: localKey,
      filename: item.filename || (item.title ? (item.title + '.pdf') : 'resume.pdf'),
      report: item.report || ('# 简历报告\n- 标题：' + item.title + '\n- 评分：' + (item.score || 0)),
      score: item.score || 0,
      date: item.date || new Date().toISOString()
    }

    try {
      const res = await axios.post(`${API_BASE}/api/resume/upload`, payload)
      if (res.data.success) {
        // 本地添加一份记录并保存
        const rec = { ...payload, _local_key: localKey }
        uploadedKeys.value.unshift(rec)
        saveUploadedLocal()
        // 调用后端增加用户任务数统计
        await axios.post(`${API_BASE}/api/user/addTask`, null, { params: { username } })
        ElMessage({ type: 'success', message: '简历已上传至 Admin' })
      } else {
        ElMessage({ type: 'error', message: '上传失败：' + (res.data.message || '') })
      }
    } catch (e) {
      ElMessage({ type: 'error', message: '上传失败：' + e.message })
    }
  } else {
    try {
      await ElMessageBox.confirm('确认取消上传并从 Admin 下线此份记录？此操作可恢复。', '取消上传', { type: 'warning' })
    } catch { return }

    // 找到本地记录并删除，同时请求后端删除
    const localKey = item.task_id || `${username}_${item.title}_${item.date}`
    const idx = uploadedKeys.value.findIndex(u => u._local_key === localKey || u.task_id === localKey)
    if (idx >= 0) {
      const target = uploadedKeys.value[idx]
      try {
        await axios.post(`${API_BASE}/api/resume/delete`, null, { params: { username, task_id: target.task_id || localKey } })
      } catch (e) { console.warn('后端删除同步失败', e) }
      uploadedKeys.value.splice(idx, 1)
      saveUploadedLocal()
      ElMessage({ type: 'info', message: '上传已取消' })
    } else {
      ElMessage({ type: 'info', message: '本地未找到上传记录' })
    }
  }
}

onMounted(() => {
  // 默认加载简历历史记录
  getResumeHistoryList()
  // 同时加载旧版历史记录（如果需要）
  // fetchHistory()
})
</script>

<template>
  <div class="history-container">
    <div class="page-header">
      <h2><el-icon><Clock /></el-icon> 历史诊断记录</h2>
      <p>查看您所有的简历润色与诊断记录存档</p>
    </div>

    <!-- 标签页切换 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="history-tabs">
      <el-tab-pane label="简历历史记录" name="resume">
        <div v-loading="resumeHistoryLoading" class="record-list">
          <el-empty v-if="resumeHistoryList.length === 0 && !resumeHistoryLoading" description="暂无简历历史记录，快去上传一份简历吧！">
            <el-button type="primary" @click="$router.push('/app')">去上传简历</el-button>
          </el-empty>

          <div v-for="(item, index) in resumeHistoryList" :key="index" class="record-card animate-up">
            <div class="card-left">
              <div class="icon-box">
                <el-icon><Document /></el-icon>
              </div>
              <div class="info">
                <div class="title">
                  {{ item.resume_file_url && !item.resume_file_url.startsWith('text_input_') ? getFileName(item.resume_file_url) : '文本输入简历' }}
                </div>
                <div class="meta">
                  <el-tag :type="item.resume_type === 'vip' ? 'danger' : 'primary'" size="small">
                    {{ item.resume_type === 'vip' ? 'VIP简历' : '普通简历' }}
                  </el-tag>
                  <span class="date">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
            </div>

            <div class="card-right">
              <div class="actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="viewResumeDetail(item)"
                  :icon="View"
                >
                  查看详情
                </el-button>
                <el-button 
                  v-if="item.resume_file_url && !item.resume_file_url.startsWith('text_input_')"
                  type="success" 
                  size="small" 
                  @click="downloadResume(item.resume_file_url)"
                  :icon="Download"
                >
                  下载
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="旧版历史记录" name="old">
        <div v-loading="loading" class="record-list">
          <el-empty v-if="historyList.length === 0" description="暂无历史记录，快去诊断一份简历吧！" />

          <div v-for="(item, index) in historyList" :key="index" class="record-card animate-up">
            <div class="card-left">
              <div class="icon-box">
                <el-icon><Document /></el-icon>
              </div>
              <div class="info">
                <div class="title">{{ item.title }}</div>
                <div class="meta">
                  <el-tag size="small" :type="item.action_type === '生成' ? 'success' : ''">{{ item.action_type }}</el-tag>
                  <span class="date">{{ item.date }}</span>
                </div>
              </div>
            </div>

            <div class="card-right">
              <div class="score-box" v-if="item.score">
                <span class="score-num">{{ item.score }}</span>
                <span class="score-label">分</span>
              </div>
              <div class="actions">
                <div style="display:flex; align-items:center; gap:10px">
                  <el-tag v-if="findUploaded(item)" size="small" type="success">已上传</el-tag>
                  <el-tag v-else size="small">未上传</el-tag>
                  <el-switch :model-value="!!findUploaded(item)" @change="(v) => { confirmUploadToggle(item, v) }" active-text="已上传" inactive-text="未上传" active-color="#13ce66" inactive-color="#c0c4cc" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 刷新按钮 -->
    <div class="refresh-btn">
      <el-button type="primary" :icon="Refresh" @click="refreshList" circle />
    </div>

    <!-- 简历历史记录详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="简历分析详情"
      width="85%"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-loading="detailLoading" class="detail-content">
        <!-- 基本信息 -->
        <div class="info-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="上传时间">
              {{ formatDate(currentDetail.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="简历类型">
              <el-tag :type="currentDetail.resume_type === 'vip' ? 'danger' : 'primary'">
                {{ currentDetail.resume_type === 'vip' ? 'VIP简历' : '普通简历' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="简历文件" :span="2">
              <span v-if="currentDetail.resume_file_url && !currentDetail.resume_file_url.startsWith('text_input_')">
                {{ getFileName(currentDetail.resume_file_url) }}
                <el-button 
                  type="primary" 
                  size="small" 
                  style="margin-left: 10px;"
                  @click="downloadResume(currentDetail.resume_file_url)"
                  :icon="Download"
                >
                  下载简历
                </el-button>
              </span>
              <el-tag v-else type="info">文本输入（无文件）</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- AI分析内容 -->
        <div class="analysis-section">
          <h3 style="margin: 20px 0 15px; color: #165DFF; font-size: 18px; font-weight: 600;">
            <el-icon style="vertical-align: middle; margin-right: 5px;"><Document /></el-icon>
            AI 分析报告
          </h3>
          <div 
            class="analysis-content" 
            v-html="formatAnalysis(currentDetail.ai_analysis)"
          ></div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button 
          v-if="currentDetail.resume_file_url && !currentDetail.resume_file_url.startsWith('text_input_')"
          type="primary" 
          @click="downloadResume(currentDetail.resume_file_url)"
        >
          下载简历
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.history-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

.page-header {
  margin-bottom: 30px;
}
.page-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}
.page-header p {
  color: #909399;
  font-size: 14px;
}

.history-tabs {
  margin-bottom: 20px;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 200px;
}

.record-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #ebeef5;
}

.record-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.icon-box {
  width: 48px;
  height: 48px;
  background: #ecf5ff;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #409EFF;
  font-size: 24px;
}

.info .title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 6px;
}

.info .meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date {
  font-size: 13px;
  color: #909399;
}

.card-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.score-box {
  text-align: right;
}
.score-num {
  font-size: 20px;
  font-weight: 800;
  color: #67C23A;
}
.score-label {
  font-size: 12px;
  color: #909399;
  margin-left: 2px;
}

.actions {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
}

.animate-up {
  animation: fadeUp 0.5s ease-out;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 详情弹窗样式 */
.detail-content {
  padding: 10px 0;
  max-height: 70vh;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 30px;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
}

.analysis-section {
  margin-top: 20px;
}

.analysis-content {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  line-height: 1.8;
  font-size: 14px;
  color: #333;
}

.analysis-content :deep(h1),
.analysis-content :deep(h2),
.analysis-content :deep(h3),
.analysis-content :deep(h4) {
  color: #165DFF;
  margin-top: 20px;
  margin-bottom: 10px;
}

.analysis-content :deep(p) {
  margin: 10px 0;
}

.analysis-content :deep(ul),
.analysis-content :deep(ol) {
  margin: 10px 0;
  padding-left: 30px;
}

.analysis-content :deep(li) {
  margin: 5px 0;
}

.analysis-content :deep(code) {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.analysis-content :deep(pre) {
  background: #f4f4f5;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
}

.analysis-content :deep(blockquote) {
  border-left: 4px solid #165DFF;
  padding-left: 15px;
  margin: 15px 0;
  color: #666;
}

.diagnosis-report {
  padding: 15px;
  background: #f0f9ff;
  border-left: 4px solid #165DFF;
  margin-bottom: 20px;
  border-radius: 4px;
}

.optimized-resume {
  padding: 15px;
  background: #f9fafb;
  border-radius: 4px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .history-container {
    padding: 10px;
  }
  
  .detail-content {
    max-height: 60vh;
  }
  
  .refresh-btn {
    bottom: 20px;
    right: 20px;
  }
}
</style>
