# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import random
from datetime import datetime

app = FastAPI()

# 允许跨域（让前端网页能访问后端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 定义数据格式 ---
class ResumeRequest(BaseModel):
    content: str

class ChatRequest(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    grade: str
    target_role: str

@app.get("/")
def home():
    return {"message": "AI Backend Running"}

# --- 核心功能 1: 简历诊断接口 ---
@app.post("/api/analyze_resume")
def analyze_resume(request: ResumeRequest):
    print(f"收到简历: {request.content[:20]}...") # 在后台打印一下日志
    time.sleep(1.5) # 模拟 AI 思考时间

    # 维度评分（用于前端雷达图）
    dimensions = [
        {"key": "structure", "name": "结构与逻辑", "score": random.randint(78, 92),
         "comment": "段落层级清晰，建议用 STAR 强化每段结论。"},
        {"key": "impact", "name": "量化影响力", "score": random.randint(60, 85),
         "comment": "当前更多是职责描述，建议补充“指标/规模/结果”。"},
        {"key": "tech", "name": "技术深度", "score": random.randint(70, 90),
         "comment": "技术栈覆盖不错，建议突出 1-2 个核心亮点与难点。"},
        {"key": "fit", "name": "岗位匹配度", "score": random.randint(72, 93),
         "comment": "关键词匹配较好，可加入与岗位强相关的项目切面。"},
        {"key": "communication", "name": "表达与可读性", "score": random.randint(75, 95),
         "comment": "措辞专业，但可进一步压缩长句、增强动词力度。"},
        {"key": "portfolio", "name": "作品与背书", "score": random.randint(55, 88),
         "comment": "若有 GitHub/作品链接与奖项证据，将显著加分。"},
    ]

    score = int(round(sum(d["score"] for d in dimensions) / len(dimensions)))

    # 关键词命中（演示用）
    keywords = ["FastAPI", "Vue", "Element Plus", "ECharts", "Python", "MySQL", "Redis", "Docker", "LLM", "RAG"]
    content_lower = request.content.lower()
    keyword_hits = [k for k in keywords if k.lower() in content_lower]

    # 模拟 AI 返回的结构化数据（更丰富，适配前端展示）
    return {
        "version": "v2",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "score": score,
        "level": "A" if score >= 90 else ("B+" if score >= 85 else ("B" if score >= 80 else "C")),
        "summary": "简历整体逻辑较清晰，亮点集中在技术栈与项目覆盖；但“量化成果/业务影响”与“作品背书”仍有明显提升空间。",
        "dimensions": dimensions,
        "highlights": {
            "strengths": [
                "技术栈覆盖全面，具备全栈协作与落地能力",
                "项目描述具备一定完整度，结构化表达良好",
                "学习能力与迁移能力迹象明显（多技术关键词）",
            ],
            "weaknesses": [
                "成果缺少可验证的量化指标（性能/转化/成本/效率）",
                "关键项目缺少“难点-方案-取舍-结果”的闭环",
                "作品集/链接/奖项等背书信息不足",
            ],
            "risks": [
                "若投递中高阶岗位，容易被判定为“广而不深”",
                "项目影响力不清晰会降低面试官追问欲望",
            ],
        },
        "suggestions": [
            "把“熟悉 Python”改为“用 Python/FastAPI 负责过 X 模块，支撑 Y 业务，指标提升 Z%”",
            "每个核心项目补齐：目标/规模/你的角色/技术方案/关键难点/量化结果",
            "补充 GitHub/作品链接（README 写清：架构图、功能列表、性能数据、部署方式）",
            "将关键词与目标岗位 JD 对齐：把最相关的内容放到第一页上半区",
        ],
        "rewrite_examples": [
            {
                "before": "参与项目开发，负责后端接口。",
                "after": "主导后端接口设计与实现（FastAPI + MySQL），将接口平均响应时间从 180ms 优化到 95ms，并完善鉴权与限流。",
            },
            {
                "before": "做过竞赛，获得奖项。",
                "after": "在 X 竞赛中负责算法/工程实现，最终获省级二等奖；方案在公开榜单 Top 5%。",
            },
        ],
        "keyword_hits": keyword_hits,
        "recommended_focus": [
            "量化成果（Impact）",
            "作品背书（Portfolio）",
            "技术深度（Tech Depth）",
        ],
    }

# --- 核心功能 2: 模拟面试接口 ---
# --- 核心功能 3：推荐接口 ---
@app.post("/api/recommend")
def recommend():
    """根据用户年级和目标岗位推荐相关职位信息"""
    import csv
    import os

    try:
        jobs_file = "jobs.csv"
        if not os.path.exists(jobs_file):
            return {"success": False, "message": "职位数据文件不存在", "data": []}

        jobs = []
        with open(jobs_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for job in reader:
                jobs.append({
                    "职业分类": job.get("职业分类", ""),
                    "岗位": job.get("岗位", ""),
                    "关键词": job.get("关键词", ""),
                    "平均薪资": job.get("平均薪资", "")
                })

        return {"success": True, "message": "获取职位数据成功", "data": jobs}

    except Exception as e:
        return {"success": False, "message": f"读取职位数据失败: {str(e)}", "data": []}
@app.post("/api/chat")
def chat(request: ChatRequest):
    time.sleep(1) # 模拟思考

    # 专业追问库：按主题组织，随机组合“肯定 + 追问”更像真实面试官
    followups = {
        "system": [
            "如果让你把它做成可水平扩展的架构，你会怎么拆分服务？为什么这样拆？",
            "你会把哪些状态放在服务端，哪些放在客户端？怎么做一致性？",
            "说说你在这个系统里对“可观测性”（日志/指标/链路追踪）的设计。",
        ],
        "db": [
            "面对高并发读写，你会怎么设计索引？如何验证索引真的生效？",
            "慢查询你会怎么定位？Explain 看到了什么信息你会重点关注？",
            "如果出现热点 Key 或者热点行锁，你会怎么处理？",
        ],
        "backend": [
            "请你解释一下幂等性：在下单/支付/消息重试里怎么落地？",
            "你如何设计接口错误码与异常处理，保证可诊断又不泄露信息？",
            "限流、熔断、降级你分别会怎么做？触发阈值怎么定？",
        ],
        "frontend": [
            "在大型前端项目里，你如何组织状态管理与模块边界，避免组件耦合？",
            "性能优化你会从哪三层入手：渲染、网络、资源？给出具体手段。",
            "如果要做可访问性（a11y）与国际化（i18n），你会怎么设计？",
        ],
        "ai": [
            "如果要让回答更稳定，你会如何做提示词工程与输出约束？",
            "你如何评估一个 AI 功能的效果？用哪些离线/在线指标？",
            "如果接入 RAG，你会如何做切分、召回、重排与防幻觉？",
        ],
        "behavior": [
            "说一个你遇到过的最棘手的 Bug，你是如何定位与复盘的？",
            "你如何在时间紧的情况下做取舍？能举一个你放弃了什么的例子吗？",
            "如果团队里对技术方案有分歧，你通常如何推动达成一致？",
        ],
    }

    openers = [
        "我认可你的思路，我们把细节再压一压：",
        "好的。为了评估你的工程化能力，我想追问一下：",
        "听起来不错。我更关心你“怎么做取舍”：",
        "可以。接下来我会从复杂度与边界条件考你：",
    ]

    topic = random.choice(list(followups.keys()))
    question = random.choice(followups[topic])
    reply_text = random.choice(openers) + question

    # 保持前端兼容：继续返回 reply，同时附带一些 meta 方便前端扩展展示
    return {
        "reply": reply_text,
        "meta": {
            "topic": topic,
            "difficulty": random.choice(["中等", "偏难", "高难"]),
            "intent": random.choice(["追问细节", "验证取舍", "考察边界", "工程化能力"]),
        },
    }

# --- 用户登录注册接口 ---
@app.post("/api/login")
def login(request: LoginRequest):
    """用户登录"""
    import csv
    import os

    # 检查用户数据文件是否存在
    users_file = "users.csv"
    if not os.path.exists(users_file):
        return {"success": False, "message": "用户数据文件不存在"}

    # 读取用户数据
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for user in reader:
            if user['username'] == request.username and user['password'] == request.password:
                return {
                    "success": True,
                    "message": "登录成功",
                    "user": {
                        "username": user['username'],
                        "grade": user['grade'],
                        "target_role": user['target_role']
                    }
                }

    return {"success": False, "message": "用户名或密码错误"}

@app.post("/api/register")
def register(request: RegisterRequest):
    """用户注册"""
    import csv
    import os

    # 检查用户数据文件是否存在，如果不存在创建
    users_file = "users.csv"
    file_exists = os.path.exists(users_file)

    # 检查用户名是否已存在
    if file_exists:
        with open(users_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for user in reader:
                if user['username'] == request.username:
                    return {"success": False, "message": "用户名已存在"}

    # 添加新用户
    with open(users_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['username', 'password', 'grade', 'target_role']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # 如果文件不存在，先写入表头
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'username': request.username,
            'password': request.password,
            'grade': request.grade,
            'target_role': request.target_role
        })

    return {
        "success": True,
        "message": "注册成功",
        "user": {
            "username": request.username,
            "grade": request.grade,
            "target_role": request.target_role
        }
    }

# 👇 注意：这行必须顶格写，不能有空格！
if __name__ == "__main__":
    import uvicorn
    # 👇 这行前面要留 4 个空格
    uvicorn.run(app, host="127.0.0.1", port=8000)