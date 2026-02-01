<template>
  <div class="explore-page">
    <div class="header-bar">
      <div class="brand-title">职航——探索</div>
    </div>

    <div class="content">
      <h2 class="page-title">功能导航 · 新手指引</h2>
      <p class="subtitle">根据大学生生涯阶段划分四个功能板块，帮助你快速找到适配资源。</p>

      <el-row :gutter="20" class="phase-row" type="flex">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="6">
          <el-card class="phase-card" shadow="hover">
            <div class="phase-header">
              <div class="phase-title">探索期</div>
              <div class="phase-desc">找准职业方向，积累基础认知</div>
            </div>
            <div class="phase-items">
              <el-tooltip content="生成个性化生涯路径建议，适合处在探索期的同学" placement="top" effect="dark">
                <div class="item" @click="navTo('roadmap')">
                  <el-icon><Compass /></el-icon>
                  <span>生涯路径规划</span>
                </div>
              </el-tooltip>

              <el-tooltip content="完成职业倾向题并生成倾向报告，适合探索职业方向的学生" placement="top" effect="dark">
                <div class="item" @click="navTo('virtual')">
                  <el-icon><VideoPlay /></el-icon>
                  <span>虚拟职业企业</span>
                </div>
              </el-tooltip>

              <el-tooltip content="甄选简历模板，快速搭建第一版简历" placement="top" effect="dark">
                <div class="item" @click="navTo('templates')">
                  <el-icon><Collection /></el-icon>
                  <span>简历模板库</span>
                </div>
              </el-tooltip>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="6">
          <el-card class="phase-card" shadow="hover">
            <div class="phase-header">
              <div class="phase-title">提升期</div>
              <div class="phase-desc">打磨求职材料，提升核心竞争力</div>
            </div>
            <div class="phase-items">
              <el-tooltip content="AI 辅助简历诊断，提升简历质量" placement="top" effect="dark">
                <div class="item" @click="navTo('resume')">
                  <el-icon><DocumentChecked /></el-icon>
                  <span>AI 简历</span>
                </div>
              </el-tooltip>

              <el-tooltip content="沙盘化的竞争力推演，帮助你发现能力短板" placement="top" effect="dark">
                <div class="item" @click="navTo('sandbox')">
                  <el-icon><Odometer /></el-icon>
                  <span>竞争力沙盘</span>
                </div>
              </el-tooltip>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="6">
          <el-card class="phase-card" shadow="hover">
            <div class="phase-header">
              <div class="phase-title">冲刺期</div>
              <div class="phase-desc">模拟实战面试，完成求职冲刺</div>
            </div>
            <div class="phase-items">
              <el-tooltip content="与 AI 模拟面试，对话式练习并获取追问建议" placement="top" effect="dark">
                <div class="item" @click="navTo('interview')">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>模拟面试</span>
                </div>
              </el-tooltip>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="6">
          <el-card class="phase-card" shadow="hover">
            <div class="phase-header">
              <div class="phase-title">个人管理</div>
              <div class="phase-desc">管理使用记录，维护个人信息</div>
            </div>
            <div class="phase-items">
              <el-tooltip content="查看你的历史记录（诊断/生成等），支持归档与管理" placement="top" effect="dark">
                <div class="item" @click="navTo('history')">
                  <el-icon><Calendar /></el-icon>
                  <span>历史记录</span>
                </div>
              </el-tooltip>

              <el-tooltip content="维护你的个人信息与头像设置" placement="top" effect="dark">
                <div class="item" @click="navTo('profile')">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </div>
              </el-tooltip>
            </div>
          </el-card>
        </el-col>
      </el-row>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElRow, ElCol, ElCard, ElTooltip, ElIcon } from 'element-plus'
