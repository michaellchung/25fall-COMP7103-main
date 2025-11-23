#!/bin/bash

###############################################################################
# TravelMate AI - 停止服务脚本
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header "停止 TravelMate AI 服务"

# 停止后端
BACKEND_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')
if [ -n "$BACKEND_PID" ]; then
    print_info "停止后端服务 (PID: $BACKEND_PID)..."
    kill -9 $BACKEND_PID 2>/dev/null || true
    print_success "后端服务已停止"
else
    print_info "后端服务未运行"
fi

# 停止前端
FRONTEND_PID=$(lsof -ti:5173 2>/dev/null)
if [ -n "$FRONTEND_PID" ]; then
    print_info "停止前端服务 (PID: $FRONTEND_PID)..."
    kill -9 $FRONTEND_PID 2>/dev/null || true
    print_success "前端服务已停止"
else
    print_info "前端服务未运行"
fi

echo ""
print_success "所有服务已停止"
echo ""

