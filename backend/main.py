import time
import random
import csv
import os
import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from typing import List
import shutil # 👈 新增
from fastapi.staticfiles import StaticFiles # 👈 新增
from openai import OpenAI
app = FastAPI()

os.makedirs("static/avatars", exist_ok=True) # 自动创建文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")
# --- 1. 跨域配置 (必不可少) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
#  DeepSeek 客户端 (新增：虚拟实验 & 生涯规划整合)
# ==========================================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-d3a066f75e744cd58708b9af635d3606")
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def _deepseek_markdown(system_prompt: str, user_prompt: str) -> str:
    """调用 DeepSeek，返回 Markdown 文本"""
    try:
        resp = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek 调用失败: {e}")

def _deepseek_json(system_prompt: str, user_prompt: str) -> dict:
    """调用 DeepSeek，要求其返回严格 JSON 对象"""
    try:
        resp = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek(JSON) 调用失败: {e}")

# ==========================================
#  模型定义 (整合了所有功能的数据结构)
# ==========================================
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    grade: str
    target_role: str

class ChatRequest(BaseModel):
    message: str

class RoadmapRequest(BaseModel):
    current_grade: str
    target_role: str

class AgentRequest(BaseModel):
    grade: str
    target_job: str

class ApplyRequest(BaseModel):
    username: str
    job_name: str
    salary: str

class AdminProfileModel(BaseModel):
    username: str = "admin"
    nickname: str = ""
    role: str = ""
    department: str = ""
    email: str = ""
    phone: str = ""
    avatar: str = ""     # 存 Base64 字符串
    lastLogin: str = ""
    ip: str = ""
    new_password: str = None # 接收新密码

class GenerateResumeRequest(BaseModel):
    focus_direction: str = "通用"
    diagnosis: dict | None = None

# ==========================================
#  新增功能 G: 虚拟实验体验 & 生涯分析整合
# ==========================================
class AnalyzeExperimentRequest(BaseModel):
    answers: dict
    career: str | None = None

class GenerateCareerRequest(BaseModel):
    personality_json: dict
    experiment_markdown: str
    note: str | None = ""

class VirtualCareerQuestionsRequest(BaseModel):
    career: str

# ==========================================
#  Mock 数据库 (职位数据)
# ==========================================
JOB_DATABASE = [
    {"职业分类": "后端开发", "岗位": "Python 开发工程师", "关键词": "FastAPI, MySQL", "平均薪资": "15k-25k"},
    {"职业分类": "前端开发", "岗位": "Vue 开发工程师", "关键词": "Vue3, Element Plus", "平均薪资": "14k-23k"},
    {"职业分类": "算法工程师", "岗位": "NLP 算法工程师", "关键词": "LLM, RAG", "平均薪资": "20k-35k"},
    {"职业分类": "数据开发", "岗位": "大数据开发工程师", "关键词": "Hadoop, Spark", "平均薪资": "18k-30k"},
    {"职业分类": "测试", "岗位": "自动化测试工程师", "关键词": "Selenium, PyTest", "平均薪资": "12k-20k"},
]

# --- 1. 定义历史记录的数据模型 ---
class HistoryItem(BaseModel):
    username: str
    action_type: str  # "诊断" 或 "生成"
    title: str        # 例如 "Java工程师简历诊断"
    score: int
    date: str
    status: str       # "已完成"
# 1. 获取管理员信息 (GET)
# ⚠️ 之前报错 404 就是因为这个函数可能没写对，或者缩进错了
@app.get("/api/admin/profile")
def get_admin_profile():
    print("🔍 [DEBUG] 收到获取 Admin Profile 请求") # 调试日志
    
    file_path = "data/admin_profile.json"
    
    # 确保 data 目录存在
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # 如果文件不存在，返回默认数据
    if not os.path.exists(file_path):
        print("⚠️ [DEBUG] JSON 文件不存在，返回默认值")
        default_data = {
            "username": "admin",
            "nickname": "默认管理员",
            "role": "Super Admin",
            "department": "技术部",
            "email": "admin@careerfly.com",
            "phone": "13800000000",
            "avatar": ""
        }
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return {"success": True, "data": default_data}
    
    # 读取文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ [DEBUG] 成功读取 JSON 数据")
        return {"success": True, "data": data}
    except Exception as e:
        print(f"❌ [DEBUG] 读取失败: {e}")
        return {"success": False, "message": "读取失败"}
