<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Clock, Document, Star, View, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const historyList = ref([])
const API_BASE = 'http://127.0.0.1:8000'

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
    loading.value = false
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
            <el-button circle :icon="View" title="查看详情" />
            <el-button circle :icon="Star" title="收藏" />
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