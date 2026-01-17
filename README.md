# AI 大学生生涯规划平台（演示版）

本仓库为演示版：前端使用 Vue 3 + Element Plus，后端使用 FastAPI。功能覆盖四大模块：

- AI 简历医生 (`/api/analyze_resume`)：简历文本结构化诊断（Mock）。
- 模拟面试 (`/api/chat`)：模拟面试官问答，回复风格已调整为偏严格的字节跳动面试官风格（Mock）。
- 竞争力沙盘（雷达图）：前端使用 ECharts 渲染，6 个维度实时驱动。
- 生涯路径规划 (`/api/generate_roadmap`)：根据 `current_grade` 与 `target_role` 返回 4-6 阶段的成长/学习路径。对“北邮大一 → 算法”场景有预置高质量路径；其它输入使用规则引擎生成示例路径以便演示。

---

## 后端（`backend/main.py`）

主要接口：

- `GET /` → 健康检查
- `POST /api/analyze_resume` → 请求体：{ content: string }
  - 返回：{ score, level, summary, dimensions, highlights, suggestions }
- `POST /api/chat` → 请求体：{ message: string }
  - 返回：{ reply }
  - 回复风格：模拟更严厉、技术导向的面试官问法。
- `POST /api/generate_roadmap` → 请求体：{ current_grade: string, target_role: string }
  - 返回：{ roadmap: [ { timestamp, title, content } ] }
  - 实现说明：若 `current_grade` 为“大一”且 `target_role` 包含“算法/字节跳动”等关键词，返回预置的高质量路线；否则使用基于年级与岗位的简单规则生成演示用路径。

快速运行（开发）：

```bash
cd backend
python main.py
```

> 注意：后端使用 `uvicorn` 运行，端口为 `8000`。

---

## 前端（`frontend/`）

技术栈：Vue 3 + Element Plus + ECharts + Vite。

主要文件：

- `frontend/src/App.vue`：主界面，包含四个模块的实现与注释（便于新人阅读）。
- `frontend/src/main.js`：入口，已引入 Element Plus。

运行前端：

```bash
cd frontend
npm install
npm run dev
```

在浏览器打开 Vite 提供的地址（通常 http://localhost:5173）。

---

## 说明与开发建议

- `generate_roadmap` 当前为规则化生成（Mock）。若需要更智能的生成，请接入 LLM（需准备 API Key）；我可以帮忙实现 LLM 接入层并把规则作为回退。
- 我已在 `frontend/src/App.vue` 添加了较多中文注释，便于新队友上手；也在 `backend/main.py` 的关键接口上方添加了注释。

---

## 变更记录（本次）

- 增强 `/api/analyze_resume` 返回结构（增加 `dimensions`、`level` 等字段）。
- 将 `/api/chat` 的回复风格调整为更严格的面试官问答示例。
- 将 `/api/generate_roadmap` 支持规则化动态生成，并保留“北邮大一 → 算法”预置示例。
- 在 `frontend/src/App.vue` 中按模块添加中文注释并做少量 UI 统一调整。

---

如果你希望我：
- 接入 LLM 动态生成 Roadmap（需说明使用的 LLM 与 API key），或者
- 把注释整理为更完整的 Developer Guide（README 的扩展），
请告诉我优先级（例如“先接入 LLM，再生成文档”）。
## 本地部署（Docker 一键启动）

### 0. 环境要求
- Windows / macOS / Linux
- 已安装 Docker Desktop（Windows 需开启 WSL2）

### 1. 启动步骤
在项目根目录（有 docker-compose.yml 的位置）运行：

```bash
docker compose up -d --build