# 2. 更新管理员信息 (POST)
@app.post("/api/admin/profile/update")
def update_admin_profile(item: AdminProfileModel):
    print(f"📝 [DEBUG] 收到更新请求: 昵称={item.nickname}, 密码更改={item.new_password}")

    # --- A. 保存到 JSON (解决头像和昵称保存) ---
    json_path = "data/admin_profile.json"
    try:
        # 使用 model_dump 替代 dict (修复 Pydantic 警告)
        save_data = item.model_dump(exclude={"new_password"}) 
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print("✅ [DEBUG] JSON 文件保存成功")
    except Exception as e:
        print(f"❌ [DEBUG] JSON 保存失败: {e}")
        return {"success": False, "message": f"JSON保存失败: {e}"}

    # --- B. 同步密码到 CSV (解决登录密码不更新问题) ---
    if item.new_password and len(item.new_password) >= 6:
        csv_path = "data/users.csv"
        
        if not os.path.exists(csv_path):
            print("❌ [DEBUG] CSV 文件不存在，无法同步密码")
            return {"success": True, "message": "资料已保存，但用户数据库不存在，无法同步密码"}

        try:
            # 1. 读取所有数据到内存
            rows = []
            updated = False
            fieldnames = []
            
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames # 获取表头
                
                for row in reader:
                    # 强力匹配：去除空格
                    if row.get("username", "").strip() == "admin":
                        print(f"🔄 [DEBUG] 找到 admin 用户，正在更新密码为: {item.new_password}")
                        row["password"] = item.new_password
                        updated = True
                    rows.append(row)
            
            # 2. 只有真的改了才写回文件
            if updated:
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                print("✅ [DEBUG] CSV 密码同步完成")
            else:
                print("⚠️ [DEBUG] 未在 CSV 中找到 admin 用户，密码未同步")

        except Exception as e:
            print(f"❌ [DEBUG] CSV 操作出错: {e}")
            return {"success": False, "message": "CSV同步失败"}

    return {"success": True, "message": "更新成功"}

# --- 3. 新增：获取历史记录接口 ---
@app.get("/api/history")
def get_history(username: str):
    file_path = "data/history.csv"
    if not os.path.exists(file_path):
        return {"success": True, "data": []}
    
    records = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username:
                records.append(row)
    
    # 按时间倒序排列 (最新的在前面)
    records.reverse()
    return {"success": True, "data": records}
# 根路径处理（避免重复声明 / 路由）
@app.get("/")
async def root():
    return {"message": "AI 后端服务运行中"}

@app.post("/api/login")
def login(request: LoginRequest):
    users_file = "data/users.csv"
    if not os.path.exists(users_file):
        # 如果文件不存在，直接返回一个模拟成功，方便测试
        return {"success": True, "message": "测试登录成功 (无数据库)", "user": {"username": request.username, "grade": "大三", "target_role": "算法工程师"}}
    
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for user in reader:
            if user['username'] == request.username and user['password'] == request.password:
                return {
                    "success": True, 
                    "message": "登录成功", 
                    "user": user
                }
    return {"success": False, "message": "用户名或密码错误"}

# ==========================================
# 🛑 替换 main.py 里的 register 函数
# ==========================================

@app.post("/api/register")
def register(req: RegisterRequest):
    csv_path = "data/users.csv"
    
    # 1. 检查文件是否存在
    if not os.path.exists(csv_path):
        return {"success": False, "message": "数据库未初始化，请先联系管理员"}

    # 2. 检查用户名是否已存在
    users = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == req.username:
                return {"success": False, "message": "该用户名已被注册"}
            users.append(row)
    
    # 3. 追加新用户
    # 注意：这里把 req.grade 存入 CSV
    new_user = {
        "username": req.username,
        "password": req.password,
        "grade": req.grade,      # 这里如果是 '管理员'，下次登录就会被识别
        "target_role": req.target_role
    }
    
    try:
        # 追加模式 'a' 不太安全（容易乱表头），建议用重写模式
        users.append(new_user)
        fieldnames = ["username", "password", "grade", "target_role"]
        
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
            
        return {"success": True, "message": "注册成功"}
    except Exception as e:
        print(f"注册写入失败: {e}")
        return {"success": False, "message": "注册写入失败"}

