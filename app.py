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

if uploaded_file is not None:
    st.success(f"✅ 已上传: {uploaded_file.name}")
    
    if st.button("开始诊断 🚀"):
        # 暂时去掉 spinner，防止它卡住界面
        st.write("🔄 正在读取 PDF...")
        try:
            resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
            st.write(f"📄 提取到字符数: {len(resume_text)}")
            
            st.write("🧠 正在呼叫 AI 大脑...")
            analysis_result = ai_advisor.analyze_resume(resume_text)
            
            # 👇👇👇【关键调试步骤】直接把 AI 返回的原始数据显示出来 👇👇👇
            st.divider()
            st.subheader("🔍 原始数据调试 (Raw JSON)")
            st.json(analysis_result) # 这一行能救命，让你看到 AI 到底回了什么
            st.divider()

            if analysis_result:
                # --- 结果展示区 (穿了防弹衣的代码) ---
                
                # 1. 评分 (带默认值，防止报错)
                score = analysis_result.get('score', 0)
                st.metric(label="🏆 简历评分", value=score)

                # 2. 点评
                summary = analysis_result.get('summary', "暂无点评")
                st.info(f"📝 **点评：** {summary}")

               # 3. 详细建议 (升级版：带证据支持)
                st.subheader("💡 循证修改建议")
                try:
                    # (可选) 在建议上方显示评分依据
                    if 'score_rationale' in analysis_result:
                        st.info(f"🤔 **AI 评分判定：** {analysis_result['score_rationale']}")

                    suggestions = analysis_result.get('suggestions', [])
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        for idx, item in enumerate(suggestions, 1):
                            
                            # 情况 A：如果 AI 返回的是新格式 (字典)
                            if isinstance(item, dict):
                                advice = item.get('advice', '无建议内容')
                                evidence = item.get('evidence', '暂无定位')
                                
                                # 使用折叠面板展示，看起来更整洁
                                with st.expander(f"建议 {idx}: {advice}", expanded=True):
                                    st.markdown(f"""
                                    <div style="background-color: #f9f9f9; padding: 10px; border-radius: 4px; border-left: 4px solid #ff4b4b; font-size: 14px; color: #555;">
                                        <strong>🕵️‍♂️ 问题定位 / 证据：</strong><br>
                                        {evidence}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # 情况 B：兼容旧格式 (如果 AI 偶尔发疯返回纯文本)
                            else:
                                st.write(f"**{idx}.** {item}")
                                
                    else:
                        st.warning("AI 没有返回具体的建议列表")
                except Exception as e:
                    st.error(f"渲染建议时出错: {e}")

                # 4. 推荐岗位 (最容易崩的地方，重点保护)
                st.subheader("🎯 推荐岗位")
                try:
                    jobs = analysis_result.get('matched_jobs', [])
                    if isinstance(jobs, list) and len(jobs) > 0:
                        # 把列表变成漂亮的标签
                        st.write(" | ".join([f"**`{job}`**" for job in jobs]))
                    else:
                        st.warning("AI 没有返回推荐岗位")
                except Exception as e:
                    st.error(f"渲染岗位时出错: {e}")

            else:
                st.error("❌ AI 分析返回了空结果 (None)，请检查 API Key 或网络。")
                
        except Exception as e:
            st.error(f"💥 发生严重错误: {str(e)}")
            st.exception(e) # 打印详细报错堆栈