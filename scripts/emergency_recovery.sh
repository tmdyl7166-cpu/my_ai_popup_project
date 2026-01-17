#!/bin/bash
#===============================================================================
# my_ai_popup_project 紧急恢复脚本
# 功能: 系统故障时的紧急恢复和修复
#===============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}=========================================="
echo "my_ai_popup_project 紧急恢复系统"
echo -e "==========================================${NC}"
echo ""

# 获取项目根目录
get_project_root() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

PROJECT_ROOT=$(get_project_root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日志函数
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

# 创建恢复目录
create_recovery_dir() {
    local recovery_dir="$PROJECT_ROOT/recovery/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$recovery_dir"
    echo "$recovery_dir"
}

# 备份当前状态
backup_current_state() {
    local recovery_dir="$1"
    log_info "备份当前状态..."

    # 备份配置文件
    mkdir -p "$recovery_dir/config"
    cp -r "$PROJECT_ROOT/rules/" "$recovery_dir/config/" 2>/dev/null || true
    cp "$PROJECT_ROOT/project_config.json" "$recovery_dir/config/" 2>/dev/null || true

    # 备份日志
    mkdir -p "$recovery_dir/logs"
    cp -r "$PROJECT_ROOT/logs/" "$recovery_dir/logs/" 2>/dev/null || true

    # 备份数据
    mkdir -p "$recovery_dir/data"
    cp -r "$PROJECT_ROOT/data/" "$recovery_dir/data/" 2>/dev/null || true

    log_success "状态备份完成: $recovery_dir"
    echo "$recovery_dir"
}

# 停止所有服务
stop_all_services() {
    log_info "停止所有服务..."

    # 停止Python进程
    pkill -f "python.*src/backend" || true
    pkill -f "python.*src/frontend" || true
    pkill -f "uvicorn.*my_ai_popup_project" || true

    # 停止Ollama
    pkill -f "ollama serve" || true

    # 停止Node.js进程 (如果有)
    pkill -f "node.*web" || true

    # 等待进程停止
    sleep 2

    log_success "所有服务已停止"
}

# 清理损坏文件
cleanup_corrupted_files() {
    log_info "清理损坏文件..."

    # 清理临时文件
    find "$PROJECT_ROOT" -name "*.tmp" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyc" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

    # 清理日志文件 (保留最近7天的)
    find "$PROJECT_ROOT/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

    # 清理数据缓存
    find "$PROJECT_ROOT/data" -name "*.cache" -type f -delete 2>/dev/null || true

    log_success "损坏文件清理完成"
}

# 修复虚拟环境
repair_virtual_env() {
    log_info "修复虚拟环境..."

    local venv_path="$PROJECT_ROOT/ai_popup_env"

    if [ ! -d "$venv_path" ]; then
        log_info "创建新的虚拟环境..."
        python3 -m venv "$venv_path"
    fi

    # 激活并修复
    source "$venv_path/bin/activate"
    pip install --upgrade pip wheel setuptools

    # 重新安装依赖
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
        log_success "依赖重新安装完成"
    else
        log_warning "requirements.txt不存在，跳过依赖安装"
    fi

    deactivate
}

# 修复配置文件
repair_config_files() {
    log_info "修复配置文件..."

    # 检查并修复project_config.json
    if [ ! -f "$PROJECT_ROOT/project_config.json" ]; then
        log_warning "创建默认project_config.json..."
        cat > "$PROJECT_ROOT/project_config.json" << 'EOF'
{
  "project_name": "my_ai_popup_project",
  "version": "1.0.0",
  "description": "AI弹窗项目",
  "author": "my_ai_popup_project Team",
  "created_at": "2025-01-21",
  "modules": {
    "frontend": true,
    "backend": true,
    "processing": true,
    "integrations": true
  },
  "paths": {
    "src": "src",
    "rules": "rules",
    "assets": "assets",
    "docs": "docs",
    "logs": "logs",
    "web": "web"
  }
}
EOF
        log_success "默认配置文件已创建"
    fi

    # 检查并修复规则文件
    for level in 1 2 3 4 5; do
        rule_file="$PROJECT_ROOT/rules/L${level}-meta-goal.json"
        if [ ! -f "$rule_file" ]; then
            log_warning "创建默认L${level}规则文件..."
            cat > "$rule_file" << EOF
{
  "level": $level,
  "name": "L${level}规则层",
  "description": "第${level}层规则配置",
  "version": "1.0.0",
  "last_updated": "$(date -Iseconds)",
  "rules": {}
}
EOF
        fi
    done

    log_success "配置文件修复完成"
}

# 修复目录结构
repair_directory_structure() {
    log_info "修复目录结构..."

    # 创建必要的目录
    mkdir -p "$PROJECT_ROOT/src/frontend"
    mkdir -p "$PROJECT_ROOT/src/backend"
    mkdir -p "$PROJECT_ROOT/src/processing"
    mkdir -p "$PROJECT_ROOT/src/integrations"
    mkdir -p "$PROJECT_ROOT/rules"
    mkdir -p "$PROJECT_ROOT/assets/images/output"
    mkdir -p "$PROJECT_ROOT/assets/videos/output"
    mkdir -p "$PROJECT_ROOT/docs"
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/web"
    mkdir -p "$PROJECT_ROOT/tests"

    # 设置权限
    chmod 755 "$PROJECT_ROOT/logs" 2>/dev/null || true
    chmod 755 "$PROJECT_ROOT/data" 2>/dev/null || true
    chmod 755 "$PROJECT_ROOT/assets" 2>/dev/null || true

    log_success "目录结构修复完成"
}

# 验证系统状态
verify_system_status() {
    log_info "验证系统状态..."

    local errors=0
    local warnings=0

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        ((errors++))
    else
        log_success "Python3可用"
    fi

    # 检查虚拟环境
    local venv_path="$PROJECT_ROOT/ai_popup_env"
    if [ ! -d "$venv_path" ]; then
        log_error "虚拟环境不存在"
        ((errors++))
    else
        if [ ! -f "$venv_path/bin/activate" ]; then
            log_error "虚拟环境激活脚本不存在"
            ((errors++))
        else
            log_success "虚拟环境正常"
        fi
    fi

    # 检查配置文件
    if [ ! -f "$PROJECT_ROOT/project_config.json" ]; then
        log_error "项目配置文件不存在"
        ((errors++))
    else
        if python3 -c "import json; json.load(open('$PROJECT_ROOT/project_config.json'))" 2>/dev/null; then
            log_success "项目配置文件格式正确"
        else
            log_error "项目配置文件格式错误"
            ((errors++))
        fi
    fi

    # 检查核心目录
    for dir in "src" "rules" "assets" "docs"; do
        if [ ! -d "$PROJECT_ROOT/$dir" ]; then
            log_error "核心目录不存在: $dir"
            ((errors++))
        else
            log_success "核心目录存在: $dir"
        fi
    done

    # 总结
    echo ""
    echo "=========================================="
    echo "验证结果:"
    echo "  ✗ 错误: $errors"
    echo "  ⚠ 警告: $warnings"

    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✓ 系统状态正常${NC}"
        return 0
    else
        echo -e "${RED}✗ 系统存在问题${NC}"
        return 1
    fi
    echo "=========================================="
}

# 生成恢复报告
generate_recovery_report() {
    local recovery_dir="$1"
    local start_time="$2"
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    local report_file="$recovery_dir/recovery_report.txt"

    cat > "$report_file" << EOF
my_ai_popup_project 紧急恢复报告
=====================================

恢复时间: $(date)
恢复目录: $recovery_dir
恢复耗时: ${duration}秒

系统状态:
$(verify_system_status 2>&1)

备份文件:
$(ls -la "$recovery_dir" 2>/dev/null || echo "无备份文件")

建议:
1. 检查恢复后的系统是否正常工作
2. 运行完整测试套件验证功能
3. 查看日志文件了解恢复过程中的问题
4. 如有问题，请查看备份文件进行手动恢复

=====================================
EOF

    log_success "恢复报告已生成: $report_file"
}

# 主程序
ACTION="full_recovery"
RECOVERY_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            ACTION="full_recovery"
            shift
            ;;
        --quick)
            ACTION="quick_recovery"
            shift
            ;;
        --verify)
            ACTION="verify_only"
            shift
            ;;
        --help|-h)
            echo "使用方法:"
            echo "  $0                    # 完整恢复 (停止服务+修复+验证)"
            echo "  $0 --full             # 完整恢复"
            echo "  $0 --quick            # 快速恢复 (仅修复)"
            echo "  $0 --verify           # 仅验证系统状态"
            echo ""
            echo "恢复流程:"
            echo "  1. 创建恢复目录和备份"
            echo "  2. 停止所有服务"
            echo "  3. 清理损坏文件"
            echo "  4. 修复虚拟环境"
            echo "  5. 修复配置文件"
            echo "  6. 修复目录结构"
            echo "  7. 验证系统状态"
            echo "  8. 生成恢复报告"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

