<template>
  <div class="resume-history">
    <!-- 页面头部 -->
    <el-page-header @back="handleBack" style="margin-bottom: 20px;">
      <template #content>
        <span style="font-size: 20px; font-weight: 600; color: #165DFF;">📋 简历历史记录</span>
      </template>
    </el-page-header>

    <!-- 历史记录列表 -->
    <el-card v-loading="loading" shadow="hover" class="history-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: 600;">我的简历分析记录</span>
          <el-button type="primary" size="small" @click="refreshList" :icon="Refresh">
            刷新
          </el-button>
        </div>
      </template>

      <!-- 表格 -->
      <el-table 
        :data="historyList" 
        border 
        style="width: 100%"
        :empty-text="loading ? '加载中...' : '暂无简历上传记录'"
        stripe
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="created_at" label="上传时间" width="200" align="center" sortable>
          <template #default="scope">
            <span>{{ formatDate(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="resume_type" label="简历类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.resume_type === 'vip' ? 'danger' : 'primary'" size="large">
              {{ scope.row.resume_type === 'vip' ? 'VIP简历' : '普通简历' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resume_file_url" label="简历文件" min-width="200">
          <template #default="scope">
            <span v-if="scope.row.resume_file_url && !scope.row.resume_file_url.startsWith('text_input_')">
              {{ getFileName(scope.row.resume_file_url) }}
            </span>
            <el-tag v-else type="info" size="small">文本输入</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewDetail(scope.row)"
              :icon="View"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据提示 -->
      <div v-if="historyList.length === 0 && !loading" class="empty-tip">
        <el-empty description="暂无简历上传记录">
          <el-button type="primary" @click="goToResumeDoctor">
            去上传简历
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 详情弹窗 -->
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

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { View, Download, Refresh, Document } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'

// 路由
const router = useRouter()

// API 配置
const API_BASE = import.meta.env.VITE_API_BASE ?? 'https://ai-career-helper-backend-u1s0.onrender.com'
console.debug('[ResumeHistory] API_BASE ->', API_BASE)

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 状态管理
const loading = ref(false)
const detailLoading = ref(false)
const historyList = ref([])
const detailVisible = ref(false)
const currentDetail = ref({})

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
    console.warn('[ResumeHistory] 获取用户名失败:', e)
    return localStorage.getItem('remembered_username')
  }
}

// 获取历史记录列表
const getHistoryList = async () => {
  const username = getCurrentUsername()
  if (!username) {
    ElMessage.warning('请先登录')
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/resume/history`, {
      params: { username }
    })
    
    if (res.data.code === 200) {
      historyList.value = res.data.data || []
      if (historyList.value.length === 0) {
        ElMessage.info('暂无历史记录')
      } else {
        ElMessage.success(`加载成功，共 ${historyList.value.length} 条记录`)
      }
    } else {
      ElMessage.error(res.data.msg || '获取历史记录失败')
    }
  } catch (err) {
    console.error('[ResumeHistory] 获取历史记录失败:', err)
    if (err.response?.status === 404) {
      ElMessage.error('用户不存在，请重新登录')
    } else if (err.response?.status === 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else {
      ElMessage.error('获取历史记录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

// 刷新列表
const refreshList = () => {
  getHistoryList()
}

// 查看详情
const viewDetail = async (row) => {
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
    console.error('[ResumeHistory] 获取详情失败:', err)
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
    console.error('[ResumeHistory] 下载失败:', err)
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
    console.error('[ResumeHistory] 格式化分析内容失败:', e)
    return `<pre style="white-space: pre-wrap; word-break: break-all;">${String(analysis)}</pre>`
  }
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

// 跳转到简历医生
const goToResumeDoctor = () => {
  router.push('/app')
}

// 页面初始化
onMounted(() => {
  getHistoryList()
})
</script>

<style scoped>
.resume-history {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

.history-card {
  margin-top: 20px;
}

.empty-tip {
  text-align: center;
  padding: 60px 20px;
}

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
  .resume-history {
    padding: 10px;
  }
  
  .detail-content {
    max-height: 60vh;
  }
}
</style>
