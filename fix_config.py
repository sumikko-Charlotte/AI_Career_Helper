import os

# 这是你想要的深蓝主题配置
config_content = """[client]
showErrorDetails = false

[toolbar]
mode = "viewer"

[theme]
primaryColor = "#165DFF"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#EFF6FF"
textColor = "#1E293B"
font = "sans serif"
"""

# 确保文件夹存在
os.makedirs(".streamlit", exist_ok=True)

# 强制用 UTF-8 编码写入，覆盖原有文件
with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
    f.write(config_content)

print("✅ 配置文件已成功修复！原来的乱码已经被清理干净了。")
print("🚀 现在请重新运行: python -m streamlit run app.py")