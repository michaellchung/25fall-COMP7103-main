#!/bin/bash

# TravelMate AI 开发环境启动脚本

echo "🚀 Starting TravelMate AI Development Environment..."
echo ""

# 检查是否在项目根目录
if [ ! -f "PRD.md" ]; then
    echo "❌ Error: Please run this script from project root directory"
    exit 1
fi

# 启动后端
echo "📦 Starting Backend (FastAPI)..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt

# 启动后端服务（后台运行）
echo "✅ Starting FastAPI server on http://localhost:8000"
python main.py &
BACKEND_PID=$!

cd ..

# 启动前端
echo ""
echo "📦 Starting Frontend (Vue.js)..."
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# 启动前端服务
echo "✅ Starting Vite dev server on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✨ TravelMate AI is running!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# 捕获Ctrl+C信号
trap "echo ''; echo '👋 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait

