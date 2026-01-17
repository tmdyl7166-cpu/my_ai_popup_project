#!/bin/bash
#===============================================================================
# my_ai_popup_project 热窗口启动脚本
# 功能: 启动热窗口GUI界面
#===============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "my_ai_popup_project 热窗口启动"
echo "==========================================${NC}"
echo ""

# 获取项目根目录
get_project_root() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

PROJECT_ROOT=$(get_project_root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
VENV_PATH="$PROJECT_ROOT/ai_popup_env"
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
else
    echo -e "${RED}错误: 虚拟环境不存在${NC}"
    echo "请先运行: bash scripts/setup_env.sh"
    exit 1
fi

# 检查GUI模块是否存在
if [ ! -d "$PROJECT_ROOT/src/frontend" ]; then
    echo -e "${RED}错误: 前端模块不存在${NC}"
    exit 1
fi

# 检查显示环境
if [ -z "${DISPLAY:-}" ]; then
    echo -e "${YELLOW}⚠ 未检测到显示环境${NC}"
    echo "如果在无头环境中运行，请设置DISPLAY变量"
    echo "例如: export DISPLAY=:0"
fi

# 启动热窗口
echo -e "${YELLOW}启动热窗口...${NC}"

# 检查是否有主窗口脚本
if [ -f "$PROJECT_ROOT/src/frontend/main_window.py" ]; then
    python3 "$PROJECT_ROOT/src/frontend/main_window.py" &
elif [ -f "$PROJECT_ROOT/src/frontend/__main__.py" ]; then
    python3 "$PROJECT_ROOT/src/frontend/__main__.py" &
elif [ -f "$PROJECT_ROOT/src/frontend/hot_window.py" ]; then
    python3 "$PROJECT_ROOT/src/frontend/hot_window.py" &
else
    echo -e "${RED}错误: 未找到GUI启动脚本${NC}"
    echo "请检查 src/frontend/ 目录"
    exit 1
fi

GUI_PID=$!
echo -e "${GREEN}✓ 热窗口已启动 (PID: $GUI_PID)${NC}"

# 保存PID
echo "$GUI_PID" > "$PROJECT_ROOT/logs/hot_window.pid"

echo ""
echo -e "${GREEN}=========================================="
echo "热窗口启动完成!"
echo -e "==========================================${NC}"
echo ""
echo "停止窗口: kill $GUI_PID"
echo "或运行: pkill -f 'python.*frontend'"

# 等待用户中断
trap "echo -e '\n${YELLOW}正在停止热窗口...${NC}'; kill $GUI_PID 2>/dev/null; exit 0" INT

echo "按 Ctrl+C 停止热窗口"
wait $GUI_PID
