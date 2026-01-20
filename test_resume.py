import os
# 导入我们自己写的两个模块
import resume_parser
import ai_advisor

# --- 👇 开关：火车模式 (没网的时候改成 True) 👇 ---
MOCK_MODE = False  
# 如果是 True，就不真正调用 AI，而是返回假数据测试流程
# ------------------------------------------------

def main():
    # 1. 设定你的简历文件路径
    # 请确保文件夹里真的有一个叫 test_resume.pdf 的文件，或者改成你实际的文件名
    pdf_path = "test_resume.pdf" 
    
    print(f"🔍 正在读取简历: {pdf_path} ...")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print("❌ 错误：找不到文件！请把 PDF 放在同一个文件夹里。")
        return

    # 2. 调用 parser 提取文字
    resume_text = resume_parser.extract_text_from_pdf(pdf_path)
    print(f"✅ 读取成功！共提取了 {len(resume_text)} 个字符。")
    
    # (可选) 看看提取了什么，调试用
    # print(f"内容预览: {resume_text[:100]}...")

    print("🧠 正在请求 AI 面试官进行分析 (请稍等)...")

    # 3. 调用 AI 进行分析
    if MOCK_MODE:
        # 假数据模式
        result = {
            "score": 88,
            "summary": "模拟数据：这是一个优秀的C++选手。",
            "suggestions": ["模拟建议：多写点Python"]
        }
    else:
        # 真·AI 模式
        result = ai_advisor.analyze_resume(resume_text)

    # 4. 展示结果
    if result:
        print("\n" + "="*30)
        print(f"🏆 简历评分: {result.get('score')}")
        print(f"📝 总结: {result.get('summary')}")
        print("-" * 30)
        print("💡 修改建议:")
        for idx, suggestion in enumerate(result.get('suggestions', []), 1):
            print(f"{idx}. {suggestion}")
        print("="*30 + "\n")
    else:
        print("❌ 分析失败，请检查网络或 API Key。")

if __name__ == "__main__":
    main()