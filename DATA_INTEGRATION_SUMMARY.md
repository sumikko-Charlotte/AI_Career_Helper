# 真实数据持久化 + 虚拟样板数据融合（实现说明）

目标：实现真实用户数据持久化到 CSV（server/public/users.csv）并在 Admin 页面与原有虚拟样板数据混合显示。适配 10 人小组与导师内部测试，支持后续线上部署。

## 变更清单（关键文件）
- 新增：`server/app.js` — Node/Express 服务器，实现 CSV 读写与用户 API
- 新增：`server/public/users.csv` — 持久化真实用户（预置 10 人）
- 新增：`server/package.json`, `server/README.md`
- 修改：`frontend/src/views/admin/UserManage.vue` — 从用户服务拉取真实用户并与前端虚拟样板数据合并显示；真实用户操作（禁用/删除）调用 API，虚拟用户仍为前端填充
- 修改：`frontend/src/components/Login.vue` — 注册/登录后同步调用用户服务，保证 users.csv 的持久化
- 修改：`frontend/src/components/ResumeDoctor.vue` — 简历诊断完成后调用用户服务 `/api/user/addTask` 更新用户任务计数

## 后端接口清单（server/app.js）
> 返回格式统一：{ code: 200 | 400, msg: "中文提示", data: ... }

- POST `/api/register`  - body: { username, password, grade?, target_role? }
- POST `/api/login`     - body: { username, password }
- GET  `/api/users`     - 返回 CSV 中的所有真实用户
- POST `/api/user/updateStatus` - body: { username, status }
- POST `/api/user/delete` - body: { username }
- POST `/api/user/addTask` - body: { username }

说明：虚拟样板数据仅用于前端填充展示，**不写入 CSV**；所有真实用户写入且读取自 `server/public/users.csv`。

## 部署（极简 3 步）
1. 进入 server 目录：`cd server`
2. 安装依赖：`npm install`
3. 启动服务：`node app.js` （监听端口 3000）

前端部署要点：
- 确保前端的 `VITE_USER_SERVER`（或 `SERVER_API`）指向后端外网地址，例如 `https://your.domain.com:3000`
- 前端仍使用原有后端（AI 功能）地址 `VITE_API_BASE`（通常 8001）用于 AI 相关功能

## 测试步骤（快速验收）
1. 启动 `server`（3000）与原后端（AI 服务，8001）以及前端 `npm run dev`。
2. 在前端注册新用户（或登录已有用户），打开 `server/public/users.csv` 可看到新增/登录同步信息（last_login、register_time）。
3. 在历史记录页上传/诊断简历后，Admin 中的真实用户统计会随调用 `/api/user/addTask` 更新 `createTaskNum` 字段。
4. Admin 用户管理页会显示真实用户（来自 CSV）与虚拟样板数据的混合列表；对真实用户的禁用/删除操作会调用服务器接口并持久化。

## 注意事项
- 本实现保持前后端代码分离，新增后端放在 `server` 文件夹，方便单独部署。
- 所有新增代码包含注释，易读且与原逻辑解耦。
- 若需上线部署（公网），请在 `server` 前加代理或使用 PM2、Docker 运行，并在前端环境变量设置外网地址。

---
若你希望，我可以：
- 将 `server` 封装为一个 `docker` 服务（Dockerfile + docker-compose）以便一键部署 ✅
- 或把 `server` 的接口改为与现有 Python 后端合并（若你更偏向单一后端）

选择一个你想优先做的扩展，我来继续实现。