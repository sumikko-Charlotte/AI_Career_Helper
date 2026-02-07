<template>
  <div class="admin-guide-page">
    <h2 class="page-title">功能引导 · 管理端</h2>
    <p class="subtitle">快速进入常用管理模块（与用户端风格对称，遵循 Admin 风格）</p>

    <div class="guide-grid">
      <div class="guide-item guide-item--dashboard">
        <el-tooltip content="查看平台核心指标与趋势" placement="top" effect="dark">
          <el-card class="guide-card guide-card--dashboard" shadow="hover" @click="navTo('dashboard')">
            <div class="card-inner">
              <el-icon class="card-icon"><Monitor /></el-icon>
              <div class="card-body">
                <div class="card-title">数据大屏</div>
                <div class="card-desc">查看平台核心数据概览与趋势</div>
                <el-button type="primary" plain size="small" class="card-btn" @click.stop="navTo('dashboard')">进入</el-button>
              </div>
            </div>
          </el-card>
        </el-tooltip>
      </div>

      <div class="guide-item guide-item--users">
        <el-tooltip content="管理所有用户账号、权限与状态" placement="top" effect="dark">
          <el-card class="guide-card guide-card--users" shadow="hover" @click="navTo('users')">
            <div class="card-inner">
              <el-icon class="card-icon"><User /></el-icon>
              <div class="card-body">
                <div class="card-title">用户管理</div>
                <div class="card-desc">管理平台所有用户的账号与权限</div>
                <el-button type="primary" plain size="small" class="card-btn" @click.stop="navTo('users')">进入</el-button>
              </div>
            </div>
          </el-card>
        </el-tooltip>
      </div>

      <div class="guide-item guide-item--tasks">
        <el-tooltip content="处理与跟踪简历诊断相关任务" placement="top" effect="dark">
          <el-card class="guide-card guide-card--tasks" shadow="hover" @click="navTo('tasks')">
            <div class="card-inner">
              <el-icon class="card-icon"><Document /></el-icon>
              <div class="card-body">
                <div class="card-title">简历任务</div>
                <div class="card-desc">处理与跟踪简历诊断相关任务</div>
                <el-button type="primary" plain size="small" class="card-btn" @click.stop="navTo('tasks')">进入</el-button>
              </div>
            </div>
          </el-card>
        </el-tooltip>
      </div>

      <div class="guide-item guide-item--prompts">
        <el-tooltip content="配置 AI 面试与诊断的提示模板" placement="top" effect="dark">
          <el-card class="guide-card guide-card--prompts" shadow="hover" @click="navTo('prompts')">
            <div class="card-inner">
              <el-icon class="card-icon"><Setting /></el-icon>
              <div class="card-body">
                <div class="card-title">Prompt 配置</div>
                <div class="card-desc">配置 AI 面试与诊断的提示模板</div>
                <el-button type="primary" plain size="small" class="card-btn" @click.stop="navTo('prompts')">进入</el-button>
              </div>
            </div>
          </el-card>
        </el-tooltip>
      </div>

      <div class="guide-item guide-item--profile">
        <el-tooltip content="管理个人账号信息与系统设置" placement="top" effect="dark">
          <el-card class="guide-card guide-card--profile" shadow="hover" @click="navTo('profile')">
            <div class="card-inner">
              <el-icon class="card-icon"><User /></el-icon>
              <div class="card-body">
                <div class="card-title">个人页面</div>
                <div class="card-desc">管理个人账号信息与系统设置</div>
                <el-button type="primary" plain size="small" class="card-btn" @click.stop="navTo('profile')">进入</el-button>
              </div>
            </div>
          </el-card>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Monitor, User, Document, Setting } from '@element-plus/icons-vue'
import { ElRow, ElCol, ElCard, ElTooltip, ElIcon, ElButton } from 'element-plus'

const router = useRouter()

const navTo = (key) => {
  switch (key) {
    case 'dashboard':
      router.push('/admin/dashboard').catch(() => {})
      break
    case 'users':
      // 支持两种路径：/admin/users 与 /admin/user-management（后者作为友好别名）
      router.push('/admin/users').catch(() => {})
      break
    case 'tasks':
      router.push('/admin/tasks').catch(() => {})
      break
    case 'prompts':
      router.push('/admin/prompts').catch(() => {})
      break
    case 'profile':
      // 个人页面路由与右上角头像一致
      router.push('/admin/profile').catch(() => {})
      break
    default:
      router.push('/admin/dashboard').catch(() => {})
  }
}
</script>

<style scoped>
.admin-guide-page { padding: 24px; }
.page-title { font-size: 20px; font-weight: 700; color: #101C4D; margin-bottom: 6px; }
.subtitle { color: #606266; margin-bottom: 18px; }

/* 把主区域铺满并使用 CSS Grid 实现 3x2 -> 2x -> 1x 的响应式布局 */
.admin-guide-page { padding: 24px; display: flex; flex-direction: column; height: calc(100vh - 120px); }
.guide-grid { margin-top: 12px; display: grid; grid-template-columns: repeat(3, 1fr); grid-auto-rows: 1fr; gap: 20px; align-items: stretch; flex: 1; }

/* 中等屏幕两列 */
@media (max-width: 1200px) {
  .guide-grid { grid-template-columns: repeat(2, 1fr); }
}
/* 小屏单列 */
@media (max-width: 768px) {
  .guide-grid { grid-template-columns: repeat(1, 1fr); }
}

/* 卡片基础样式（一致圆角、铺满高度、内边距） */
.guide-card { cursor: pointer; border-radius: 12px; height: 100%; display: flex; align-items: center; box-shadow: 0 8px 20px rgba(16,24,40,0.04); padding: 18px; }
.card-inner { display:flex; align-items:center; gap: 16px; width: 100%; }
.card-icon { font-size: 36px; border-radius: 10px; padding: 6px; width: 52px; height: 52px; display:flex; align-items:center; justify-content:center; }
.card-body { flex: 1; }
.card-title { font-weight: 700; font-size: 16px; color: #165DFF; }
.card-desc { color: #606266; margin-top: 6px; margin-bottom: 10px; }
.card-btn { padding: 6px 12px; }
.el-button.card-btn:hover { background-color: rgba(64,158,255,0.08); }

/* 每个卡片的浅色主题背景（低饱和度）与图标呼应色 */
.guide-card--dashboard { background: #E8F4FF; }
.guide-card--dashboard .card-icon { color: #165DFF; background: rgba(22,93,255,0.08); }

.guide-card--users { background: #E8FFF0; }
.guide-card--users .card-icon { color: #16A34A; background: rgba(22,163,74,0.06); }

.guide-card--tasks { background: #FFF5E8; }
.guide-card--tasks .card-icon { color: #D97706; background: rgba(217,119,6,0.06); }

.guide-card--prompts { background: #F5E8FF; }
.guide-card--prompts .card-icon { color: #7C3AED; background: rgba(124,58,237,0.06); }

.guide-card--profile { background: #F0F4F8; }
.guide-card--profile .card-icon { color: #475569; background: rgba(71,85,105,0.06); }

/* 保证在非常窄的设备下卡片内边距合理 */
@media (max-width: 480px) {
  .guide-card { padding: 12px; }
  .card-icon { width: 44px; height: 44px; font-size: 28px; }
}
</style>