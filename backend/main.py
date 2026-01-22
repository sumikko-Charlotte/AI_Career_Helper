# backend/main.py
# 确保顶部导入了 os
import os 
import csv
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import random
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
# 导入你刚搬进来的模块
# 如果放在同级目录：
from services.resume_parser import *
from services.ai_advisor import *
# 如果放在 services 文件夹：from services import resume_parser, ai_advisor

app = FastAPI()

@app.post("/api/analyze_resume")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    简历诊断接口
    输入：PDF文件
    输出：JSON格式的诊断报告
    """
    # 1. 验证文件类型
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    # 2. 读取文件内容 (pypdf 需要文件对象)
    # 这里的 file.file 就是一个类文件对象，可以直接传给我们写的 parser
    try:
        # 注意：Streamlit 的 uploader 和 FastAPI 的 UploadFile 略有不同
        # pypdf 的 PdfReader 可以直接读 file.file
        resume_text = resume_parser.extract_text_from_pdf(file.file)
        
        # 3. 调用 AI 分析
        # 这里建议加上 try-except 处理 AI 调用失败的情况
        analysis_result = ai_advisor.analyze_resume(resume_text)
        
        if not analysis_result:
            raise HTTPException(status_code=500, detail="AI 分析失败")
            
        # 4. 返回 JSON
        return analysis_result

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

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
# --- 👇 请复制粘贴到 main.py 的后面 (不要覆盖前面的代码) ---
# --- 👇 新增：岗位数据库（与 jobs.csv 字段对应，没有 CSV 也能运行）---
JOB_DATABASE = [
    {"职业分类": "后端开发", "岗位": "Python 开发工程师", "关键词": "FastAPI, MySQL, Redis", "平均薪资": "15k-25k"},
    {"职业分类": "前端开发", "岗位": "Vue 开发工程师", "关键词": "Vue3, Vite, Element Plus", "平均薪资": "14k-23k"},
    {"职业分类": "算法工程师", "岗位": "NLP 算法工程师", "关键词": "LLM, RAG, 深度学习", "平均薪资": "20k-35k"},
    {"职业分类": "数据开发", "岗位": "数据工程师", "关键词": "Spark, Hadoop, 数据仓库", "平均薪资": "16k-28k"},
    {"职业分类": "运维开发", "岗位": "DevOps 工程师", "关键词": "Docker, Kubernetes, 自动化", "平均薪资": "18k-26k"},
]
class AgentRequest(BaseModel):
    grade: str       # 用户年级
    target_job: str  # 目标方向

@app.post("/api/agent")
def agent_recommend(req: AgentRequest):
    """
    智能体核心逻辑：
    1. 根据用户年级筛选（大一 -> 找日常实习/学习路线）
    2. 根据目标方向筛选（算法 -> 找 Python/模型相关）
    """
    recommendations = []
    
    # 1. 简单的规则筛选 (模拟 Agent 思考)
    for job in JOB_DATABASE:
        # 获取 CSV 里的字段 (注意：要和你昨天的表头对应)
        j_name = str(job.get('岗位', '')).lower()
        j_cate = str(job.get('职业分类', '')).lower()
        
        # 规则 A: 匹配目标方向
        if req.target_job.lower() in j_name or req.target_job.lower() in j_cate:
            recommendations.append(job)
            
    # 2. 生成“拟人化”的话术
    if not recommendations:
        reply = f"同学你好！作为{req.grade}学生，目前库里暂时没有完全匹配 '{req.target_job}' 的岗位。建议你可以先从基础项目练手，积累经验。"
    else:
        # 取前 3 个最匹配的
        top_jobs = recommendations[:3] 
        job_names = "、".join([j.get('岗位', '未知岗位') for j in top_jobs])
        
        reply = f"你好！我是你的专属职业顾问。检测到你是{req.grade}学生，且主修{req.target_job}方向。\n\n"
        reply += f"💡 **Agent 洞察**：对于这个阶段，我为你精选了 **{len(recommendations)}** 个机会，重点推荐：**{job_names}**。\n"
        reply += "这些岗位对新人比较友好，建议你点击下方按钮尝试投递！"

    return {
        "reply": reply,
        "data": recommendations[:3] # 返回前3个给前端展示
    }
# 👇 注意：这行必须顶格写，不能有空格！
# --- 👇 复制到 main.py 末尾 ---

# 定义投递的数据模型
class ApplyRequest(BaseModel):
    username: str
    job_name: str
    salary: str

@app.post("/api/apply")
def apply_job(req: ApplyRequest):
    """
    模拟投递接口：将投递记录写入 applications.csv
    """
    file_path = "data/applications.csv"
    
    # 如果文件不存在，先创建并写表头
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["用户", "投递岗位", "薪资", "投递时间", "状态"])

    # 写入本次投递记录
    import datetime
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(file_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([req.username, req.job_name, req.salary, now_time, "已投递"])

    return {"message": "投递成功", "status": "success"}
# --- Resume Doctor Mock Interface (Day 1) ---

# 引入 UploadFile，因为我们要接收文件
from fastapi import UploadFile, File
class GenerateResumeRequest(BaseModel):
    focus_direction: str = "通用"          # 优化方向
    diagnosis: dict | None = None          # 诊断结果
# --- Day 1 简历分析接口 (Mock版 - 增强数据返回) ---
@app.post("/api/resume/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    import time
    time.sleep(1.5) # 模拟 AI 思考
    
    # 👇👇👇 这里是核心修改：增加了 score_rationale 字段 👇👇👇
    return {
        "score": 82, # 增加具体分数
        "score_rationale": "基础得分 70 分，因项目经历描述清晰 +5 分，技术栈匹配 +5 分；但缺少量化成果数据 -8 分，排版稍显拥挤 -5 分。",
        "summary": "该简历结构完整，教育背景清晰，但项目描述偏泛，缺乏具体数据支撑。",
        "strengths": [
            "教育背景与目标岗位匹配度高",
            "有两段相关实习经历，具备实战意识",
            "技术栈关键词覆盖较全 (Python, Vue, FastAPI)"
        ],
        "weaknesses": [
            "项目成果量化不足（缺少具体提升百分比）",
            "STAR 法则运用不熟练，过程描述多于结果",
            "自我评价过于笼统，未体现核心竞争力"
        ],
        "suggestions": [
            "建议在项目 A 中补充性能优化前后的对比数据（如响应时间提升 50%）",
            "将“负责后端开发”改为“使用 FastAPI 重构核心接口，提升并发能力”",
            "补充 GitHub 链接或技术博客地址，增加可信度"
        ]
    }
# --- 👇 核心功能 6: 生涯路径规划 (Mock) ---

# 定义请求数据格式
class RoadmapRequest(BaseModel):
    current_grade: str
    target_role: str

# --- 👇 智能版：生涯规划接口 (带雷达图数据) ---
@app.post("/api/generate_roadmap")
def generate_roadmap(req: RoadmapRequest):
    import time
    import random
    time.sleep(1) # 模拟 AI 运算
    
    # 1. 定义不同方向的技能维度 (用于雷达图)
    # 模拟数据：根据年级生成“当前能力值”，目标岗位是“满分标准”
    radar_config = {}
    
    if "算法" in req.target_role:
        radar_indicators = [
            {"name": "数学基础", "max": 100},
            {"name": "Python/C++", "max": 100},
            {"name": "论文复现", "max": 100},
            {"name": "模型调优", "max": 100},
            {"name": "工程落地", "max": 100}
        ]
        # 模拟不同年级的分数 (大一低，大三高)
        base = {"大一": 30, "大二": 50, "大三": 70, "大四": 85}.get(req.current_grade, 40)
        current_scores = [base + random.randint(-5, 10) for _ in range(5)]
        
    elif "前端" in req.target_role:
        radar_indicators = [
            {"name": "HTML/CSS", "max": 100},
            {"name": "JavaScript", "max": 100},
            {"name": "Vue/React", "max": 100},
            {"name": "工程化", "max": 100},
            {"name": "UI审美", "max": 100}
        ]
        base = {"大一": 35, "大二": 55, "大三": 75, "大四": 90}.get(req.current_grade, 40)
        current_scores = [base + random.randint(-5, 10) for _ in range(5)]
        
    else: # 默认后端/其他
        radar_indicators = [
            {"name": "编程语言", "max": 100},
            {"name": "数据库", "max": 100},
            {"name": "分布式", "max": 100},
            {"name": "中间件", "max": 100},
            {"name": "系统设计", "max": 100}
        ]
        base = {"大一": 30, "大二": 50, "大三": 70, "大四": 85}.get(req.current_grade, 40)
        current_scores = [base + random.randint(-5, 10) for _ in range(5)]

    # 2. 生成“AI 导师寄语”
    ai_comment = f"同学你好！基于你的{req.current_grade}身份，你的{radar_indicators[0]['name']}基础尚可，但在'{radar_indicators[3]['name']}'方面与{req.target_role}岗位要求存在 {100 - current_scores[3]}% 的差距。建议重点强化实战项目。"

    # 3. 生成更美观的时间轴数据 (增加 status 字段)
    # 逻辑：大一之前的算 done，当前的算 process，未来的算 wait
    roadmap = []
    stages = [
        {"time": "大一上", "title": "通识与筑基", "content": "高数/C++ 均分 85+，加入技术社团", "res": ["CS50 公开课", "C++ Prime"]},
        {"time": "大一下", "title": "编程入门", "content": "完成简易管理系统，熟悉 Git/Linux", "res": ["Git 飞行手册", "鸟哥的 Linux 私房菜"]},
        {"time": "大二全", "title": "核心栈构建", "content": f"系统学习 {req.target_role} 核心框架，刷题 200+", "res": ["LeetCode", "官方文档"]},
        {"time": "大三上", "title": "项目实战", "content": "参与高含金量开源项目或学科竞赛", "res": ["GitHub Trending", "Kaggle"]},
        {"time": "大三下", "title": "实习冲刺", "content": "制作简历，模拟面试，投递暑期实习", "res": ["牛客网", "Boss 直聘"]},
        {"time": "大四", "title": "秋招定局", "content": "查漏补缺，冲击 SP Offer", "res": ["Offershow"]}
    ]

    # 简单粗暴的状态判断逻辑
    grades = ["大一", "大二", "大三", "大四"]
    try:
        curr_idx = grades.index(req.current_grade[:2]) # 取前两个字 "大一"
    except:
        curr_idx = 0

    final_roadmap = []
    for i, stage in enumerate(stages):
        status = "wait"
        color = "#909399" # 灰色
        icon = "CircleCheck"
        
        # 简单模拟：当前年级之前的都算完成
        # 注意：这里只是简单演示，真实逻辑会更复杂
        stage_grade_idx = 0
        if "大一" in stage["time"]: stage_grade_idx = 0
        elif "大二" in stage["time"]: stage_grade_idx = 1
        elif "大三" in stage["time"]: stage_grade_idx = 2
        elif "大四" in stage["time"]: stage_grade_idx = 3

        if stage_grade_idx < curr_idx:
            status = "done"
            color = "#67C23A" # 绿色
        elif stage_grade_idx == curr_idx:
            status = "process"
            color = "#409EFF" # 蓝色
            icon = "Loading"
        
        final_roadmap.append({
            "timestamp": stage["time"],
            "title": stage["title"],
            "content": stage["content"],
            "resources": stage["res"],
            "status": status,
            "color": color,
            "icon": icon
        })

    return {
        "radar_chart": {
            "indicators": radar_indicators,
            "values": current_scores
        },
        "ai_comment": ai_comment,
        "roadmap": final_roadmap
    }
# --- 👇 新增功能：简历生成 (Resume Generation) ---


# --- 3. 简历生成接口 (Pro 增强版) ---
@app.post("/api/resume/generate")
def generate_resume(req: GenerateResumeRequest):
    import time
    import random
    time.sleep(1.5) # 模拟 AI 深度思考
    
    # 1. 提取上下文信息
    direction = req.focus_direction
    diagnosis = req.diagnosis or {}
    strengths = diagnosis.get("strengths", [])
    
    # 2. 根据求职方向，智能匹配技术栈模板 (模拟 AI 的知识库)
    if "算法" in direction or "AI" in direction:
        target_role = "算法工程师 / AI 研究员"
        skills_template = """
