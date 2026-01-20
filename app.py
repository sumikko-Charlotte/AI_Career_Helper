import streamlit as st
import os
import resume_parser
import ai_advisor

# 设置页面标题和图标
st.set_page_config(page_title="AI 简历医生", page_icon="🩺")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🛠️ 控制面板")
    api_key = st.text_input("输入 DeepSeek API Key", type="password")
    st.info("💡 如果在本地测试没有 Key，系统将使用模拟数据。")

# --- 主页面 ---
st.title("🩺 AI 简历医生")
st.markdown("上传你的简历 (PDF)，AI 面试官将为你提供 **评分** 与 **修改建议**。")

# 1. 文件上传器
uploaded_file = st.file_uploader("请选择 PDF 文件", type=["pdf"])

if uploaded_file is not None:
    # 2. 显示文件名
    st.success(f"✅ 已上传: {uploaded_file.name}")
    
    # 3. 点击开始分析
    if st.button("开始诊断 🚀"):
        with st.spinner("AI 正在阅读并分析你的简历..."):
            try:
                # 关键步骤：Streamlit 的文件对象可以直接被 pypdf 读取
                # 我们不需要保存到本地，直接传给 parser
                resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
                
                # 调用 AI (如果没有填 Key，这里你可以加个判断让 ai_advisor 走 Mock 模式)
                # 这里的逻辑建议修改 ai_advisor 支持传入 key，或者用环境变量
                # 简单起见，我们假设 ai_advisor 内部已经配好了，或者走了 Mock
                
                # 为了演示，如果没填 Key 且 ai_advisor 里没写死 Key，可能会报错
                # 建议：在 ai_advisor.py 里把 MOCK_MODE 设为 True 先跑通 UI
                analysis_result = ai_advisor.analyze_resume(resume_text)
                
                if analysis_result:
                    # --- 结果展示区 ---
                    
                    # 第一行：评分大字展示
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric(label="简历评分", value=analysis_result.get('score', 0))
                    with col2:
                        st.info(f"**一句话点评：** {analysis_result.get('summary')}")
                    
                    st.divider()
                    
                    # 第二行：详细建议
                    st.subheader("💡 修改建议")
                    for idx, suggestion in enumerate(analysis_result.get('suggestions', []), 1):
                        st.write(f"**{idx}.** {suggestion}")
                        
                    # 第三行：推荐岗位
                    st.subheader("🎯 推荐岗位")
                    tags = analysis_result.get('matched_jobs', [])
                    st.write(" | ".join([f"`{tag}`" for tag in tags]))
                    
                else:
                    st.error("分析失败，请检查 API Key 或网络。")
                    
            except Exception as e:
                st.error(f"发生错误: {str(e)}")