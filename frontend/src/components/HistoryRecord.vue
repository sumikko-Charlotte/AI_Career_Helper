<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Clock, Document, Star, View, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const loading = ref(false)
const historyList = ref([])
const uploadedKeys = ref([])
const UP_KEY = 'uploaded_resume_tasks'
const API_BASE = import.meta.env.VITE_API_BASE ?? ''
console.debug('[HistoryRecord] API_BASE ->', API_BASE)

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

// 获取历史数据
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
  fetchHistory()
})
</script>

<template>
  <div class="history-container">
    <div class="page-header">
      <h2><el-icon><Clock /></el-icon> 历史诊断记录</h2>
      <p>查看您所有的简历润色与诊断记录存档</p>
    </div>

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
  </div>
</template>

<style scoped>
.history-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
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

.record-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
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

.animate-up {
  animation: fadeUp 0.5s ease-out;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>