* **深度学习**：熟练掌握 PyTorch/TensorFlow，熟悉 Transformer、BERT、ResNet 等经典架构。
* **数据处理**：精通 Pandas, NumPy, Matplotlib，具备海量数据清洗与特征工程经验。
* **开发工具**：熟悉 Linux 环境开发，掌握 Docker 容器化部署，熟练使用 Git。
"""
        project_tech = "PyTorch, HuggingFace, FastAPI"
        
    elif "前端" in direction or "Web" in direction:
        target_role = "高级前端开发工程师"
        skills_template = """
* **核心框架**：深入理解 Vue3 原理，熟练使用 Composition API，了解 React/Next.js 生态。
* **工程化**：熟悉 Webpack/Vite 配置，具备前端性能优化（首屏加载、SSR）实战经验。
* **样式与交互**：精通 CSS3/Sass，熟练使用 TailwindCSS，追求极致的 UI/UX 体验。
"""
        project_tech = "Vue3, Element Plus, ECharts, TypeScript"
        
    else: # 默认/全栈/后端
        target_role = direction
        skills_template = """
* **后端技术**：熟练掌握 Python (FastAPI/Django) 或 Java (Spring Boot)，了解高并发架构设计。
* **数据库**：精通 MySQL 索引优化，熟悉 Redis 缓存策略与应用场景。
* **系统运维**：熟悉 CI/CD 流程，掌握 Nginx 配置与 Linux 常用命令。
"""
        project_tech = "FastAPI, Vue3, PostgreSQL, Docker"

    # 3. 动态生成亮点 (基于诊断结果)
    highlight_text = "具备扎实的计算机科学基础，代码风格规范。"
    if strengths:
        # 把诊断出的前3个亮点拼进去
        highlight_text = f"**{strengths[0]}**，**{strengths[1] if len(strengths)>1 else ''}**。经 AI 诊断，您的核心竞争力在于{strengths[-1] if len(strengths)>2 else '学习能力'}。"

    # 4. 生成内容 (使用更专业的 Markdown 排版)
    generated_content = f"""
