"""
streamlit_app.py

一个可直接运行的 Streamlit 应用入口：
- 优先复用项目里现有的 Streamlit 核心流程（PDF 上传 -> 文本提取 -> AI 诊断/生成）。
- 针对检查报告指出的依赖问题（resume_parser 接口不匹配、ai_advisor 可能运行时报错），做了“安全降级”：
  - 能导入并正常调用则走原逻辑
  - 任何一步不可用则提供可访问的 Demo 页面能力，保证 `streamlit run streamlit_app.py` 一定能启动

启动命令（PowerShell / CMD 通用）：
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
import threading
import time

import requests
import streamlit as st


BACKEND_KEEPALIVE_URL = "https://ai-career-helper-backend-u1s0.onrender.com/health"
KEEPALIVE_INTERVAL_SECONDS = 600  # 10 分钟


def _backend_keepalive_worker() -> None:
    """在 Streamlit 运行期间定期请求后端，降低后端休眠概率"""
    while True:
        try:
            resp = requests.get(BACKEND_KEEPALIVE_URL, timeout=10)
            print(f"[streamlit keepalive] backend -> {resp.status_code}")
        except Exception as e:  # noqa: BLE001
            print(f"[streamlit keepalive] error: {e}")
        time.sleep(KEEPALIVE_INTERVAL_SECONDS)


# 在脚本加载时启动后台线程（daemon 不会阻塞应用退出）
threading.Thread(target=_backend_keepalive_worker, daemon=True).start()


def _safe_import_resume_parser():
    try:
        import resume_parser  # type: ignore
        return resume_parser
    except Exception as e:
        return e


def _safe_import_ai_advisor():
    try:
        import ai_advisor  # type: ignore
        return ai_advisor
    except Exception as e:
        return e


def _extract_text_from_pdf(uploaded_file) -> str:
    """
    兼容两种实现：
    - 若项目现有 `resume_parser.extract_text_from_pdf` 可用，则优先调用
      - 如果它只能接受路径：会先落盘为临时文件再调用
      - 如果它能接受 file-like：直接传入
    - 否则使用内置兜底（pypdf）从 UploadedFile bytes 中提取
    """
    resume_parser = _safe_import_resume_parser()

    # 1) 复用项目实现（如果存在）
    if not isinstance(resume_parser, Exception) and hasattr(resume_parser, "extract_text_from_pdf"):
        fn = getattr(resume_parser, "extract_text_from_pdf")
        # 1.1) 先尝试直接传 UploadedFile
        try:
            return fn(uploaded_file) or ""
        except Exception:
            # 1.2) 不支持 UploadedFile：保存到临时文件路径再调用
            suffix = Path(uploaded_file.name).suffix or ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            return fn(tmp_path) or ""

    # 2) 内置兜底：pypdf
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text
    except Exception:
        # 进一步兜底：保存成临时文件再用 PdfReader(path)
        from pypdf import PdfReader  # type: ignore

        suffix = Path(uploaded_file.name).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        reader = PdfReader(tmp_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text


def _ai_analyze(resume_text: str) -> Dict[str, Any]:
    """
    优先调用项目的 ai_advisor.analyze_resume。
    若不可用/报错，则返回一个可展示的 mock 结果，保证页面可用。
    """
    ai_advisor = _safe_import_ai_advisor()
    if not isinstance(ai_advisor, Exception) and hasattr(ai_advisor, "analyze_resume"):
        try:
            result = ai_advisor.analyze_resume(resume_text)
            if isinstance(result, dict):
                return result
        except Exception as e:
            return {
                "score": 0,
                "summary": "AI 诊断模块当前不可用（调用失败）。",
                "error": str(e),
                "suggestions": [
                    {"advice": "请检查 .env 是否配置 DEEPSEEK_API_KEY", "evidence": "环境变量缺失会导致调用失败"},
                    {"advice": "确认 openai/python-dotenv 版本与代码兼容", "evidence": "依赖版本不一致可能导致 API 调用异常"},
                ],
                "matched_jobs": [],
            }

    # mock 兜底
    return {
        "score": 82,
        "score_rationale": "基础分 70；内容结构清晰 +8；缺少量化成果 - - -（示例 mock）。",
        "summary": "这是一个可访问的 Demo 结果：核心流程可跑通，但 AI 诊断尚未接通或不可用。",
        "suggestions": [
            {"advice": "为每段经历补齐量化指标（如性能提升、成本降低）", "evidence": "当前描述偏职责，缺少结果数据"},
            {"advice": "增加作品集/GitHub 链接与项目截图", "evidence": "背书信息不足"},
        ],
        "matched_jobs": ["后端开发", "全栈开发", "数据开发"],
    }


def _ai_generate_resume_markdown(prompt: str) -> str:
    """
    优先调用项目 ai_advisor.generate_resume_markdown。
    不可用则返回一个可下载的 Demo Markdown。
    """
    ai_advisor = _safe_import_ai_advisor()
    if not isinstance(ai_advisor, Exception) and hasattr(ai_advisor, "generate_resume_markdown"):
        try:
            out = ai_advisor.generate_resume_markdown(prompt)
            if isinstance(out, str) and out.strip():
                return out.strip()
        except Exception as e:
            return f"# 生成失败（Demo）\n\n- 错误信息：{e}\n\n请检查 AI 配置与依赖。"

    return (
        "# 优化版简历（Demo）\n\n"
        "## 基本信息\n- 姓名：你的名字\n- 邮箱：you@example.com\n- 电话：138-xxxx-xxxx\n\n"
        "## 技能\n- Python / FastAPI / MySQL\n- Vue3 / Element Plus\n\n"
        "## 项目经历（示例）\n- 使用 STAR 法则描述项目背景、任务、行动与结果。\n"
    )


def _init_state():
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "optimized_markdown" not in st.session_state:
        st.session_state.optimized_markdown = ""


def main():
    st.set_page_config(page_title="AI 简历医生", page_icon="🩺", layout="wide")

    _init_state()

    with st.sidebar:
        st.header("🛠️ 控制面板")
        st.caption("此入口为根目录一键可运行版本：会自动复用项目模块，并在失败时降级到 Demo。")
        st.info("💡 若分析/生成结果不完整，请查看页面中的【原始数据调试】。")

        st.subheader("运行环境自检")
        rp = _safe_import_resume_parser()
        aa = _safe_import_ai_advisor()
        st.write("- resume_parser:", "✅ 可导入" if not isinstance(rp, Exception) else f"⚠️ 导入失败：{rp}")
        st.write("- ai_advisor:", "✅ 可导入" if not isinstance(aa, Exception) else f"⚠️ 导入失败：{aa}")

    st.title("🩺 AI 简历医生（可运行版）")

    uploaded_file = st.file_uploader("请选择 PDF 文件", type=["pdf"])

    if uploaded_file is None:
        st.markdown(
            "你可以先上传一份 PDF 简历体验完整流程。若暂时没有文件，也可以在右侧看到模块自检结果。"
        )
        st.stop()

    st.success(f"✅ 已上传: {uploaded_file.name}")

    if st.button("开始诊断 🚀"):
        st.write("🔄 正在读取 PDF...")
        try:
            resume_text = _extract_text_from_pdf(uploaded_file)
            st.session_state.resume_text = resume_text
            st.write(f"📄 提取到字符数: {len(resume_text)}")
        except Exception as e:
            st.error(f"💥 读取 PDF 失败: {e}")
            st.exception(e)
            st.stop()

        st.write("🧠 正在呼叫 AI 大脑...")
        result = _ai_analyze(st.session_state.resume_text)
        st.session_state.analysis_result = result

    if not st.session_state.analysis_result:
        st.stop()

    analysis_result: Dict[str, Any] = st.session_state.analysis_result

    st.divider()
    st.subheader("🔍 原始数据调试 (Raw JSON)")
    st.json(analysis_result)
    st.divider()

    score = analysis_result.get("score", 0)
    st.metric(label="🏆 简历评分", value=score)

    summary = analysis_result.get("summary", "暂无点评")
    st.info(f"📝 **点评：** {summary}")

    st.subheader("💡 循证修改建议")
    if "score_rationale" in analysis_result:
        st.info(f"🤔 **AI 评分判定：** {analysis_result.get('score_rationale')}")

    suggestions = analysis_result.get("suggestions", [])
    if isinstance(suggestions, list) and suggestions:
        for idx, item in enumerate(suggestions, 1):
            if isinstance(item, dict):
                advice = item.get("advice", "无建议内容")
                evidence = item.get("evidence", "暂无定位")
                with st.expander(f"建议 {idx}: {advice}", expanded=True):
                    st.markdown(
                        f"""
