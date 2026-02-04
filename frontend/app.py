import streamlit as st
import resume_parser
import ai_advisor
import json

# 设置页面配置
st.set_page_config(page_title="AI 简历医生", page_icon="🩺", layout="wide")

# --- 侧边栏 ---
with st.sidebar:
    st.header("🛠️ 控制面板")
    st.info("💡 如果分析结果不完整，请检查下方的【原始数据调试】。")

# --- 主页面 ---
st.title("🩺 AI 简历医生 (调试版)")

# 1. 文件上传
uploaded_file = st.file_uploader("请选择 PDF 文件", type=["pdf"])

# 👇👇👇 [修改点 1] 初始化状态 (为了防止点击生成按钮时页面刷新数据丢失) 👇👇👇
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
# 👆👆👆 [修改结束] 👆👆👆

if uploaded_file is not None:
    st.success(f"✅ 已上传: {uploaded_file.name}")
    
    if st.button("开始诊断 🚀"):
        # 暂时去掉 spinner，防止它卡住界面
        st.write("🔄 正在读取 PDF...")
        try:
            # 提取文本
            resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
            st.session_state.resume_text = resume_text # 保存到状态
            st.write(f"📄 提取到字符数: {len(resume_text)}")
            
            st.write("🧠 正在呼叫 AI 大脑...")
            # 调用 AI
            result = ai_advisor.analyze_resume(resume_text)
            st.session_state.analysis_result = result # 保存到状态
            
        except Exception as e:
            st.error(f"💥 发生严重错误: {str(e)}")
            st.exception(e)

    # 👇👇👇 [修改点 2] 从状态里取数据 (这样点击生成按钮时，诊断结果不会消失) 👇👇👇
    if st.session_state.analysis_result:
        analysis_result = st.session_state.analysis_result
        # 👆👆👆 [修改结束] 👆👆👆

        # === 以下是你原来的代码 (完全保留) ===
        
        # 👇👇👇【关键调试步骤】直接把 AI 返回的原始数据显示出来 👇👇👇
        st.divider()
        st.subheader("🔍 原始数据调试 (Raw JSON)")
        st.json(analysis_result) 
        st.divider()

        # --- 结果展示区 (穿了防弹衣的代码) ---
        
        # 1. 评分
        score = analysis_result.get('score', 0)
        st.metric(label="🏆 简历评分", value=score)

        # 2. 点评
        summary = analysis_result.get('summary', "暂无点评")
        st.info(f"📝 **点评：** {summary}")

        # 3. 详细建议
        st.subheader("💡 循证修改建议")
        try:
            if 'score_rationale' in analysis_result:
                st.info(f"🤔 **AI 评分判定：** {analysis_result['score_rationale']}")

            suggestions = analysis_result.get('suggestions', [])
            if isinstance(suggestions, list) and len(suggestions) > 0:
                for idx, item in enumerate(suggestions, 1):
                    if isinstance(item, dict):
                        advice = item.get('advice', '无建议内容')
                        evidence = item.get('evidence', '暂无定位')
                        with st.expander(f"建议 {idx}: {advice}", expanded=True):
                            st.markdown(f"""
                            <div style="background-color: #f9f9f9; padding: 10px; border-radius: 4px; border-left: 4px solid #ff4b4b; font-size: 14px; color: #555;">
                                <strong>🕵️‍♂️ 问题定位 / 证据：</strong><br>
                                {evidence}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write(f"**{idx}.** {item}")
            else:
                st.warning("AI 没有返回具体的建议列表")
        except Exception as e:
            st.error(f"渲染建议时出错: {e}")

        # 4. 推荐岗位
        st.subheader("🎯 推荐岗位")
        try:
            jobs = analysis_result.get('matched_jobs', [])
            if isinstance(jobs, list) and len(jobs) > 0:
                st.write(" | ".join([f"**`{job}`**" for job in jobs]))
            else:
                st.warning("AI 没有返回推荐岗位")
        except Exception as e:
            st.error(f"渲染岗位时出错: {e}")
            
        # === 你原来的代码结束 ===

        # 👇👇👇 [修改点 3] 新增：简历生成功能 (无缝拼接在最后) 👇👇👇
        st.markdown("---")
        st.subheader("✨ AI 简历生成")
        st.write("AI 将根据上述诊断建议，为您重写一份 Markdown 格式的简历。")

        if st.button("⚡ 立即生成优化版简历"):
            with st.spinner("✍️ AI 正在重写简历，请稍候..."):
                try:
                    # 1. 准备 Prompt
                    prompt = f"""
                    请根据以下原始简历内容和修改建议，重写一份优化后的简历。
                    
                    【原始简历】：
                    {st.session_state.resume_text[:2000]}
                    
                    【修改建议】：
                    {json.dumps(analysis_result.get('suggestions', []), ensure_ascii=False)}
                    
                    要求：
                    1. 使用标准 Markdown 格式。
                    2. 针对建议点进行具体修改。
                    3. 优化语言表达，使其更专业。
                    """
                    
                    # 2. 调用生成接口
                    optimized_content = ai_advisor.generate_resume_markdown(prompt)
                    
                    # 3. 显示结果
                    st.success("🎉 生成成功！")
                    
                    # 4. 预览与下载
                    st.text_area("Markdown 源码预览", value=optimized_content, height=300)
                    
                    st.download_button(
                        label="📥 下载优化后的简历 (.md)",
                        data=optimized_content,
                        file_name="optimized_resume.md",
                        mime="text/markdown"
                    )
                    
                    # 5. 渲染预览
                    with st.expander("👁️ 查看渲染效果", expanded=True):
                        st.markdown(optimized_content)

                except Exception as e:
                    st.error(f"生成失败: {e}")
        # 👆👆👆 [新增结束] 👆👆👆