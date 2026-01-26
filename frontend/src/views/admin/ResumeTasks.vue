<script setup>
import { ref, onMounted } from 'vue'
import { DocumentCopy, Timer, Search, RefreshRight } from '@element-plus/icons-vue'

const loading = ref(false)
const tasks = ref([])

// --- 模拟任务数据 ---
const mockTasks = [
  { id: 'T-20260125-01', user: '张三', filename: '张三_算法实习.pdf', score: 85, time: '10:23:45', status: 'completed' },
  { id: 'T-20260125-02', user: '李四', filename: '李四_Java后端.docx', score: 72, time: '10:25:12', status: 'completed' },
  { id: 'T-20260125-03', user: '王五', filename: '我的简历v2.pdf', score: 0, time: '10:28:00', status: 'processing' },
  { id: 'T-20260125-04', user: '赵六', filename: '赵六_产品经理.pdf', score: 91, time: '10:30:55', status: 'completed' },
  { id: 'T-20260125-05', user: '访客', filename: '未命名简历.pdf', score: 0, time: '10:32:10', status: 'failed' },
]

const fetchTasks = () => {
  loading.value = true
  // 模拟刷新
  setTimeout(() => {
    tasks.value = mockTasks
    loading.value = false
  }, 800)
}

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

onMounted(() => fetchTasks())
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
      <el-button circle :icon="RefreshRight" @click="fetchTasks" title="刷新列表" />
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <span class="label">今日任务</span>
        <span class="value">128</span>
      </div>
      <div class="stat-item">
        <span class="label">成功率</span>
        <span class="value success">98.5%</span>
      </div>
      <div class="stat-item">
        <span class="label">平均耗时</span>
        <span class="value primary">12s</span>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="任务ID" width="160">
          <template #default="scope">
            <span class="task-id">{{ scope.row.id }}</span>
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

        <el-table-column prop="user" label="提交用户" width="120" />

        <el-table-column label="AI 评分" width="120" align="center">
          <template #default="scope">
            <span v-if="scope.row.status === 'completed'" class="score-num" :class="{ high: scope.row.score >= 85 }">
              {{ scope.row.score }}
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

        <el-table-column prop="time" label="提交时间" width="120" align="right">
          <template #default="scope">
            <div class="time-cell">
              <el-icon><Timer /></el-icon> {{ scope.row.time }}
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
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