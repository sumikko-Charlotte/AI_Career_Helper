# 前端 API 地址更新报告

## 📋 修改摘要

**目标：** 将前端所有 API 请求地址从本地后端改为 Render 线上后端

**线上后端地址：** `https://ai-career-helper-backend-u1s0.onrender.com`

**修改时间：** 2026-01-30

---

## ✅ 已修改的文件

### 1. `frontend/src/utils/request.js`

**修改位置：** 第 4 行

**修改前：**
```javascript
const API_BASE = 'https://unphrased-letha-lumpiest.ngrok-free.dev'
```

**修改后：**
```javascript
const API_BASE = 'https://ai-career-helper-backend-u1s0.onrender.com'
```

**影响范围：**
- 所有使用 `request.js` 导出的 `request` 实例的组件
- 所有使用 `request.js` 导出的 `API_BASE` 的组件
- 包括：`Login.vue` 等组件

---

### 2. `frontend/vite.config.js`

**修改位置：** 第 33 行和第 37 行（proxy 配置）

**修改前：**
```javascript
proxy: {
  '/api': {
    target: 'https://unphrased-letha-lumpiest.ngrok-free.dev',
    changeOrigin: true
  },
  '/static': {
    target: 'https://unphrased-letha-lumpiest.ngrok-free.dev',
    changeOrigin: true
  }
}
```

**修改后：**
```javascript
proxy: {
  '/api': {
    target: 'https://ai-career-helper-backend-u1s0.onrender.com',
    changeOrigin: true
  },
  '/static': {
    target: 'https://ai-career-helper-backend-u1s0.onrender.com',
    changeOrigin: true
  }
}
```

**影响范围：**
- 开发环境下的代理转发（`npm run dev`）
- 所有通过 `/api` 和 `/static` 路径的请求

---

## 📝 关键 Diff

### Diff 1: `frontend/src/utils/request.js`

```diff
--- frontend/src/utils/request.js (修改前)
+++ frontend/src/utils/request.js (修改后)
@@ -1,7 +1,7 @@
 import axios from 'axios'
 
 // 全局 API 基础地址配置
-const API_BASE = 'https://unphrased-letha-lumpiest.ngrok-free.dev'
+const API_BASE = 'https://ai-career-helper-backend-u1s0.onrender.com'
 
 // 创建 axios 实例，统一配置请求
 const request = axios.create({
```

### Diff 2: `frontend/vite.config.js`

```diff
--- frontend/vite.config.js (修改前)
+++ frontend/vite.config.js (修改后)
@@ -30,11 +30,11 @@
     allowedHosts: true,
     proxy: {
       '/api': {
-        target: 'https://unphrased-letha-lumpiest.ngrok-free.dev',
+        target: 'https://ai-career-helper-backend-u1s0.onrender.com',
         changeOrigin: true
       },
       '/static': {
-        target: 'https://unphrased-letha-lumpiest.ngrok-free.dev',
+        target: 'https://ai-career-helper-backend-u1s0.onrender.com',
         changeOrigin: true
       }
     }
```

---

## 📌 其他组件说明

以下组件使用 `import.meta.env.VITE_API_BASE` 环境变量：

- `src/App.vue`
- `src/components/VirtualExperiment.vue`
- `src/components/ResumeDoctor.vue`
- `src/components/UserProfile.vue`
- `src/components/HistoryRecord.vue`
- `src/components/CareerExperience.vue`
- `src/components/AdminLayout.vue`
- `src/views/admin/ResumeTasks.vue`
- `src/views/admin/AdminProfile.vue`

**处理方式：**
- 这些组件使用 `import.meta.env.VITE_API_BASE ?? ''`
- 如果环境变量未设置，会使用空字符串（相对路径）
- **建议：** 在部署环境（如 Vercel、Netlify）中设置环境变量 `VITE_API_BASE=https://ai-career-helper-backend-u1s0.onrender.com`
- 或者在本地开发时创建 `.env` 文件（已被 .gitignore 忽略）

---

## ✅ 验证步骤

1. **重启前端开发服务器：**
   ```bash
   cd frontend
   npm run dev
   ```

2. **检查网络请求：**
   - 打开浏览器开发者工具（F12）
   - 切换到 Network 标签
   - 执行登录或其他 API 操作
   - 确认请求地址为 `https://ai-career-helper-backend-u1s0.onrender.com/api/...`

3. **测试关键功能：**
   - 用户登录
   - 数据获取
   - 文件上传
   - 其他 API 调用

---

## 📋 修改统计

- **修改文件数：** 2 个
- **修改行数：** 3 行
- **影响组件：** 所有使用 `request.js` 的组件
- **修改类型：** 仅修改 baseURL，未改动业务逻辑

---

## ⚠️ 注意事项

1. **环境变量配置：**
   - 如果使用 `VITE_API_BASE` 的组件需要环境变量，请在部署平台设置
   - 本地开发可以创建 `.env` 文件（不会被提交到 Git）

2. **CORS 配置：**
   - 确保 Render 后端已配置 CORS，允许前端域名访问
   - 如果遇到 CORS 错误，检查后端 `main.py` 中的 CORS 配置

3. **HTTPS 证书：**
   - Render 使用 HTTPS，确保所有请求使用 `https://` 协议

4. **代理配置：**
   - `vite.config.js` 中的 proxy 仅用于开发环境
   - 生产环境（构建后）不会使用 proxy，直接使用 `request.js` 中的 `baseURL`

---

**修改完成时间：** 2026-01-30  
**修改状态：** ✅ 完成
