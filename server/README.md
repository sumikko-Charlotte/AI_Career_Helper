# AI Project - Minimal User Server

提供一个最小的 Node/Express 服务器，用于在 `public/users.csv` 中持久化真实用户数据，满足小组 10 人与导师内部测试。

快速启动（3 步）:
1. cd server
2. npm install
3. node app.js

服务信息:
- 端口: 3000
- CSV 文件: `server/public/users.csv`（持久化，重启不丢失）

主要接口:
- POST `/api/register`    - 参数: { username, password, grade?, target_role? }
- POST `/api/login`       - 参数: { username, password }
- GET  `/api/users`       - 返回所有 CSV 中的真实用户
- POST `/api/user/updateStatus` - 参数: { username, status }
- POST `/api/user/delete` - 参数: { username }
- POST `/api/user/addTask` - 参数: { username }

返回格式:
{ code: 200 | 400, msg: "中文提示", data: {...} }

快速验证示例（terminal/curl）:

1) 获取用户列表：
   curl http://127.0.0.1:3000/api/users

2) 注册一个新用户：
   curl -X POST http://127.0.0.1:3000/api/register -H "Content-Type: application/json" -d '{"username":"testuser","password":"test123"}'

3) 登录（更新 last_login）：
   curl -X POST http://127.0.0.1:3000/api/login -H "Content-Type: application/json" -d '{"username":"testuser","password":"test123"}'

4) 增加任务数统计：
   curl -X POST http://127.0.0.1:3000/api/user/addTask -H "Content-Type: application/json" -d '{"username":"testuser"}'

注意：这些命令能帮助你在部署后快速确认 CSV 已被持久化更新。
说明:
- 保留前端的虚拟样板数据不写入 CSV，仅用于 Admin 页面填充显示。
- 服务器已开启 CORS，适合前端跨域调用以便线上部署测试。