<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { DocumentCopy, Timer, Search, RefreshRight } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const loading = ref(false)
const tasks = ref([])
const uploadedTasks = ref([])
const viewReportDialog = ref(false)
const currentReport = ref('')
const filterStatus = ref('all')
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

// 本地任务存储 key: competition_resume_task_list
const TASK_KEY = 'competition_resume_task_list'

const DEFAULT_TASKS = [
  { id: 'T-20260125-01', user: '张三', user_id: 1001, filename: '张三 - 算法实习 - 校招简历.pdf', score: 85.2, submit_time: '2026-01-25 10:23:45', status: 'completed', report: '# 诊断报告\n\n- 分数：85.2\n- 建议：强化项目经验与算法题目练习' },
  { id: 'T-20260125-02', user: '李四', user_id: 1002, filename: '李四 - Java后端.docx', score: 72.5, submit_time: '2026-01-25 10:25:12', status: 'completed', report: '# 诊断报告\n\n- 分数：72.5\n- 建议：补充项目经历，优化描述' },
  { id: 'T-20260125-03', user: '王五', user_id: 1003, filename: '王五 - 前端 - 校园简历.pdf', score: 0, submit_time: '2026-01-25 10:28:00', status: 'processing', report: '' },
]

const fetchTasks = () => {
  loading.value = true
  setTimeout(() => {
    try {
      const raw = localStorage.getItem(TASK_KEY)
      if (raw) tasks.value = JSON.parse(raw)
      else { tasks.value = DEFAULT_TASKS; localStorage.setItem(TASK_KEY, JSON.stringify(DEFAULT_TASKS)) }
    } catch (e) { console.error('读取任务失败', e); tasks.value = DEFAULT_TASKS }
    loading.value = false
  }, 300)
}

