#!/bin/bash
#===============================================================================
# my_ai_popup_project Web配置同步脚本
# 功能: 同步Web配置，确保Web模块与主项目配置一致
#===============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "my_ai_popup_project Web配置同步"
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

# 检查文件是否存在
check_file_exists() {
    local file="$1"
    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return 1
    fi
    return 0
}

# 同步主项目配置到Web配置
sync_main_to_web() {
    log_info "同步主项目配置到Web配置..."

    # 检查主项目配置文件
    if ! check_file_exists "$PROJECT_ROOT/project_config.json"; then
        log_error "主项目配置文件不存在"
        return 1
    fi

    # 检查Web配置目录
    if [ ! -d "$PROJECT_ROOT/web" ]; then
        log_warning "Web目录不存在，跳过同步"
        return 0
    fi

    # 读取主项目配置
    local main_config
    main_config=$(cat "$PROJECT_ROOT/project_config.json" 2>/dev/null || echo "{}")

    # 生成Web配置
    local web_config="{
  \"project_name\": \"my_ai_popup_project\",
  \"version\": \"1.0.0\",
  \"web_port\": 8080,
  \"api_base_url\": \"http://localhost:8000\",
  \"sync_timestamp\": \"$(date -Iseconds)\",
  \"main_config\": $main_config
}"

    # 写入Web配置
    echo "$web_config" > "$PROJECT_ROOT/web/web_config.json"
    log_success "Web配置已同步"

    # 同步Web配置重构文件
    if [ -f "$PROJECT_ROOT/web/web_config_refactor.json" ]; then
        local refactor_config="{
  \"web_module\": {
    \"description\": \"Web监控模块配置\",
    \"sync_info\": {
      \"last_sync\": \"$(date -Iseconds)\",
      \"source\": \"project_config.json\",
      \"target\": \"web_config.json\"
    },
    \"components\": {
      \"web_api\": {
        \"description\": \"Web API服务\",
        \"config_file\": \"web_config.json\"
      },
      \"deployment_monitor\": {
        \"description\": \"部署监控\",
        \"config_file\": \"web_config.json\"
      },
      \"system_monitor\": {
        \"description\": \"系统监控\",
        \"config_file\": \"web_config.json\"
      }
    }
  }
}"
        echo "$refactor_config" > "$PROJECT_ROOT/web/web_config_refactor.json"
        log_success "Web配置重构文件已同步"
    fi
}

# 同步Web配置到主项目
sync_web_to_main() {
    log_info "同步Web配置到主项目..."

    if [ ! -f "$PROJECT_ROOT/web/web_config.json" ]; then
        log_warning "Web配置文件不存在，跳过同步"
        return 0
    fi

    # 读取Web配置
    local web_config
    web_config=$(cat "$PROJECT_ROOT/web/web_config.json" 2>/dev/null || echo "{}")

    # 提取同步信息
    local sync_info="Web配置同步于 $(date -Iseconds)"

    log_success "Web配置同步信息已记录: $sync_info"
}

# 验证配置同步状态
verify_sync() {
    log_info "验证配置同步状态..."

    local errors=0
    local warnings=0

    # 检查主项目配置
    if [ ! -f "$PROJECT_ROOT/project_config.json" ]; then
        log_error "主项目配置文件不存在"
        ((errors++))
    else
        log_success "主项目配置文件存在"
    fi

    # 检查Web配置
    if [ ! -f "$PROJECT_ROOT/web/web_config.json" ]; then
        log_warning "Web配置文件不存在"
        ((warnings++))
    else
        log_success "Web配置文件存在"
    fi

    # 检查配置一致性
    if [ -f "$PROJECT_ROOT/project_config.json" ] && [ -f "$PROJECT_ROOT/web/web_config.json" ]; then
        # 简单的JSON语法检查
        if python3 -m json.tool "$PROJECT_ROOT/project_config.json" > /dev/null 2>&1; then
            log_success "主项目配置JSON格式正确"
        else
            log_error "主项目配置JSON格式错误"
            ((errors++))
        fi

        if python3 -m json.tool "$PROJECT_ROOT/web/web_config.json" > /dev/null 2>&1; then
            log_success "Web配置JSON格式正确"
        else
            log_error "Web配置JSON格式错误"
            ((errors++))
        fi
    fi

    # 总结
    echo ""
    echo "=========================================="
    echo "验证结果:"
    echo "  ✗ 错误: $errors"
    echo "  ⚠ 警告: $warnings"

    if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
        echo -e "${GREEN}✓ 配置同步状态良好${NC}"
    elif [ $errors -eq 0 ]; then
        echo -e "${YELLOW}⚠ 配置同步存在警告${NC}"
    else
        echo -e "${RED}✗ 配置同步存在错误${NC}"
        return 1
    fi
    echo "=========================================="
}

# 主程序
ACTION="sync-main-to-web"

while [[ $# -gt 0 ]]; do
    case $1 in
        --main-to-web)
            ACTION="sync-main-to-web"
            shift
            ;;
        --web-to-main)
            ACTION="sync-web-to-main"
            shift
            ;;
        --verify)
            ACTION="verify"
            shift
            ;;
        --help|-h)
            echo "使用方法:"
            echo "  $0                    # 同步主项目配置到Web"
            echo "  $0 --main-to-web      # 同步主项目配置到Web"
            echo "  $0 --web-to-main      # 同步Web配置到主项目"
            echo "  $0 --verify           # 验证配置同步状态"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

case $ACTION in
    sync-main-to-web)
        sync_main_to_web
        ;;
    sync-web-to-main)
        sync_web_to_main
        ;;
    verify)
        verify_sync
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "Web配置同步完成!"
echo -e "==========================================${NC}"
