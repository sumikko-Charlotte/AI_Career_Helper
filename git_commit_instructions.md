# Git 提交指令

## 📋 当前状态
- 当前分支：`main`
- 需要提交的文件：
  - **前端**：`ai-career-helper-frontend/src/App.vue`、`ai-career-helper-frontend/src/components/SloganPage.vue`、`ai-career-helper-frontend/public/images/`
  - **后端**：`backend/main.py`

## 🎯 提交步骤

### 第一步：提交前端修改（main 分支）

```bash
# 1. 添加前端修改的文件
git add ai-career-helper-frontend/src/App.vue
git add ai-career-helper-frontend/src/components/SloganPage.vue
git add ai-career-helper-frontend/public/images/

# 2. 提交前端修改
git commit -m "fix: 修复竞争力沙盘模块 - 解决报告显示问题和405错误

- 修复前端报告显示逻辑，兼容后端返回的 markdown/analysis_report 字段
- 修复按钮文字：将'生成雷达图/分析报告'改为'生成雷达图'
- 修复报告生成逻辑，避免同时显示成功和失败提示
- 添加 slogan 图片支持（SloganPage.vue）
- 创建 public/images/ 目录用于存放 slogan 图片"

# 3. 推送到 main 分支（前端部署分支）
git push origin main
```

### 第二步：提交后端修改（backend-update 分支）

```bash
# 1. 切换到 backend-update 分支
git checkout backend-update

# 2. 如果 backend-update 分支不存在，先创建
# git checkout -b backend-update

# 3. 合并 main 分支的后端修改（或直接添加）
git add backend/main.py

# 4. 提交后端修改
git commit -m "fix: 修复竞争力沙盘分析接口和语法错误

- 增强 /api/analyze-experiment 接口，自动识别竞争力沙盘请求
- 为竞争力沙盘添加专门的 AI 提示词，生成6维度详细分析报告
- 修复返回格式，同时返回 markdown 和 analysis_report 字段以兼容前端
- 修复字符串中的中文引号语法错误
- 添加降级逻辑，AI失败时返回基础报告"

# 5. 推送到 backend-update 分支（后端部署分支）
git push origin backend-update
```

### 第三步：切换回 main 分支（可选）

```bash
git checkout main
```

## ⚠️ 注意事项

1. **不要提交的文件**：
   - `backend/__pycache__/main.cpython-314.pyc`（Python 缓存文件，应忽略）
   - `ai-career-helper-frontend/package-lock.json`（如果只是依赖更新，可选择性提交）

2. **如果 backend-update 分支不存在**：
   ```bash
   git checkout -b backend-update
   git push -u origin backend-update
   ```

3. **验证提交**：
   - 前端：检查 Vercel 是否自动部署
   - 后端：检查 Render 是否自动部署 backend-update 分支

## 🚀 快速执行（一键脚本）

### Windows PowerShell：

```powershell
# 前端提交
git add ai-career-helper-frontend/src/App.vue ai-career-helper-frontend/src/components/SloganPage.vue ai-career-helper-frontend/public/images/
git commit -m "fix: 修复竞争力沙盘模块 - 解决报告显示问题和405错误"
git push origin main

# 后端提交
git checkout backend-update
git add backend/main.py
git commit -m "fix: 修复竞争力沙盘分析接口和语法错误"
git push origin backend-update

# 切换回 main
git checkout main
```
