import json
import os
from openai import OpenAI
from dotenv import load_dotenv # 👈 刚刚装的库

# 1. 加载 .env 文件
load_dotenv()

# 2. 从环境里拿 Key，而不是写死在代码里
api_key = os.getenv("DEEPSEEK_API_KEY")

# 防呆检查
if not api_key:
    raise ValueError("⚠️ 没找到 Key！请检查 .env 文件有没有建好。")

client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com" 
)

# ... 下面保持不变 ...

# --- 👇 新增：清洗函数放在这里 👇 ---
def clean_ai_response(raw_response):
    """
    这个函数负责把 AI 返回的 Markdown 格式（```json ... ```）
    清洗成纯净的 JSON 字符串
    """
    # 1. 去掉开头的 ```json
    clean_text = raw_response.replace("```json", "")
    # 2. 去掉结尾的 ```
    clean_text = clean_text.replace("```", "")
    # 3. 去掉首尾空白
    return clean_text.strip()
# ------------------------------------

def analyze_resume(resume_text):
    system_prompt = """
    你是一位资深技术面试官。请分析简历并严格输出纯 JSON 格式。
    包含字段：score, summary, pros, cons, suggestions, matched_jobs。
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"这是我的简历内容：\n{resume_text}"}
            ],
            temperature=0.1,
            # 虽然加了 json_object，但为了保险，我们还是清洗一下
            response_format={ "type": "json_object" } 
        )
        
        # 拿到原始结果
        raw_result = response.choices[0].message.content
        
        # --- 👇 关键步骤：调用清洗函数 👇 ---
        clean_result = clean_ai_response(raw_result)
        # ----------------------------------
        
        # 现在再转 JSON 就不会报错了
        return json.loads(clean_result) 
        
    except Exception as e:
        print(f"AI 调用出错: {e}")
        return None