import json
import os
from openai import OpenAI

# 配置你的 API Key
# ⚠️ 注意：不要把真实的 Key 提交到 GitHub
client = OpenAI(
    # 建议把 Key 填在这里，但在提交代码前记得删掉，或者用环境变量
    api_key="sk-d7497f8619b44e1da0b225aedef5ff9b", 
    base_url="https://api.deepseek.com" 
)

# --- 👇 清洗函数 👇 ---
def clean_ai_response(raw_response):
    """
    负责把 AI 返回的 Markdown 格式（```json ... ```）清洗成纯净的 JSON 字符串
    """
    clean_text = raw_response.replace("```json", "").replace("```", "").strip()
    return clean_text

def analyze_resume(resume_text):
    # 👇 修改了 Prompt：增加了 "score_rationale" 和 "evidence" 的要求
    system_prompt = """
    你是一位严厉但专业的资深技术面试官。请阅读用户的简历，并严格按照下面的 JSON 格式返回分析结果。
    
    【重要要求】
    1. 评分要有依据，必须在 "score_rationale" 中说明扣分点。
    2. 提建议时必须“有凭有据”，在 "evidence" 字段中引用简历原文，或者指出缺少的具体板块。

    返回格式要求（不要包含 Markdown，只返回纯 JSON）：
    {
        "score": (0-100整数),
        "score_rationale": "一句话解释评分依据（例如：基础扎实，但缺少量化数据，因此扣分）",
        "summary": "50字以内的专业点评",
        "pros": ["亮点1", "亮点2", "亮点3"],
        "cons": ["不足1", "不足2", "不足3"],
        "suggestions": [
            {
                "advice": "具体的修改建议（例如：使用STAR法则重写）",
                "evidence": "关联的简历原文（例如：简历中写道'负责后端开发'，但未提及具体并发量）"
            },
            {
                "advice": "具体的修改建议2",
                "evidence": "关联的简历原文或缺失说明"
            }
        ],
        "matched_jobs": ["岗位1", "岗位2", "岗位3"]
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
        print(f"❌ AI 分析失败: {e}")
        return None