# [你的姓名] 
> 求职意向：{target_role} | 状态：随时到岗
> 电话：138-xxxx-xxxx | 邮箱：email@example.com | 📍 北京

---

## 💡 AI 优化摘要
> **本次优化重点**：
> 1. 根据您的求职方向 **{direction}**，重构了技能清单，突出关键词命中率。
> 2. 引入 **STAR 法则** 优化项目描述，强化了“数据成果”的展示。
> 3. 基于诊断报告，将您的 **{len(strengths)} 个核心亮点** 植入到了自我评价中。

---

## 🎓 教育背景
**北京邮电大学** | 人工智能学院 | 人工智能专业 | 本科 (2024-2028)
* **核心绩效**：专业排名前 10% (GPA 3.8/4.0)
* **主修课程**：数据结构与算法 (95)、机器学习导论 (92)、计算机网络 (90)、操作系统 (88)
* **校园奖项**：校级一等奖学金、全国大学生数学建模竞赛省一等奖

## 🛠 专业技能
{skills_template}
* **通用能力**：CET-6 (580+)，具备良好的英文文档阅读能力；热衷开源技术。

## 💻 项目经历 (精修版)

### 🚀 **AI 简历全科医生平台 (AI Career Helper)**
**角色：全栈开发负责人** | 技术栈：{project_tech}
* **背景 (Situation)**：针对大学生求职简历“缺乏针对性”和“排版混乱”的痛点，开发一款基于 LLM 的智能辅助系统。
* **任务 (Task)**：负责从 0 到 1 搭建前后端分离架构，实现简历解析、智能诊断与自动生成功能。
* **行动 (Action)**：
    * **架构设计**：基于 **FastAPI** 重构后端接口，设计 RESTful API 规范，解决了原系统“评分理由丢失”的数据一致性问题。
    * **体验优化**：前端采用 **Vue3 + Element Plus** 实现响应式布局，开发“双屏联动”交互模式，让用户能实时对比修改效果。
    * **性能调优**：通过异步 I/O 处理文件上传，引入 Redis 缓存高频请求，将大文件解析速度提升了 **40%**。
* **结果 (Result)**：项目上线首周获得 200+ 次调用，GitHub Star 数突破 50+，生成的简历模板采纳率达 95%。

### 🏆 **基于深度学习的图像识别系统**
**角色：算法核心成员** | 技术栈：PyTorch, OpenCV
* **行动**：复现 ResNet50 经典论文，针对特定数据集进行微调（Fine-tuning）。
* **行动**：设计数据增强（Data Augmentation）策略，解决了样本不平衡问题，模型在测试集准确率提升 **5%**。
* **结果**：该项目最终作为课程优秀大作业进行展示，代码被收录进实验室代码库。

## 📜 自我评价
* {highlight_text}
* 具备极强的工程落地能力，善于在压力下快速定位 Bug（曾在一周内完成核心模块重构）。
* 技术视野开阔，保持对新技术（如 LLM Agent、RAG）的敏锐关注，致力于用技术创造实际价值。

---
*注：本简历由 AI 深度生成，建议结合真实经历微调数据。*
"""
    return {
        "success": True,
        "content": generated_content.strip()
    }
if __name__ == "__main__":
    import uvicorn
    # 👇 这行前面要留 4 个空格
    uvicorn.run(app, host="127.0.0.1", port=8000)