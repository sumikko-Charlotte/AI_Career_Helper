# AI 职业助手 - 后端模块

## 📖 功能介绍

这是 AI 职业助手项目的后端模块，基于 FastAPI 构建，提供完整的 RESTful API 服务，包括：

- 🔐 用户认证（登录/注册）
- 💼 职位推荐与投递管理
- 🤖 AI 模拟面试对话
- 📊 生涯路径规划（AI 生成）
- 🩺 简历诊断与生成
- 🎮 虚拟职业体验
- 👤 用户资料管理
- 🔧 管理员后台接口

## 🚀 本地运行

### 前置要求

- Python >= 3.10
- MySQL 数据库（或使用云数据库）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境变量配置

创建 `.env` 文件（或在系统环境变量中设置）：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 数据库配置

修改 `db_config.py` 中的数据库连接信息：

```python
DB_CONFIG = {
    "host": "your_database_host",
    "port": 3306,
    "user": "your_username",
    "password": "your_password",
    "database": "ai_career_helper",
    "charset": "utf8mb4"
}
```

### 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

访问地址：
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📦 部署到 Render

### 步骤一：准备代码

1. 确保所有文件已提交到 Git 仓库

2. 检查 `Procfile` 内容：
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. 检查 `runtime.txt` 内容：
```
python-3.10
```

### 步骤二：创建 Render 服务

1. 访问 [Render Dashboard](https://dashboard.render.com/)

2. 点击 "New +" → "Web Service"

3. 连接你的 GitHub 仓库

4. 配置服务：
   - **Name**: `ai-career-helper-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: 选择 Free 计划（学生可用）

### 步骤三：配置环境变量

在 Render 项目设置中添加环境变量：

- `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key
- `PORT`: Render 会自动设置（无需手动配置）

### 步骤四：数据库配置

如果使用云数据库（如腾讯云 TDSQL-C），确保：

1. 数据库已创建并配置好表结构
2. 安全组已开放对应端口
3. `db_config.py` 中的连接信息正确

### 步骤五：部署

点击 "Create Web Service"，Render 会自动：

1. 克隆代码
2. 安装依赖
3. 启动服务

部署完成后，你会获得一个类似 `https://ai-career-helper-backend.onrender.com` 的 URL。

## 📁 项目结构

```
ai-career-helper-backend/
├── main.py              # FastAPI 应用入口
├── db_config.py         # 数据库配置
├── services/            # 业务逻辑模块
│   ├── ai_advisor.py   # AI 服务
│   └── resume_parser.py # 简历解析
├── static/              # 静态文件（头像等）
│   └── avatars/
├── data/                # 数据文件（CSV/JSON）
├── requirements.txt     # Python 依赖
├── Procfile            # Render 启动配置
└── runtime.txt         # Python 版本
```

## 🔧 依赖说明

### 核心依赖

- `fastapi>=0.104.0` - Web 框架
- `uvicorn[standard]>=0.24.0` - ASGI 服务器
- `pydantic>=2.0.0` - 数据验证
- `pymysql>=1.0.2` - MySQL 驱动
- `openai>=1.0.0` - OpenAI API 客户端（用于 DeepSeek）
- `python-dotenv>=1.0.0` - 环境变量管理

## 🔌 API 接口说明

主要接口列表：

- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `POST /api/chat` - AI 模拟面试
- `POST /api/generate_roadmap` - 生成生涯规划
- `POST /api/resume/analyze` - 简历诊断
- `POST /api/resume/generate` - 简历生成
- `GET /docs` - API 文档（Swagger UI）

完整 API 文档请访问 `/docs` 端点。

## 📝 注意事项

1. **数据库连接**：确保数据库服务可访问，且安全组配置正确

2. **API Key 安全**：不要将 API Key 提交到代码仓库，使用环境变量

3. **CORS 配置**：当前配置允许所有来源，生产环境建议限制为前端域名

4. **静态文件**：`static/avatars/` 目录需要写入权限

## 🆘 常见问题

**Q: 部署后无法连接数据库？**  
A: 检查数据库安全组是否开放了对应端口，以及连接信息是否正确

**Q: API 返回 500 错误？**  
A: 查看 Render 日志，检查环境变量是否配置正确

**Q: 如何查看日志？**  
A: 在 Render Dashboard 中点击 "Logs" 标签页

## 📄 许可证

本项目仅供学习使用。
