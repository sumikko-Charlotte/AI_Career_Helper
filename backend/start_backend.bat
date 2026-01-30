@echo off
REM 一键启动 FastAPI 后端（端口 8001）

REM 切换到当前脚本所在目录（backend）
cd /d "%~dp0"

echo ==========================================
echo 🚀 启动后端服务: FastAPI (backend/main.py)
echo    监听地址: http://127.0.0.1:8001
echo ==========================================
echo.

REM 启动 Python 后端
python main.py

echo.
echo ✅ 后端进程已退出，如需重新启动请再次运行本脚本。
pause