START_TIME=$(date +%s)

case $ACTION in
    full_recovery)
        log_info "开始完整恢复流程..."
        RECOVERY_DIR=$(create_recovery_dir)
        backup_current_state "$RECOVERY_DIR"
        stop_all_services
        cleanup_corrupted_files
        repair_virtual_env
        repair_config_files
        repair_directory_structure
        if verify_system_status; then
            generate_recovery_report "$RECOVERY_DIR" "$START_TIME"
            log_success "完整恢复成功完成!"
        else
            log_error "恢复过程中发现问题，请检查日志"
            exit 1
        fi
        ;;

    quick_recovery)
        log_info "开始快速恢复流程..."
        RECOVERY_DIR=$(create_recovery_dir)
        backup_current_state "$RECOVERY_DIR"
        cleanup_corrupted_files
        repair_config_files
        repair_directory_structure
        if verify_system_status; then
            generate_recovery_report "$RECOVERY_DIR" "$START_TIME"
            log_success "快速恢复成功完成!"
        else
            log_error "恢复过程中发现问题，请检查日志"
            exit 1
        fi
        ;;

    verify_only)
        verify_system_status
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "紧急恢复系统执行完成"
echo -e "==========================================${NC}"
echo ""
if [ -n "$RECOVERY_DIR" ]; then
    echo "恢复目录: $RECOVERY_DIR"
    echo "恢复报告: $RECOVERY_DIR/recovery_report.txt"
fi