import { Compass, VideoPlay, Collection, DocumentChecked, Odometer, ChatDotRound, Calendar, User } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const navTo = (key) => {
  // 统一跳转策略：如果功能有独立路由就直接 push；否则 push 到功能页(/app)并携带 focus 查询参数，App.vue 会处理
  switch (key) {
    case 'roadmap':
      router.push({ path: '/app', query: { focus: '0' } })
      break
    case 'virtual':
      router.push('/virtual-experiment')
      break
    case 'templates':
      router.push({ path: '/app', query: { focus: '6' } })
      break
    case 'resume':
      router.push({ path: '/app', query: { focus: '1' } })
      break
    case 'sandbox':
      router.push({ path: '/app', query: { focus: '3' } })
      break
    case 'interview':
      router.push({ path: '/app', query: { focus: '2' } })
      break
    case 'history':
      router.push('/history')
      break
    case 'profile':
      router.push({ path: '/app', query: { focus: '4' } })
      break
    default:
      router.push('/app')
  }
}
</script>

<style scoped>
/* ==========================================
   页面整体布局 - 新增蓝色渐变背景
   ========================================== */
.explore-page {
  min-height: 100vh;
  padding: 32px 24px;
  background: linear-gradient(135deg, #0A1A40 0%, #1e293b 50%, #4A6FA5 100%);
  position: relative;
  overflow: hidden;
}

/* 新增：背景装饰光效 */
.explore-page::before {
  content: '';
  position: absolute;
  top: -20%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(74, 137, 220, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite;
  z-index: 0;
}

.explore-page::after {
  content: '';
  position: absolute;
  bottom: -15%;
  left: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 10s ease-in-out infinite reverse;
  z-index: 0;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

/* ==========================================
   顶部标题栏 - 美化样式
   ========================================== */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

/* 修改：品牌标题使用蓝色渐变文字 */
.brand-title {
  font-weight: 700;
  font-size: 20px;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.link-btn {
  background: transparent;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  transition: color 0.3s ease;
}

.link-btn:hover {
  color: #a78bfa;
}

/* ==========================================
   内容区域 - 玻璃态卡片效果
   ========================================== */
.content {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  padding: 32px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

/* 修改：页面标题使用白色，增加阴影 */
.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

/* 修改：副标题使用浅蓝色 */
.subtitle {
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 32px;
  font-size: 15px;
  line-height: 1.6;
}

/* ==========================================
   阶段卡片 - 渐变背景与边框
   ========================================== */
.phase-row {
  margin-top: 8px;
}

/* 修改：卡片基础样式 */
.phase-card {
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 新增：探索期（绿色系）- 第一个卡片 */
.phase-row .el-col:nth-child(1) .phase-card {
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 8px 32px rgba(16, 185, 129, 0.15);
}

.phase-row .el-col:nth-child(1) .phase-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.5);
}

.phase-row .el-col:nth-child(1) .phase-card::before {
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.6), transparent);
}

/* 新增：提升期（橙色系）- 第二个卡片 */
.phase-row .el-col:nth-child(2) .phase-card {
  border: 1px solid rgba(245, 158, 11, 0.3);
  box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
}

.phase-row .el-col:nth-child(2) .phase-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(245, 158, 11, 0.3);
  border-color: rgba(245, 158, 11, 0.5);
}

.phase-row .el-col:nth-child(2) .phase-card::before {
  background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.6), transparent);
}

/* 新增：冲刺期（紫色系）- 第三个卡片 */
.phase-row .el-col:nth-child(3) .phase-card {
  border: 1px solid rgba(139, 92, 246, 0.3);
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
}

.phase-row .el-col:nth-child(3) .phase-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.5);
}

.phase-row .el-col:nth-child(3) .phase-card::before {
  background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.6), transparent);
}

/* 新增：个人管理（蓝色系）- 第四个卡片 */
.phase-row .el-col:nth-child(4) .phase-card {
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
}

.phase-row .el-col:nth-child(4) .phase-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.5);
}

.phase-row .el-col:nth-child(4) .phase-card::before {
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent);
}

/* 新增：卡片内部光效（通用） */
.phase-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.phase-card:hover::before {
  opacity: 1;
}

/* ==========================================
   阶段标题区域 - 美化样式
   ========================================== */
.phase-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  position: relative;
}

/* 新增：探索期标题底部边框（绿色） */
.phase-row .el-col:nth-child(1) .phase-header {
  border-bottom: 1px solid rgba(16, 185, 129, 0.3);
}

