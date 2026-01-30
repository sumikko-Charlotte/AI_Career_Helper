import json
import openai
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
print("✅ LOADED services/ai_advisor.py FROM:", __file__)


# ==========================================
# 🛠️ 修复 1: 强制 Windows 输出 UTF-8 (解决报错核心)
# ==========================================
# 这一行是解决 'ascii' codec can't encode... 的关键
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# 2) 如果 api_key 缺失，直接 raise（不要让 client 带 None 运行）
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError(f"Missing DEEPSEEK_API_KEY, please check {env_path}")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# ==========================================
# 📂 配置路径与 Key (保留你指定的绝对路径)
# ==========================================
# 1. 你的项目根目录
project_root = Path(r"C:\Users\sumik\Desktop\AI_Project")
env_path = project_root / ".env"

# 2. 加载环境变量
print(f"🔍 [AI Advisor] 正在加载配置文件: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

# 3. 获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 4. 检查 Key
if not api_key:
    # 尝试找一下 .env.txt 这种常见错误
    if (project_root / ".env.txt").exists():
        print("⚠️ 警告: 发现了 .env.txt，请重命名为 .env")
    print(f"❌ [AI Advisor] 错误: 未找到 API Key，请检查 {env_path}")
    # 可以在这里临时填入 Key 进行测试 (但不建议提交)
    # api_key = "sk-..." 
else:
    print(f"✅ [AI Advisor] API Key 加载成功")

# 5. 初始化 OpenAI Client
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com" 
)

# ==========================================
# 🧹 工具函数
# ==========================================
def clean_ai_response(raw_response):
    """清洗 AI 返回的 Markdown 格式，提取纯 JSON"""
    if not raw_response:
        return ""
    clean_text = raw_response.replace("```json", "").replace("```", "")
    return clean_text.strip()

# ==========================================
# 🧠 核心功能 1: 简历诊断 (含评分理由)
# ==========================================
def analyze_resume(resume_text):
    """
    分析简历，返回包含 score_rationale 的完整 JSON
    """
    print("🚀 [AI Advisor] 正在调用 DeepSeek 进行深度诊断...")
    
    # 这个 Prompt 保留了你要求的所有字段
    system_prompt = """
    你是一位资深技术面试官。请分析简历并严格输出纯 JSON 格式。
    
    【核心要求】
    1. "score_rationale": 必须用一句话解释为什么给这个分数（这是核心功能，必填）。
    2. "suggestions": 提建议时，必须在 "evidence" 字段指出简历原文的问题。

    返回格式（纯JSON）：
    {
        "score": (0-100整数),
        "score_rationale": "评分依据",
        "summary": "综合点评",
        "pros": ["亮点1", "亮点2"],
        "cons": ["不足1", "不足2"],
        "suggestions": [
            {
                "advice": "修改建议",
                "evidence": "简历原文引用"
            }
        ],
        "matched_jobs": ["推荐岗位1", "推荐岗位2"]
    }
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"这是我的简历内容：\n{resume_text}"}
            ],
            temperature=0.2,
            response_format={ "type": "json_object" } 
        )
        
        raw_result = response.choices[0].message.content
        clean_result = clean_ai_response(raw_result)
        
        # 解析 JSON
        return json.loads(clean_result)
            
    except Exception as e:
        # 使用 repr() 防止中文报错炸毁整个程序
        print(f"❌ 分析过程出错: {repr(e)}")
        return None

# ==========================================
# ✍️ 核心功能 2: 简历生成 (你的新功能)
# ==========================================
def generate_resume_markdown(prompt: str, temperature: float = 0.6) -> str:
    """
    生成/优化简历内容（返回 Markdown 文本）
    """
    print("✍️ [AI Advisor] 正在调用 DeepSeek 生成优化版简历...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是严谨的简历优化专家，请直接输出 Markdown 格式的简历内容，不要包含 ```markdown 标记。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ 生成过程出错: {repr(e)}")
        return f"AI 生成服务暂时不可用: {str(e)}"

def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY in env.")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
print("✅ ai_advisor loaded, has get_deepseek_client:", "get_deepseek_client" in globals())

# 新增：职业体验总结Markdown生成函数（和你的main.py逻辑完全一致）
def generate_simulation_summary_markdown(role_name: str, final_score: int, hp: int, logs: list):
    """
    生成职业体验总结的Markdown内容
    :param role_name: 职业名称
    :param final_score: 最终得分
    :param hp: 剩余生命值
    :param logs: 精简后的体验日志列表
    :return: 大模型生成的Markdown格式总结字符串
    """
    # 拼接日志为prompt可用的文本格式（保留你的截断/精简逻辑）
    logs_text = ""
    for idx, log in enumerate(logs, 1):
        logs_text += f"{idx}. 场景：{log['scene']} | 选择：{log['choice']} | 反馈：{log['feedback']} | 分数变化：{log['score_change']}\n"
    
    # 你原有的prompt，一字未改，完全保留
    prompt = f"""
    你是严谨的职业规划顾问。用户刚完成【虚拟职业体验】。
    【职业】{role_name}
    【最终得分】{final_score}
    【剩余生命值】{hp}
    【体验日志】
    {logs_text}
    请基于以上信息，生成一份职业体验总结报告，要求：
    1. 包含职业匹配度分析（结合得分和行为）
    2. 分析用户的职业优势和短板
    3. 给出3条具体的职业提升建议
    4. 最后用一句话给出核心结论
    5. 全程使用markdown格式，分标题层级，语言简洁专业
    """
    
    # 调用DeepSeek大模型（复用你项目现有配置，模型名/参数不变）
    response = openai.ChatCompletion.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.7,
        max_tokens=1024
    )
    # 提取并返回生成的Markdown内容
    md_content = response.choices[0].message["content"].strip()
    return md_content


# 在 ai_advisor.py 文件末尾
__all__ = [
    "generate_simulation_summary_markdown"
]