<div style="background-color: #f9f9f9; padding: 10px; border-radius: 4px; border-left: 4px solid #ff4b4b; font-size: 14px; color: #555;">
  <strong>🕵️‍♂️ 问题定位 / 证据：</strong><br>
  {evidence}
</div>
""",
                        unsafe_allow_html=True,
                    )
            else:
                st.write(f"**{idx}.** {item}")
    else:
        st.warning("AI 没有返回具体的建议列表（或当前为 Demo 模式）。")

    st.subheader("🎯 推荐岗位")
    jobs = analysis_result.get("matched_jobs", [])
    if isinstance(jobs, list) and jobs:
        st.write(" | ".join([f"**`{job}`**" for job in jobs]))
    else:
        st.warning("AI 没有返回推荐岗位（或当前为 Demo 模式）。")

    st.markdown("---")
    st.subheader("✨ AI 简历生成")
    st.write("AI 将根据上述诊断建议，为你重写一份 Markdown 格式的简历。")

    if st.button("⚡ 立即生成优化版简历"):
        with st.spinner("✍️ AI 正在重写简历，请稍候..."):
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
            optimized_content = _ai_generate_resume_markdown(prompt)
            st.session_state.optimized_markdown = optimized_content
            st.success("🎉 生成完成！")

    if st.session_state.optimized_markdown:
        st.text_area("Markdown 源码预览", value=st.session_state.optimized_markdown, height=300)
        st.download_button(
            label="📥 下载优化后的简历 (.md)",
            data=st.session_state.optimized_markdown,
            file_name="optimized_resume.md",
            mime="text/markdown",
        )
        with st.expander("👁️ 查看渲染效果", expanded=True):
            st.markdown(st.session_state.optimized_markdown)


if __name__ == "__main__":
    main()