# ==========================================
#  核心功能 B: 职位推荐 (修复 404 错误)
# ==========================================
@app.post("/api/recommend")
def recommend():
    """简单的职位推荐接口"""
    return {"success": True, "data": JOB_DATABASE}

# ==========================================
#  核心功能 C: AI 模拟面试 (聊天)
# ==========================================
@app.post("/api/chat")
def chat(request: ChatRequest):
    time.sleep(0.5)
    followups = [
        "在这个项目中，你遇到的最大技术难点是什么？",
        "如果让你优化数据库查询，你会怎么做？",
        "对于高并发场景，你有什么设计思路？"
    ]
    return {
        "reply": f"收到！关于'{request.message}'，我的看法是... (模拟AI回复)\n\n👉 追问：{random.choice(followups)}",
        "meta": {"topic": "技术", "difficulty": "中等"}
    }

# ==========================================
#  核心功能 D: 生涯规划 (雷达图 + 时间轴)
# ==========================================
@app.post("/api/generate_roadmap")
def generate_roadmap(req: RoadmapRequest):
    time.sleep(1)
    # 雷达图逻辑
    radar_indicators = [
        {"name": "基础知识", "max": 100}, {"name": "实战能力", "max": 100},
        {"name": "算法思维", "max": 100}, {"name": "工程素养", "max": 100},
        {"name": "软技能", "max": 100}
    ]
    base_score = 60 if "大一" in req.current_grade else (70 if "大二" in req.current_grade else 80)
    current_scores = [base_score + random.randint(-10, 10) for _ in range(5)]

    # 时间轴逻辑
    stages = [
        {"time": "大一", "title": "夯实基础", "content": "学习 C++/Python，刷 LeetCode 100题", "status": "done", "color": "#67C23A"},
        {"time": "大二", "title": "项目实战", "content": "参与一个完整的 Web 全栈项目", "status": "process", "color": "#409EFF"},
        {"time": "大三", "title": "实习冲刺", "content": "准备简历，投递日常实习", "status": "wait", "color": "#909399"},
        {"time": "大四", "title": "秋招定局", "content": "查漏补缺，冲击 SP Offer", "status": "wait", "color": "#909399"}
    ]
    
    return {
        "radar_chart": {"indicators": radar_indicators, "values": current_scores},
        "ai_comment": f"基于{req.current_grade}的你，建议重点加强实战能力。",
        "roadmap": stages
    }

# ==========================================
#  核心功能 E: Agent 职位推荐 & 投递
# ==========================================
@app.post("/api/agent")
def agent_recommend(req: AgentRequest):
    recommendations = [j for j in JOB_DATABASE if req.target_job in j['岗位'] or req.target_job in j['职业分类']]
    if not recommendations: recommendations = JOB_DATABASE[:2]
    
    return {
        "reply": f"我是你的 Agent。为你找到 {len(recommendations)} 个相关岗位。",
        "data": recommendations
    }

