#!/bin/bash

###############################################################################
# TravelMate AI - 一键启动脚本
# 功能：环境检查、依赖安装、后端启动、前端启动
###############################################################################

# 不使用 set -e，手动处理错误
# set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录（脚本在scripts目录下，需要回到上级目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOGS_DIR="$SCRIPT_DIR/logs"

# 创建日志目录
mkdir -p "$LOGS_DIR"

# 日志文件
BACKEND_LOG="$LOGS_DIR/backend.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"
INSTALL_LOG="$LOGS_DIR/install.log"

###############################################################################
# 工具函数
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

###############################################################################
# 环境检查
###############################################################################

check_environment() {
    print_header "环境检查"
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_success "Python 已安装: $PYTHON_VERSION"
    else
        print_error "Python3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js 已安装: $NODE_VERSION"
    else
        print_error "Node.js 未安装，请先安装 Node.js 16+"
        exit 1
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm 已安装: $NPM_VERSION"
    else
        print_error "npm 未安装"
        exit 1
    fi
    
    # 检查 .env 文件
    if [ -f "$BACKEND_DIR/.env" ]; then
        print_success ".env 配置文件存在"
    else
        print_warning ".env 文件不存在，将使用默认配置"
        if [ -f "$BACKEND_DIR/env.example" ]; then
            cp "$BACKEND_DIR/env.example" "$BACKEND_DIR/.env"
            print_info "已从 env.example 创建 .env 文件，请配置 API Key"
        fi
    fi
}

###############################################################################
# 后端设置
###############################################################################

setup_backend() {
    print_header "后端环境配置"
    
    cd "$BACKEND_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv >> "$INSTALL_LOG" 2>&1
        print_success "虚拟环境创建完成"
    else
        print_success "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip >> "$INSTALL_LOG" 2>&1
    print_success "pip 升级完成"
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装 Python 依赖包..."
        pip install -r requirements.txt >> "$INSTALL_LOG" 2>&1
        print_success "Python 依赖安装完成"
    else
        print_warning "requirements.txt 不存在，跳过依赖安装"
    fi
    
    cd "$PROJECT_ROOT"
}

###############################################################################
# 前端设置
###############################################################################

setup_frontend() {
    print_header "前端环境配置"
    
    cd "$FRONTEND_DIR"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖包..."
        npm install >> "$INSTALL_LOG" 2>&1
        print_success "前端依赖安装完成"
    else
        print_success "前端依赖已安装"
    fi
    
    cd "$PROJECT_ROOT"
}

###############################################################################
# 停止现有服务
###############################################################################

stop_services() {
    print_header "停止现有服务并清理端口"
    
    # 停止后端（通过端口号）
    BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$BACKEND_PORT_PID" ]; then
        print_info "发现端口8000被占用 (PID: $BACKEND_PORT_PID)，正在清理..."
        kill -9 $BACKEND_PORT_PID 2>/dev/null || true
        print_success "端口8000已释放"
    fi
    
    # 停止后端（通过进程名）
    BACKEND_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')
    if [ -n "$BACKEND_PID" ]; then
        print_info "停止后端服务进程 (PID: $BACKEND_PID)..."
        kill -9 $BACKEND_PID 2>/dev/null || true
        print_success "后端服务已停止"
    fi
    
    # 停止前端（通过端口号）
    FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null)
    if [ -n "$FRONTEND_PORT_PID" ]; then
        print_info "发现端口5173被占用 (PID: $FRONTEND_PORT_PID)，正在清理..."
        kill -9 $FRONTEND_PORT_PID 2>/dev/null || true
        print_success "端口5173已释放"
    fi
    
    # 停止前端（通过进程名）
    FRONTEND_PID=$(ps aux | grep "npm.*run.*dev" | grep -v grep | awk '{print $2}')
    if [ -n "$FRONTEND_PID" ]; then
        print_info "停止前端服务进程 (PID: $FRONTEND_PID)..."
        kill -9 $FRONTEND_PID 2>/dev/null || true
        print_success "前端服务已停止"
    fi
    
    # 停止 vite 进程
    VITE_PID=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
    if [ -n "$VITE_PID" ]; then
        print_info "停止 Vite 进程 (PID: $VITE_PID)..."
        kill -9 $VITE_PID 2>/dev/null || true
    fi
    
    # 如果没有找到任何服务
    if [ -z "$BACKEND_PORT_PID" ] && [ -z "$BACKEND_PID" ] && [ -z "$FRONTEND_PORT_PID" ] && [ -z "$FRONTEND_PID" ]; then
        print_info "没有发现运行中的服务"
    fi
    
    # 等待端口完全释放
    sleep 2
    
    # 二次确认端口已释放
    if lsof -ti:8000 > /dev/null 2>&1; then
        print_warning "端口8000仍被占用，强制清理..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    if lsof -ti:5173 > /dev/null 2>&1; then
        print_warning "端口5173仍被占用，强制清理..."
        lsof -ti:5173 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    print_success "端口清理完成"
}

