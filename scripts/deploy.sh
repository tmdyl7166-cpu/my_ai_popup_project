#!/bin/bash
#===============================================================================
# my_ai_popup_project 完整部署脚本
# 一键部署所有服务（支持本地模式）
#
# 功能:
#   - 检查系统要求
#   - 创建/更新虚拟环境
#   - 安装Python依赖
#   - 初始化目录结构
#   - 启动后端服务
#   - 启动健康检测服务
#
# 环境变量:
#   MY_AI_POPUP_PROJECT_ROOT - 项目根目录
#
# 使用方式:
#   ./deploy.sh              # 交互式部署
#   ./deploy.sh --local      # 本地模式（默认）
#===============================================================================

set -euo pipefail

#-------------------------------------------------------------------------------
# 颜色定义
#-------------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "my_ai_popup_project 完整部署脚本"
echo "==========================================${NC}"
echo ""

#-------------------------------------------------------------------------------
# 路径检测函数
#-------------------------------------------------------------------------------

get_project_root() {
    # 优先级: MY_AI_POPUP_PROJECT_ROOT > 脚本目录的父目录
    
    if [ -n "${MY_AI_POPUP_PROJECT_ROOT:-}" ] && [ -d "$MY_AI_POPUP_PROJECT_ROOT" ]; then
        echo "$MY_AI_POPUP_PROJECT_ROOT"
        return 0
    fi
    
    # 获取脚本所在目录
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 脚本目录的父目录即为项目根目录
    echo "$(dirname "$script_dir")"
}

#-------------------------------------------------------------------------------
# 日志函数
#-------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

#-------------------------------------------------------------------------------
# 主程序
#-------------------------------------------------------------------------------

PROJECT_ROOT=$(get_project_root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info "项目根目录: $PROJECT_ROOT"
log_info "脚本目录: $SCRIPT_DIR"

# 确保在项目根目录执行
cd "$PROJECT_ROOT"

# 解析命令行参数
MODE="local"
while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            MODE="local"
            shift
            ;;
        --help|-h)
            echo "使用方法:"
            echo "  $0              # 交互式部署"
            echo "  $0 --local      # 本地模式（默认）"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

echo ""
log_info "部署模式: $MODE"
echo ""

# ==========================================
# 步骤1: 检查系统要求
# ==========================================
echo -e "${YELLOW}[1/6] 检查系统要求...${NC}"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装"
    exit 1
fi

python3 --version
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)