@app.post("/api/apply")
def apply_job(req: ApplyRequest):
    file_path = "data/applications.csv"
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(["用户", "岗位", "薪资", "时间", "状态"])
    
    with open(file_path, "a", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow([req.username, req.job_name, req.salary, datetime.datetime.now(), "已投递"])
    return {"message": "投递成功", "status": "success"}

# ... 之前的代码 ...

# --- 1. 定义用户资料模型 ---
class UserProfile(BaseModel):
    username: str
    avatar: str = ""  # 👈 新增这一行
    email: str = ""
    phone: str = ""
    city: str = ""
    style: str = "专业正式"
    file_format: str = "PDF"
    notify: bool = True
    auto_save: bool = True

# --- 2. 获取用户资料接口 ---
@app.get("/api/user/profile")
def get_profile(username: str):
    file_path = "data/profiles.csv"
    if not os.path.exists(file_path):
        # 如果还没存过资料，返回一个默认的空资料
        return {"success": True, "data": {"username": username, "email": "", "phone": "", "city": "", "style": "专业正式", "file_format": "PDF"}}
    
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('username') == username:
                # 转换布尔值 (CSV里存的是字符串)
                row['notify'] = row.get('notify') == 'True'
                row['auto_save'] = row.get('auto_save') == 'True'
                return {"success": True, "data": row}
    
    # 没找到也返回默认
    return {"success": True, "data": {"username": username}}

# --- 3. 更新用户资料接口 ---
@app.post("/api/user/profile")
def update_profile(profile: UserProfile):
    file_path = "data/profiles.csv"
    os.makedirs("data", exist_ok=True)
    
    # 读取所有现存资料
    profiles = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            profiles = list(reader)
    
    # 查找并更新，或者新增
    updated = False
    for row in profiles:
        if row.get('username') == profile.username:
            row.update(profile.dict()) # 更新字段 (这里会自动包含 avatar)
            # 把布尔值转回字符串存CSV
            row['notify'] = str(profile.notify)
            row['auto_save'] = str(profile.auto_save)
            updated = True
            break
    
    if not updated:
        # 新增一条
        new_row = profile.dict()
        new_row['notify'] = str(profile.notify)
        new_row['auto_save'] = str(profile.auto_save)
        profiles.append(new_row)
    
    # 写回文件
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        # 👇 关键修改点：在列表里加入了 "avatar"
        fieldnames = ["username", "avatar", "email", "phone", "city", "style", "file_format", "notify", "auto_save"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(profiles)
        
    return {"success": True, "message": "资料已保存"}
# ==========================================
#  核心功能 F: 简历医生 (诊断 + 生成)
# ==========================================
@app.post("/api/resume/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    time.sleep(1.5)
    print(f"收到简历诊断请求: {file.filename}")
    
    # 核心：确保 score_rationale 存在
    return {
        "score": 82,
        "score_rationale": "✅ 基础分70。因项目使用了STAR法则+5分，技术栈匹配+10分；❌ 但缺少GitHub链接-3分。",
        "summary": "简历结构清晰，技术栈覆盖全面，但‘量化成果’有待提升。",
        "strengths": ["教育背景优秀", "两段相关实习", "技术栈命中率高"],
        "weaknesses": ["缺乏具体性能数据", "自我评价泛泛", "无开源贡献"],
        "suggestions": ["补充性能对比数据", "增加熟练度描述", "添加 GitHub 链接"]
    }

# --- 4. 修改密码接口 ---
class ChangePwdRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

@app.post("/api/user/change_password")
def change_password(req: ChangePwdRequest):
    users_file = "data/users.csv"
    rows = []
    updated = False
    
    # 1. 读取并查找
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == req.username:
                if row['password'] != req.old_password:
                    return {"success": False, "message": "旧密码不正确"}
                row['password'] = req.new_password # 更新密码
                updated = True
            rows.append(row)
    
    # 2. 写回文件
    if updated:
        with open(users_file, 'w', encoding='utf-8', newline='') as f:
            # 注意：这里要跟你 users.csv 的表头一致
            fieldnames = ['username', 'password', 'grade', 'target_role']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return {"success": True, "message": "密码修改成功"}
    
    return {"success": False, "message": "用户不存在"}

# --- 5. 上传头像接口 ---
@app.post("/api/user/upload_avatar")
async def upload_avatar(file: UploadFile = File(...)):
    # 生成一个文件名，避免冲突
    file_path = f"static/avatars/{file.filename}"
    
    # 保存文件到本地
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回可访问的 URL
    return {"success": True, "url": f"http://127.0.0.1:8000/{file_path}"}
@app.post("/api/resume/generate")
def generate_resume(req: GenerateResumeRequest):
    time.sleep(1.5)
    direction = req.focus_direction
    print(f"收到生成请求，方向: {direction}")
    
    # 动态生成内容
    if "算法" in direction:
        tech = "PyTorch, Transformer, CUDA"
        role = "算法工程师"
    elif "前端" in direction:
        tech = "Vue3, TypeScript, Vite, Element Plus"
        role = "前端开发工程师"
    else:
        tech = "FastAPI, Vue3, Docker, Redis"
        role = "全栈开发工程师"

    content = f"""
# 你的姓名 (意向岗位：{role})
电话：138-xxxx-xxxx | 邮箱：email@example.com

## 💡 AI 优化摘要
> **优化重点**：根据 **{direction}** 方向重构了技能清单，并引入 **STAR 法则** 优化了项目描述。

## 🎓 教育背景
**北京邮电大学** | 人工智能学院 | 本科 | 2024-2028
* **主修课程**：数据结构 (95)、机器学习 (92)
* **核心优势**：专业排名前 10%

## 💻 项目经历 (精修版)
**AI 简历全科医生平台** | 全栈负责人 | {tech}
* **背景 (S)**：针对大学生求职痛点，开发智能辅助系统。
* **任务 (T)**：负责从 0 到 1 搭建前后端分离架构。
* **行动 (A)**：
    * **架构设计**：基于 **FastAPI** 重构接口，修复了“404 Not Found"的关键 Bug。
    * **体验优化**：前端采用 **Vue3** 实现“双屏联动”，效率提升 **50%"。
* **结果 (R)**：项目上线首周获得 200+ 次调用。

## 🛠 技能清单
* **核心技术**：{tech}
* **工具**：Git, Linux

## 📜 自我评价
* 具备极强的 Debug 能力，善于在压力下快速定位并解决问题。
"""
    return {"success": True, "content": content.strip()}


# ===================== 新增：简历上传相关接口 =====================
class ResumeUploadRequest(BaseModel):
    username: str
    task_id: str
    filename: str
    report: str
    score: float | int = 0
    date: str | None = None


@app.post('/api/resume/upload')
def upload_resume(item: ResumeUploadRequest):
    """接收前端上传的简历报告，持久化到 data/uploaded_resumes.csv 并更新 users.csv 的 uploadedResumeNum 字段"""
    os.makedirs('data', exist_ok=True)
    uploaded_file = 'data/uploaded_resumes.csv'
    users_file = 'data/users.csv'

    # 填充默认日期
    if not item.date:
        item.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. 写入 uploaded_resumes.csv
    fieldnames = ['task_id', 'username', 'filename', 'report', 'score', 'date']
    exists = os.path.exists(uploaded_file)
    try:
        with open(uploaded_file, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists:
                writer.writeheader()
            writer.writerow({
                'task_id': item.task_id,
                'username': item.username,
                'filename': item.filename,
                'report': item.report,
                'score': item.score,
                'date': item.date,
            })
    except Exception as e:
        return {'success': False, 'message': f'写入上传记录失败: {e}'}

    # 2. 更新 users.csv 的 uploadedResumeNum 字段
    if os.path.exists(users_file):
        rows = []
        updated = False
        with open(users_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames_users = reader.fieldnames or []
            for row in reader:
                if row.get('username') == item.username:
                    # 初始化字段
                    row.setdefault('uploadedResumeNum', '0')
                    row['uploadedResumeNum'] = str(int(row.get('uploadedResumeNum', '0')) + 1)
                    updated = True
                rows.append(row)
        # 如果字段不存在在写回时需要加入表头
        if updated:
            if 'uploadedResumeNum' not in fieldnames_users:
                fieldnames_users = fieldnames_users + ['uploadedResumeNum']
            with open(users_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_users)
                writer.writeheader()
                writer.writerows(rows)
    else:
        # 没有 users.csv，不阻碍上传，但记录提示
        return {'success': True, 'message': '上传成功，但用户数据库不存在，无法同步统计'}

    return {'success': True, 'message': '上传成功'}


@app.get('/api/resume/getUploadedList')
def get_uploaded_list():
    """返回所有已上传的简历上传记录（若无则生成 3 条模拟数据）"""
    os.makedirs('data', exist_ok=True)
    uploaded_file = 'data/uploaded_resumes.csv'

    # 如果文件不存在，生成三条默认模拟数据
    if not os.path.exists(uploaded_file):
        mock = [
            {'task_id': 'T-MOCK-01', 'username': 'alice', 'filename': 'alice_resume.pdf', 'report': '# 模拟报告\n- 分数：88\n- 建议：突出项目', 'score': 88, 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'task_id': 'T-MOCK-02', 'username': 'bob', 'filename': 'bob_resume.pdf', 'report': '# 模拟报告\n- 分数：76\n- 建议：补充实习', 'score': 76, 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'task_id': 'T-MOCK-03', 'username': 'carol', 'filename': 'carol_resume.pdf', 'report': '# 模拟报告\n- 分数：92\n- 建议：保持精炼', 'score': 92, 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        with open(uploaded_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['task_id','username','filename','report','score','date'])
            writer.writeheader()
            writer.writerows(mock)

    # 读取并返回
    records = []
    with open(uploaded_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # convert numeric
            row['score'] = float(row.get('score') or 0)
            records.append(row)
    # 返回按时间倒序（最新在前）
    records.reverse()
    return {'success': True, 'data': records}


@app.post('/api/resume/delete')
def delete_upload(username: str, task_id: str):
    """删除上传记录并同步 users.csv 的统计字段"""
    uploaded_file = 'data/uploaded_resumes.csv'
    users_file = 'data/users.csv'

    if not os.path.exists(uploaded_file):
        return {'success': False, 'message': '没有上传记录文件'}

    rows = []
    removed = False
    with open(uploaded_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('username') == username and row.get('task_id') == task_id:
                removed = True
                continue
            rows.append(row)

    if removed:
        with open(uploaded_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['task_id','username','filename','report','score','date'])
            writer.writeheader()
            writer.writerows(rows)

        # 同步 users.csv uploadedResumeNum 减一
        if os.path.exists(users_file):
            urows = []
            with open(users_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames_users = reader.fieldnames or []
                for row in reader:
                    if row.get('username') == username:
                        row.setdefault('uploadedResumeNum', '0')
                        row['uploadedResumeNum'] = str(max(0, int(row.get('uploadedResumeNum','0')) - 1))
                    urows.append(row)
            with open(users_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_users)
                writer.writeheader()
                writer.writerows(urows)

        return {'success': True, 'message': '删除上传记录成功'}

    return {'success': False, 'message': '未找到对应上传记录'}


@app.post('/api/user/addTask')
def add_user_task(username: str):
    """为用户的 createTaskNum +1（用于统计用户提交到 Admin 的次数）"""
    users_file = 'data/users.csv'
    if not os.path.exists(users_file):
        return {'success': False, 'message': '用户数据库不存在'}

    rows = []
    updated = False
    with open(users_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames_users = reader.fieldnames or []
        for row in reader:
            if row.get('username') == username:
                row.setdefault('createTaskNum', '0')
                row['createTaskNum'] = str(int(row.get('createTaskNum','0')) + 1)
                updated = True
            rows.append(row)

    if updated:
        if 'createTaskNum' not in fieldnames_users:
            fieldnames_users = fieldnames_users + ['createTaskNum']
        with open(users_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_users)
            writer.writeheader()
            writer.writerows(rows)
        return {'success': True, 'message': '用户任务数已更新'}

    return {'success': False, 'message': '未找到用户'}
# ==========================================
# 🎮 虚拟职业体验模块 (Career Simulation)
# ==========================================

# 1. 模拟剧本数据 (Mock Data)
SIMULATION_SCRIPTS = {
    "product_manager": {
        "title": "产品经理的一天",
        "desc": "体验从需求评审到上线发布的生死时速。",
        "scenes": [
            {
                "id": 1,
                "text": "早上9:30，你刚到公司，开发组长气冲冲地跑过来说：'昨天定的需求技术实现不了，必须砍掉！' 同时，运营那边催着要上线。你会怎么做？",
                "options": [
                    {"label": "坚持原需求，让开发想办法", "score_change": -10, "feedback": "开发组长拍了桌子，项目延期风险增加。"},
                    {"label": "立刻砍掉功能，保上线", "score_change": 5, "feedback": "运营很不满，但至少能按时上线。"},
                    {"label": "拉会协调，寻找替代方案", "score_change": 10, "feedback": "虽然花了一小时开会，但大家达成了共识，干得漂亮！"}
                ]
            },
            {
                "id": 2,
                "text": "下午3:00，老板突然在群里发了一张竞品的截图，说：'这个功能很酷，我们要不要也加一个？' 此时距离封版只剩2小时。",
                "options": [
                    {"label": "老板说加就加！", "score_change": -20, "feedback": "开发全员炸锅，今晚通宵已成定局，士气低落。"},
                    {"label": "私聊老板，说明风险，建议下个版本加", "score_change": 10, "feedback": "老板觉得你考虑周全，同意了你的建议。"},
                    {"label": "装作没看见", "score_change": -5, "feedback": "老板在群里@了你，场面一度十分尴尬。"}
                ]
            }
        ]
    },
    "programmer": {
        "title": "全栈工程师的一天",
        "desc": "体验代码、Bug与产品经理之间的爱恨情仇。",
        "scenes": [
            {
                "id": 1,
                "text": "上午10:00，你正在写核心代码，产品经理突然跑过来说：'这个按钮的颜色能不能换成五彩斑斓的黑？' 你被打断了思路。",
                "options": [
                    {"label": "直接怼回去：'你行你上！'", "score_change": -10, "feedback": "产品经理哭着去找老板了，你被HR约谈。"},
                    {"label": "耐心解释技术实现难度", "score_change": 10, "feedback": "产品经理被你的专业术语绕晕了，放弃了修改。"},
                    {"label": "默默记下，先写完手头代码", "score_change": 5, "feedback": "稳妥的做法，但需求还是得改。"}
                ]
            },
            {
                "id": 2,
                "text": "下午5:50，准备下班去约会。测试突然提了一个 '严重' 级别的Bug，说是偶发性的，复现不出来。",
                "options": [
                    {"label": "不管了，先下班", "score_change": -15, "feedback": "线上炸了，你在约会途中被叫回公司修通宵。"},
                    {"label": "留下来排查，推迟约会", "score_change": 10, "feedback": "查出了是缓存问题，半小时搞定，不仅没迟到还收获了测试的崇拜。"},
                    {"label": "告诉测试：'我本地是好的'", "score_change": -5, "feedback": "经典的程序员语录，但问题依然存在。"}
                ]
            }
        ]
    }
}

class SimulationRequest(BaseModel):
    role_id: str

# 2. 获取剧本接口
@app.post("/api/simulation/start")
def start_simulation(req: SimulationRequest):
    role = req.role_id
    if role not in SIMULATION_SCRIPTS:
        return {"success": False, "message": "剧本不存在"}
    
    script = SIMULATION_SCRIPTS[role]
    return {
        "success": True, 
        "data": {
            "title": script["title"],
            "scenes": script["scenes"] # 一次性把简单剧本都给前端，前端自己控制进度
        }
    }

# ==========================================
#  新增功能 G: 虚拟职业体验 & 生涯分析整合
# ==========================================
@app.post("/api/virtual-career/questions")
def virtual_career_questions(req: VirtualCareerQuestionsRequest):
    """
    根据职业名称动态生成 15 道匹配度选择题（每题 4 个选项）
    """
    system_prompt = (
        "你是一名职业规划评估题目设计专家。"
        "请针对指定职业设计 15 道用于评估匹配度的单选题，每题 4 个选项。"
        "题目要尽量贴近真实工作场景，覆盖能力要求、工作方式偏好、压力/节奏、沟通协作等维度。\n"
        "必须严格按照以下 JSON 结构返回：\n"
        "{\n"
        '  \"career\": \"职业名称\",\n'
        '  \"questions\": [\n'
        "    {\"id\": \"q1\", \"title\": \"题目 1 文本\", \"options\": [\"选项A\", \"选项B\", \"选项C\", \"选项D\"]},\n"
        "    ... 共 15 道题 ...\n"
        "  ]\n"
        "}"
    )

    user_prompt = (
        "目标职业名称：\n"
        f"{req.career}\n\n"
        "如果这是一个非常冷门或未见过的职业，请先用 1-2 句话理解/假设这个职业的核心工作内容，"
        "然后基于你的理解设计题目。"
    )

    data = _deepseek_json(system_prompt, user_prompt)
    questions = data.get("questions") or []
    if not isinstance(questions, list) or len(questions) == 0:
        raise HTTPException(status_code=500, detail="AI 生成题目失败，请稍后重试")

    # 简单保证 id 存在
    for idx, q in enumerate(questions, start=1):
        q.setdefault("id", f"q{idx}")

    return {
        "career": data.get("career", req.career),
        "questions": questions[:15],
    }

@app.post("/api/analyze-experiment")
def analyze_experiment(req: AnalyzeExperimentRequest):
    """
    接收 15 题答案字典，调用 DeepSeek 生成 Markdown 分析报告
    """
    target_career = req.career or "未指定（请根据答题推断最匹配的方向）"
    system_prompt = (
        "你是一位资深生涯规划师与组织心理学顾问。"
        "用户针对某一职业完成了 15 道匹配度选择题（每题 4 个选项）。"
        "请为该用户生成一份围绕“目标职业匹配度”的 Markdown 报告，包含：\n"
        "1) 职业画像与动机分析（3-6 条要点）\n"
        "2) 与目标职业的整体匹配度评级（例如：高度匹配/基本匹配/需谨慎）\n"
        "3) 关键优势/潜在风险点（各 3-5 条，结合答题内容给证据）\n"
        "4) 若坚持该职业的 4 周行动建议（按周分解）\n"
        "5) 若不适合该职业，建议的备选职业方向（至少 3 个，并解释理由）\n"
        "要求：只输出 Markdown，不要输出 JSON。"
    )

    user_prompt = (
        f"目标职业：{target_career}\n\n"
        "以下是用户的作答（字典形式，key 为题号，value 为选项文本）：\n"
        f"{json.dumps(req.answers, ensure_ascii=False, indent=2)}\n"
        "请围绕此目标职业，生成一份匹配度分析报告。"
    )

    markdown = _deepseek_markdown(system_prompt, user_prompt)
    return {"success": True, "markdown": markdown}


@app.post("/api/generate-career")
def generate_career(req: GenerateCareerRequest):
    """
    接收：性格测试 JSON + 虚拟实验 Markdown + 可选补充说明
    输出：整合后的生涯规划 Markdown 报告
    """
    system_prompt = (
        "你是一位资深生涯规划师。你将整合两份输入：\n"
        "- 性格测试结果（JSON：可能含截图/自述/字段）\n"
        "- 虚拟实验倾向分析（Markdown）\n"
        "请输出一份最终的生涯规划 Markdown 报告，包含：\n"
        "1) 个人画像（性格/动机/工作方式偏好）\n"
        "2) 目标职业方向建议（3 个主方向 + 3 个备选方向）\n"
        "3) 方向匹配理由（用证据对齐：来自性格测试与虚拟实验）\n"
        "4) 能力差距清单（按：基础/项目/软技能/行业认知）\n"
        "5) 12 周成长路线图（按周分解，每周 3-6 个任务）\n"
        "6) 作品集/项目建议（至少 3 个可落地项目，写清楚产出物）\n"
        "7) 简历与面试策略（关键词、故事线、STAR/项目讲法）\n"
        "要求：只输出 Markdown，不要输出 JSON。"
    )

    user_prompt = (
        "【性格测试 JSON】\n"
        f"{json.dumps(req.personality_json, ensure_ascii=False, indent=2)}\n\n"
        "【虚拟实验 Markdown】\n"
        f"{req.experiment_markdown}\n\n"
        "【用户补充说明（可为空）】\n"
        f"{req.note or ''}\n\n"
        "请输出最终的生涯规划 Markdown 报告。"
    )

    markdown = _deepseek_markdown(system_prompt, user_prompt)
    return {"success": True, "markdown": markdown}

# ==========================================
#  启动入口
# ==========================================
if __name__ == "__main__":
    print("🚀 服务器启动中...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
