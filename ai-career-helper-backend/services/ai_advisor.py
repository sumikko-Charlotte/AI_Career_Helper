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

# ... (上面的代码保持不变) ...

def analyze_resume(resume_text):
    print("🚀 [AI Advisor] 正在调用 DeepSeek 进行深度诊断...")
    
    # 👇👇👇 修改了这里的 JSON Key，为了匹配前端 👇👇👇
    system_prompt = """
    你是一位资深技术面试官。请分析简历并严格输出纯 JSON 格式。
    
    【核心要求】
    1. "score_rationale": 必须用一句话解释为什么给这个分数。
    2. "suggestions": 提建议时，必须在 "evidence" 字段指出简历原文的问题。

    返回格式（纯JSON）：
    {
        "score": (0-100整数),
        "score_rationale": "评分依据",
        "summary": "综合点评",
        "strengths": ["亮点1", "亮点2"],   <-- 改成了 strengths
        "weaknesses": ["不足1", "不足2"],   <-- 改成了 weaknesses
        "suggestions": [
            {
                "advice": "修改建议",
                "evidence": "简历原文引用"
            }
        ],
        "matched_jobs": ["推荐岗位1", "推荐岗位2"]
    }
    """
    
    # ... (下面的代码保持不变) ...
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