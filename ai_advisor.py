import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# ==========================================
# 👇 终极修复：直接指定绝对路径 (硬编码) 👇
# ==========================================

# 1. 直接写死你的项目根目录 (根据你的截图填写的)
# 注意：前面的 r 表示不转义，防止 Windows 路径斜杠报错
project_root = Path(r"C:\Users\sumik\Desktop\AI_Project")

# 2. 拼出 .env 的位置
env_path = project_root / ".env"

# 3. 🐛 调试：先看看目录下到底有什么文件？
# (这一步会把根目录下所有文件名打印出来，如果叫 .env.txt 你一眼就能看到)
if project_root.exists():
    print(f"📂 正在扫描目录: {project_root}")
    print(f"📄 目录下的文件有: {os.listdir(project_root)}")
else:
    print(f"❌ 目录不存在: {project_root}")

# 4. 尝试加载
print(f"🔍 正在尝试加载: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

# 5. 获取 Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 6. 如果还是没有...
if not api_key:
    # 尝试找一下是不是叫 .env.txt
    txt_path = project_root / ".env.txt"
    if txt_path.exists():
        raise ValueError(f"⚠️ 找到了！你的文件被命名为了 '.env.txt' (有个隐藏后缀)。\n请在文件夹里重命名，把 '.txt' 删掉！")
    
    raise ValueError(f"⚠️ 彻底没找到 Key。\n请确认 C:\\Users\\sumik\\Desktop\\AI_Project 下确实有一个叫 .env 的文件。")

# ==========================================
# 👆 修复结束 👆
# ==========================================

client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com" 
)

# ... 下面的代码不要动 ...
# --- 清洗函数 (保持不变) ---
def clean_ai_response(raw_response):
    clean_text = raw_response.replace("```json", "").replace("```", "")
    return clean_text.strip()

def analyze_resume(resume_text):
    # 👇 关键修正：为了配合你的前端展示，Prompt 必须包含 score_rationale 和 evidence
    # 如果这里不改，你的前端网页上“评分依据”和“证据框”就是空的
    system_prompt = """
    你是一位资深技术面试官。请分析简历并严格输出纯 JSON 格式。
    
    【重要要求】
    1. "score_rationale": 必须用一句话解释为什么给这个分数。
    2. "suggestions": 提建议时，必须在 "evidence" 字段指出简历原文的问题。

    返回格式（纯JSON）：
    {
        "score": (0-100整数),
        "score_rationale": "评分依据",
        "summary": "点评",
        "pros": ["亮点1", "亮点2"],
        "cons": ["不足1", "不足2"],
        "suggestions": [
            {
                "advice": "修改建议",
                "evidence": "简历原文引用"
            }
        ],
        "matched_jobs": ["岗位1", "岗位2"]
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
        return json.loads(clean_result) 
        
    except Exception as e:
        print(f"AI 调用出错: {e}")
        return None