if [ "$PYTHON_VERSION" -lt 3 ] || ([ "$PYTHON_VERSION" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    log_error "Python版本需要>=3.10，推荐3.12"
    exit 1
fi
log_success "Python版本检查通过"

# 检查必要的系统依赖
if ! command -v git &> /dev/null; then
    log_warning "Git 未安装，部分功能可能受限"
fi

echo ""

# ==========================================
# 步骤2: 创建/更新虚拟环境
# ==========================================
echo -e "${YELLOW}[2/6] 创建Python虚拟环境...${NC}"

VENV_PATH="$PROJECT_ROOT/ai_popup_env"

if [ ! -d "$VENV_PATH" ]; then
    log_info "创建新虚拟环境..."
    python3 -m venv "$VENV_PATH"
    log_success "虚拟环境创建成功"
else
    log_info "虚拟环境已存在，检查是否需要更新..."
    VENV_PYTHON="$VENV_PATH/bin/python"
    if [ -f "$VENV_PYTHON" ]; then
        VENV_VERSION=$($VENV_PYTHON --version 2>/dev/null | awk '{print $2}')
        log_info "当前虚拟环境Python版本: $VENV_VERSION"
    fi
fi

# 激活虚拟环境
source "$VENV_PATH/bin/activate"
log_success "虚拟环境已激活"

# ==========================================
# 步骤3: 升级pip并安装依赖
# ==========================================
echo ""
echo -e "${YELLOW}[3/6] 安装Python依赖...${NC}"

# 升级pip
log_info "升级pip..."
pip install --upgrade pip wheel setuptools

# 检查requirements.txt是否存在
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    log_error "requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖
log_info "安装项目依赖..."
pip install -r "$PROJECT_ROOT/requirements.txt"

log_success "依赖安装完成"

# ==========================================
# 步骤4: 目录初始化
# ==========================================
echo ""
echo -e "${YELLOW}[4/6] 初始化目录结构...${NC}"

# 确保必要目录存在
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/assets/images/output"
mkdir -p "$PROJECT_ROOT/assets/videos/output"

# 设置目录权限
chmod 755 "$PROJECT_ROOT/logs" 2>/dev/null || true
chmod 755 "$PROJECT_ROOT/data" 2>/dev/null || true
chmod 755 "$PROJECT_ROOT/assets" 2>/dev/null || true

log_success "目录初始化完成"

# ==========================================
# 步骤5: 配置检查
# ==========================================
echo ""
echo -e "${YELLOW}[5/6] 配置检查...${NC}"

# 检查项目配置文件
if [ -f "$PROJECT_ROOT/project_config.json" ]; then
    log_success "项目配置文件存在"
else
    log_warning "项目配置文件不存在，将使用默认配置"
fi

# 检查规则配置
if [ -d "$PROJECT_ROOT/rules" ]; then
    log_success "规则配置目录存在"
else
    log_warning "规则配置目录不存在"
fi

# 检查src目录
if [ -d "$PROJECT_ROOT/src" ]; then
    log_success "源码目录存在"
else
    log_error "源码目录不存在"
    exit 1
fi

log_success "配置检查完成"

# ==========================================
# 步骤6: 启动服务
# ==========================================
echo ""
echo -e "${YELLOW}[6/6] 启动服务...${NC}"

LOG_DIR="$PROJECT_ROOT/logs"

# 启动后端服务
log_info "启动后端API服务..."

# 检查是否有uvicorn
if python3 -c "import uvicorn" 2>/dev/null; then
    nohup python3 -m uvicorn src.backend.api:app --host 0.0.0.0 --port 8000 \
        > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    log_success "Backend API已启动 (PID: $BACKEND_PID)"
else
    log_warning "uvicorn未安装，跳过API服务启动"
    BACKEND_PID=""
fi

# 启动健康检测服务
log_info "启动健康检测服务..."

if [ -f "$SCRIPT_DIR/health_check.py" ]; then
    nohup python3 "$SCRIPT_DIR/health_check.py" \
        > "$LOG_DIR/health_check.log" 2>&1 &
    HEALTH_PID=$!
    log_success "健康检测服务已启动 (PID: $HEALTH_PID)"
else
    log_warning "健康检测脚本不存在，跳过启动"
    HEALTH_PID=""
fi

# 保存PID到文件
if [ -n "$BACKEND_PID" ] || [ -n "$HEALTH_PID" ]; then
    echo "$BACKEND_PID $HEALTH_PID" > "$LOG_DIR/my_ai_popup_project_pids.txt" 2>/dev/null || true
fi

# 等待服务启动
log_info "等待服务启动..."
sleep 3

# 检查服务状态
if [ -n "$BACKEND_PID" ]; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend API健康检查通过"
    else
        log_warning "Backend API可能还在启动中，请稍后检查"
    fi
fi

# ==========================================
# 完成
# ==========================================
echo ""
echo -e "${GREEN}=========================================="
echo "my_ai_popup_project 部署完成!"
echo -e "==========================================${NC}"
echo ""
echo "服务状态:"
echo "  - Backend API: http://localhost:8000"
echo "  - API文档:     http://localhost:8000/docs"
if [ -f "$LOG_DIR/backend.log" ]; then
    echo "  - 后端日志:    tail -f $LOG_DIR/backend.log"
fi
echo ""
echo "常用命令:"
echo "  查看日志:     tail -f $LOG_DIR/backend.log"
if [ -f "$LOG_DIR/my_ai_popup_project_pids.txt" ]; then
    echo "  停止服务:     kill \$(cat $LOG_DIR/my_ai_popup_project_pids.txt)"
fi
echo "  重启服务:     bash $SCRIPT_DIR/start_server.sh"
echo ""
echo "后续步骤:"
echo "  1. 访问 http://localhost:8000/docs 查看API文档"
echo "  2. 启动GUI: bash $SCRIPT_DIR/start_gui.sh"
echo "  3. 查看健康状态: python3 $SCRIPT_DIR/health_check.py"
echo ""

# 禁用虚拟环境
deactivate 2>/dev/null || true