/* 新增：提升期标题底部边框（橙色） */
.phase-row .el-col:nth-child(2) .phase-header {
  border-bottom: 1px solid rgba(245, 158, 11, 0.3);
}

/* 新增：冲刺期标题底部边框（紫色） */
.phase-row .el-col:nth-child(3) .phase-header {
  border-bottom: 1px solid rgba(139, 92, 246, 0.3);
}

/* 新增：个人管理标题底部边框（蓝色） */
.phase-row .el-col:nth-child(4) .phase-header {
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
}

/* 修改：阶段标题使用白色，加粗 */
.phase-title {
  font-weight: 700;
  font-size: 16px;
  color: #ffffff;
  margin-bottom: 6px;
  letter-spacing: 0.3px;
}

/* 修改：阶段描述使用浅色 */
.phase-desc {
  color: rgba(255, 255, 255, 0.65);
  font-size: 13px;
  line-height: 1.5;
}

/* ==========================================
   功能入口项 - 渐变背景与悬浮效果
   ========================================== */
.phase-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 修改：功能入口项基础样式 */
.item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px 14px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 新增：探索期功能入口项（绿色系） */
.phase-row .el-col:nth-child(1) .item {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.08) 100%);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.phase-row .el-col:nth-child(1) .item:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(52, 211, 153, 0.2) 100%);
  border-color: rgba(16, 185, 129, 0.5);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.25);
}

.phase-row .el-col:nth-child(1) .item :deep(.el-icon) {
  color: #10b981;
  font-size: 18px;
  transition: all 0.3s ease;
}

.phase-row .el-col:nth-child(1) .item:hover :deep(.el-icon) {
  color: #34d399;
  transform: scale(1.15);
}

/* 新增：提升期功能入口项（橙色系） */
.phase-row .el-col:nth-child(2) .item {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.08) 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.phase-row .el-col:nth-child(2) .item:hover {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(251, 191, 36, 0.2) 100%);
  border-color: rgba(245, 158, 11, 0.5);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.25);
}

.phase-row .el-col:nth-child(2) .item :deep(.el-icon) {
  color: #f59e0b;
  font-size: 18px;
  transition: all 0.3s ease;
}

.phase-row .el-col:nth-child(2) .item:hover :deep(.el-icon) {
  color: #fbbf24;
  transform: scale(1.15);
}

/* 新增：冲刺期功能入口项（紫色系） */
.phase-row .el-col:nth-child(3) .item {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(167, 139, 250, 0.08) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.phase-row .el-col:nth-child(3) .item:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(167, 139, 250, 0.2) 100%);
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.25);
}

.phase-row .el-col:nth-child(3) .item :deep(.el-icon) {
  color: #8b5cf6;
  font-size: 18px;
  transition: all 0.3s ease;
}

.phase-row .el-col:nth-child(3) .item:hover :deep(.el-icon) {
  color: #a78bfa;
  transform: scale(1.15);
}

/* 新增：个人管理功能入口项（蓝色系） */
.phase-row .el-col:nth-child(4) .item {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(96, 165, 250, 0.08) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.phase-row .el-col:nth-child(4) .item:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(96, 165, 250, 0.2) 100%);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.25);
}

.phase-row .el-col:nth-child(4) .item :deep(.el-icon) {
  color: #3b82f6;
  font-size: 18px;
  transition: all 0.3s ease;
}

.phase-row .el-col:nth-child(4) .item:hover :deep(.el-icon) {
  color: #60a5fa;
  transform: scale(1.15);
}

/* 修改：文字颜色使用白色，悬浮时略有变化（通用） */
.item span {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
  letter-spacing: 0.2px;
}

.item:hover span {
  color: #e0e7ff;
}

/* ==========================================
   底部备注 - 保留样式
   ========================================== */
.footer-note {
  margin-top: 24px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  text-align: center;
}

/* ==========================================
   响应式适配
   ========================================== */
@media (max-width: 768px) {
  .explore-page {
    padding: 20px 16px;
  }
  
  .content {
    padding: 24px 20px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .phase-card {
    padding: 16px;
  }
}
</style>