const fetchUploaded = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/resume/getUploadedList`)
    if (res.data.success) {
      uploadedTasks.value = res.data.data
    }
  } catch (e) { console.warn('获取已上传列表失败', e); uploadedTasks.value = [] }
}

// 监听全局事件，实时刷新
window.addEventListener('competitionDataChanged', () => { fetchTasks(); fetchUploaded() })

const getStatusType = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'processing') return 'primary'
  return 'danger'
}
const getStatusLabel = (status) => {
  if (status === 'completed') return '诊断完成'
  if (status === 'processing') return 'AI 分析中...'
  return '失败'
}

const getTodayUploadedCount = () => {
  const today = new Date().toISOString().slice(0,10)
  return uploadedTasks.value.filter(u => (u.date || '').startsWith(today)).length
}

const getSuccessRate = () => {
  const uploadedIds = uploadedTasks.value.map(u => u.task_id)
  const uploadedCompleted = tasks.value.filter(t => uploadedIds.includes(t.id) && t.status === 'completed').length
  return ((uploadedCompleted / Math.max(1, uploadedIds.length)) * 100).toFixed(1)
}

const simpleMarkdownToHtml = (md) => {
  if (!md) return ''
  // very light conversion for headings and line breaks
  let html = md.replace(/^# (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/\n\s*-\s/g, '<br>• ')
  html = html.replace(/\n/g, '<br>')
  return html
}

const viewReport = (row) => {
  if (!row) return
  // 查找是否为已上传任务
  const uploaded = uploadedTasks.value.find(u => u.task_id === row.id || (u.filename === row.filename && u.username === row.user))
  if (!uploaded) {
    ElMessage({ type: 'info', message: '用户未上传简历' })
    return
  }
  // 显示上传的报告（后端/CSV 里的内容优先）
  if (!uploaded.report) currentReport.value = '<div>暂无诊断报告</div>'
  else currentReport.value = simpleMarkdownToHtml(uploaded.report)
  viewReportDialog.value = true
}

const deleteTask = (row) => {
  if (!row) return
  ElMessageBox.confirm('确认删除任务：' + row.id + '？此操作不可恢复。', '删除确认', {
    type: 'warning'
  }).then(async () => {
    const idx = tasks.value.findIndex(t => t.id === row.id)
    if (idx >= 0) tasks.value.splice(idx, 1)
    // 如果该任务在已上传列表中，也请求后端删除
    const uploaded = uploadedTasks.value.find(u => u.task_id === row.id || (u.filename === row.filename && u.username === row.user))
    if (uploaded) {
      try {
        await axios.post(`${API_BASE}/api/resume/delete`, null, { params: { username: uploaded.username, task_id: uploaded.task_id || row.id } })
        // 从本地 uploaded_resume_tasks 同步移除（若存在）
        try {
          const raw = localStorage.getItem('uploaded_resume_tasks')
          if (raw) {
            const arr = JSON.parse(raw).filter(u => u.task_id !== (uploaded.task_id || row.id))
            localStorage.setItem('uploaded_resume_tasks', JSON.stringify(arr))
          }
        } catch (e) { console.warn('本地删除同步失败', e) }
        // 触发刷新
        await fetchUploaded()
      } catch (e) { console.warn('删除已上传记录失败', e) }
    }

    try {
      localStorage.setItem(TASK_KEY, JSON.stringify(tasks.value))
      // 通知其他窗体或组件刷新
      window.dispatchEvent(new Event('competitionDataChanged'))
      ElMessage({ type: 'success', message: '删除成功' })
    } catch (e) { ElMessage({ type: 'error', message: '删除失败：' + e.message }) }
  }).catch(() => {})
}

// 修复点：copyReport 支持直接接收行对象，并优先使用已上传记录中的报告内容（如果存在）
const copyReport = async (row) => {
  try {
    if (!row) return ElMessage({ type: 'info', message: '未指定要复制的任务' })

    // 优先查找后端已上传的报告
    const uploaded = uploadedTasks.value.find(u => u.task_id === row.id || (u.filename === row.filename && u.username === row.user))
    let reportMd = ''
    if (uploaded && uploaded.report) reportMd = uploaded.report
    else if (row.report) reportMd = row.report
    else return ElMessage({ type: 'info', message: '暂无诊断报告可复制' })

    // 使用现有的简单 Markdown 转换器以提取纯文本
    const html = simpleMarkdownToHtml(reportMd)
    const tmp = document.createElement('div')
    tmp.innerHTML = html
    await navigator.clipboard.writeText(tmp.innerText || tmp.textContent || '')
    ElMessage({ type: 'success', message: '报告内容已复制到剪切板' })
  } catch (e) {
    ElMessage({ type: 'error', message: '复制失败：' + e.message })
  }
}

onMounted(() => { fetchTasks(); fetchUploaded() })
</script>

<template>
  <div class="page-container animate-fade-in">
    <div class="header-section">
      <div class="title-group">
        <div class="icon-box" style="background: linear-gradient(135deg, #059669 0%, #10b981 100%);">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <div>
          <h2 class="page-title">简历任务监控</h2>
          <p class="page-subtitle">实时监控全平台 AI 简历诊断任务队列与结果</p>
        </div>
      </div>
      <div style="display:flex; gap:10px; align-items:center">
        <el-select v-model="filterStatus" placeholder="筛选状态" size="small" clearable style="width:160px">
          <el-option label="全部" value="all" />
          <el-option label="诊断中" value="processing" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button circle :icon="RefreshRight" @click="fetchTasks" title="刷新列表" />
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <span class="label">今日任务</span>
        <span class="value">{{ tasks.length }}</span>
      </div>
      <div class="stat-item">
        <span class="label">今日上传简历数</span>
        <span class="value success">{{ getTodayUploadedCount() }}</span>
      </div>
      <div class="stat-item">
        <span class="label">成功率 (仅统计已上传)</span>
        <span class="value primary">{{ getSuccessRate() }}%</span>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="filterStatus === 'all' ? tasks : tasks.filter(t => t.status === filterStatus)" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="任务ID" width="160">
          <template #default="scope">
            <span class="task-id">{{ scope.row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column label="上传状态" width="140" align="center">
          <template #default="scope">
            <el-tag v-if="uploadedTasks.find(u => u.task_id === scope.row.id || (u.filename === scope.row.filename && u.username === scope.row.user))" type="success">已上传</el-tag>
            <el-tag v-else type="info">用户未上传</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="filename" label="简历文件名" min-width="200">
          <template #default="scope">
             <div class="file-cell">
               <el-icon color="#909399"><DocumentCopy /></el-icon>
               <span>{{ scope.row.filename }}</span>
             </div>
          </template>
        </el-table-column>

        <el-table-column prop="user" label="提交用户" width="140">
          <template #default="scope">
            <div style="display:flex; flex-direction:column;">
              <span style="font-weight:700">{{ scope.row.user }}</span>
              <span style="color:#94a3b8; font-size:12px">UID: {{ scope.row.user_id || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="AI 评分" width="120" align="center">
          <template #default="scope">
            <span v-if="scope.row.status === 'completed'" class="score-num" :class="{ high: scope.row.score >= 85 }">
              {{ scope.row.score.toFixed(1) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="140">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="light" size="small" round>
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="submit_time" label="提交时间" width="160" align="center">
          <template #default="scope">
            <div class="time-cell">
              <el-icon><Timer /></el-icon> {{ scope.row.submit_time }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" align="center" fixed="right">
          <!-- 修复点：使用标准的 scoped slot 语法 #default="{ scope }"，并添加中文注释标记 -->
          <template #default="{ scope }">
            <!-- 修复点：将非法的 @click 表达式替换为标准的方法调用，并将 scope.row 作为参数传入 -->
            <el-button size="small" type="primary" plain @click="viewReport(scope.row)">查看报告</el-button>

            <!-- 复制报告内容按钮：直接传入当前行，函数会读取已上传或本地报告并复制 -->
            <el-button size="small" type="info" plain @click="copyReport(scope.row)">复制报告内容</el-button>

            <!-- 删除任务按钮：保持原有业务逻辑，传入当前行 -->
            <el-button size="small" type="danger" plain @click="deleteTask(scope.row)">删除任务</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :visible.sync="viewReportDialog" width="700px" title="诊断报告">
      <div v-if="currentReport" class="markdown-body" v-html="currentReport"></div>
      <div v-else>暂无诊断报告</div>
      <template #footer>
        <el-button @click="viewReportDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 复用部分基础样式 */
.page-container { padding: 10px; min-height: 100%; display: flex; flex-direction: column; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title-group { display: flex; align-items: center; gap: 15px; }
.icon-box {
  width: 48px; height: 48px; border-radius: 12px; color: white;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.page-title { margin: 0; font-size: 22px; color: #101C4D; font-weight: 800; }
.page-subtitle { margin: 4px 0 0 0; color: #64748b; font-size: 13px; }

/* 统计行 */
.stats-row { 
  display: flex; gap: 40px; margin-bottom: 20px; padding: 15px 25px; 
  background: white; border-radius: 12px; border: 1px solid #f1f5f9;
  width: fit-content;
}
.stat-item { display: flex; flex-direction: column; gap: 5px; }
.stat-item .label { font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.stat-item .value { font-size: 20px; font-weight: 800; color: #1e293b; }
.stat-item .value.success { color: #10b981; }
.stat-item .value.primary { color: #3b82f6; }

/* 表格样式 */
.table-card { border-radius: 16px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.task-id { font-family: monospace; color: #64748b; font-size: 12px; }
.file-cell { display: flex; align-items: center; gap: 8px; font-weight: 500; color: #334155; }
.score-num { font-weight: 800; color: #f59e0b; }
.score-num.high { color: #10b981; }
.time-cell { display: flex; align-items: center; gap: 4px; color: #94a3b8; font-size: 13px; }

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>