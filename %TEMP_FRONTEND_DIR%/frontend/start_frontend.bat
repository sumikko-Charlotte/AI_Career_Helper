@echo off
REM 一键启动前端 Vite 开发服务器

REM 切换到当前脚本所在目录（frontend）
cd /d "%~dp0"

echo ==========================================
echo 🚀 启动前端服务: Vue3 + Vite
echo    目录: %cd%
echo ==========================================
echo.

REM 如果尚未安装依赖，则自动安装
IF NOT EXIST "node_modules" (
  echo 📦 检测到首次运行，正在安装依赖（npm install）...
  npm install
  IF ERRORLEVEL 1 (
    echo ❌ 依赖安装失败，请检查 Node/npm 环境。
    pause
    exit /b 1
  )
)

echo.
echo ✅ 依赖已就绪，启动开发服务器：npm run dev
echo.

npm run dev

echo.
echo ✅ 前端 dev 进程已退出，如需重新启动请再次运行本脚本。
pause

