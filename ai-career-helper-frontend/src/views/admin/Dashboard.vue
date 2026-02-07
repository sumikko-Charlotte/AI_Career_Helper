<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { User, Document, ChatLineRound, Trophy } from '@element-plus/icons-vue'

// --- 模拟数据 (后续对接后端 API) ---
const stats = ref([
  { title: '总用户数', value: '2,847', icon: User, color: '#409EFF' },
  { title: '简历诊断', value: '1,302', icon: Document, color: '#67C23A' },
  { title: '模拟面试', value: '5,600', icon: ChatLineRound, color: '#E6A23C' },
  { title: '今日新增', value: '+128', icon: Trophy, color: '#F56C6C' },
])

const chartRef = ref(null)
let myChart = null

// --- 初始化图表 (复刻 UI 组的 ECharts 配置) ---
const initChart = () => {
  if (!chartRef.value) return
  myChart = echarts.init(chartRef.value)

  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['9月', '10月', '11月', '12月', '1月', '2月', '3月'],
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    yAxis: {
      type: 'value',
      name: '活跃用户',
      splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
    },
    series: [{
      data: [1800, 2100, 2300, 2500, 2600, 2700, 2847], // 模拟数据
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        borderRadius: [5, 5, 0, 0],
        // 复刻 UI 文件里的渐变色
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#8338ec' }, // 紫色
          { offset: 1, color: '#3a86ff' }  // 蓝色
        ])
      }
    }]
  }
  myChart.setOption(option)
}

// 响应式调整
const handleResize = () => myChart && myChart.resize()

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (myChart) myChart.dispose()
})
</script>

<template>
  <div class="dashboard-container">
    <h2 class="page-title">数据概览 Dashboard</h2>

    <el-row :gutter="20" class="card-row">
      <el-col :span="6" v-for="(item, index) in stats" :key="index">
        <el-card shadow="hover" class="stat-card animate-up">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-title">{{ item.title }}</div>
            </div>
            <div class="stat-icon" :style="{ background: item.color + '20', color: item.color }">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <div class="chart-wrapper animate-up" style="animation-delay: 0.1s">
          <div class="chart-header">
            <h3>平台流量趋势</h3>
            <el-tag type="primary" effect="dark">实时</el-tag>
          </div>
          <div ref="chartRef" style="width: 100%; height: 350px;"></div>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="chart-wrapper animate-up" style="animation-delay: 0.2s">
          <div class="chart-header">
            <h3>热门岗位意向</h3>
          </div>
          <div class="rank-list">
            <div class="rank-item">
              <span class="rank-num top">1</span>
              <span class="rank-name">Java 后端开发</span>
              <span class="rank-val">45%</span>
            </div>
            <div class="rank-item">
              <span class="rank-num top">2</span>
              <span class="rank-name">算法工程师</span>
              <span class="rank-val">30%</span>
            </div>
            <div class="rank-item">
              <span class="rank-num top">3</span>
              <span class="rank-name">前端开发</span>
              <span class="rank-val">15%</span>
            </div>
            <div class="rank-item">
              <span class="rank-num">4</span>
              <span class="rank-name">产品经理</span>
              <span class="rank-val">10%</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page-title { margin-bottom: 20px; color: #303133; font-weight: 700; }

.stat-card { border: none; border-radius: 12px; }
.stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-value { font-size: 28px; font-weight: 800; color: #303133; margin-bottom: 5px; }
.stat-title { font-size: 14px; color: #909399; }
.stat-icon { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }

.chart-wrapper {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  height: 430px;
}
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.chart-header h3 { margin: 0; font-size: 18px; }

/* 排行榜样式 */
.rank-list { padding-top: 10px; }
.rank-item { display: flex; align-items: center; margin-bottom: 20px; font-size: 15px; }
.rank-num { width: 24px; height: 24px; border-radius: 4px; background: #f0f2f5; color: #909399; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: bold; font-size: 12px; }
.rank-num.top { background: #EFE3B2; color: #101C4D; } /* 呼应 UI 设计的金色 */
.rank-name { flex: 1; color: #606266; }
.rank-val { font-weight: bold; color: #303133; }

.animate-up { animation: fadeInUp 0.6s ease backwards; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>