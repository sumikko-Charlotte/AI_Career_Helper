#!/bin/bash
# App.vue 模拟面试板块重构 - 快速启动脚本

echo "🚀 职航——AI辅助的大学生生涯成长平台 - 模拟面试模块重构"
echo "=============================================="
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未安装 Node.js，请先安装"
    exit 1
fi

echo "✅ Node.js 已安装"
echo ""

# 进入前端目录
cd frontend || exit

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，安装依赖..."
    npm install
    echo ""
fi

echo "📝 配置检查："
echo "  ✅ 后端地址: http://127.0.0.1:8000"
echo "  ✅ API 端点: /api/chat"
echo "  ✅ 前端地址: http://localhost:5173"
echo ""

echo "🎯 功能检查清单："
echo "  ✅ 面试官动态头像"
echo "  ✅ 语音输入 (Web Speech API)"
echo "  ✅ 现代聊天气泡设计"
echo ""

echo "🚀 启动开发服务..."
echo "访问地址: http://localhost:5173"
echo "点击左侧菜单 '模拟面试' 查看新功能"
echo ""

npm run dev