###############################################################################
# 启动服务
###############################################################################

start_backend() {
    print_header "启动后端服务"
    
    # 再次确认端口8000未被占用
    if lsof -ti:8000 > /dev/null 2>&1; then
        print_error "端口8000仍被占用，无法启动后端"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 清空旧日志
    > "$BACKEND_LOG"
    
    # 启动后端
    print_info "启动 FastAPI 服务..."
    nohup python main.py > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    
    # 等待启动
    sleep 3
    
    # 检查是否启动成功
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_success "后端服务启动成功 (PID: $BACKEND_PID)"
        print_info "后端地址: http://localhost:8000"
        print_info "API文档: http://localhost:8000/docs"
        print_info "日志文件: $BACKEND_LOG"
    else
        print_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        tail -20 "$BACKEND_LOG"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
}

start_frontend() {
    print_header "启动前端服务"
    
    # 再次确认端口5173未被占用
    if lsof -ti:5173 > /dev/null 2>&1; then
        print_error "端口5173仍被占用，无法启动前端"
        lsof -ti:5173 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    cd "$FRONTEND_DIR"
    
    # 清空旧日志
    > "$FRONTEND_LOG"
    
    # 启动前端
    print_info "启动 Vite 开发服务器..."
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    
    # 等待启动
    sleep 5
    
    # 检查是否启动成功
    if lsof -ti:5173 > /dev/null 2>&1; then
        print_success "前端服务启动成功 (PID: $FRONTEND_PID)"
        print_info "前端地址: http://localhost:5173"
        print_info "日志文件: $FRONTEND_LOG"
    else
        print_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
        tail -20 "$FRONTEND_LOG"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
}

###############################################################################
# 显示状态
###############################################################################

show_status() {
    print_header "服务状态"
    
    echo ""
    echo -e "${GREEN}✓ 所有服务已启动${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}前端服务:${NC} http://localhost:5173"
    echo -e "${YELLOW}后端服务:${NC} http://localhost:8000"
    echo -e "${YELLOW}API文档:${NC}  http://localhost:8000/docs"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}日志文件:${NC}"
    echo -e "  后端: $BACKEND_LOG"
    echo -e "  前端: $FRONTEND_LOG"
    echo -e "  安装: $INSTALL_LOG"
    echo ""
    echo -e "${BLUE}查看日志:${NC}"
    echo -e "  tail -f $BACKEND_LOG"
    echo -e "  tail -f $FRONTEND_LOG"
    echo ""
    echo -e "${BLUE}停止服务:${NC}"
    echo -e "  ./stop.sh"
    echo ""
}

###############################################################################
# 主流程
###############################################################################

main() {
    clear
    
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║      TravelMate AI 启动脚本           ║"
    echo "║   智能旅游攻略生成系统                 ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # 1. 环境检查
    check_environment
    
    # 2. 停止现有服务
    stop_services
    
    # 3. 设置后端
    setup_backend
    
    # 4. 设置前端
    setup_frontend
    
    # 5. 启动后端
    start_backend
    
    # 6. 启动前端
    start_frontend
    
    # 7. 显示状态
    show_status
    
    print_success "启动完成！"
}

# 执行主流程
main

