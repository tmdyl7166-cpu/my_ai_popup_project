#!/bin/bash
#===============================================================================
# my_ai_popup_project OpenCV依赖修复脚本
# 功能: 修复OpenCV相关的依赖问题
#===============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "my_ai_popup_project OpenCV依赖修复"
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

# 检查系统信息
check_system_info() {
    log_info "检查系统信息..."

    echo "操作系统: $(uname -s)"
    echo "架构: $(uname -m)"

    if command -v lsb_release &> /dev/null; then
        echo "发行版: $(lsb_release -d | cut -f2)"
    elif [ -f /etc/os-release ]; then
        echo "发行版: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
    fi

    if command -v python3 &> /dev/null; then
        echo "Python版本: $(python3 --version)"
    else
        log_error "Python3未安装"
        exit 1
    fi
}

# 检查当前OpenCV状态
check_opencv_status() {
    log_info "检查当前OpenCV状态..."

    # 检查虚拟环境
    local venv_path="$PROJECT_ROOT/ai_popup_env"
    if [ ! -d "$venv_path" ]; then
        log_error "虚拟环境不存在，请先运行 setup_env.sh"
        exit 1
    fi

    # 激活虚拟环境
    source "$venv_path/bin/activate"

    # 检查OpenCV安装
    if python3 -c "import cv2; print('OpenCV版本:', cv2.__version__)" 2>/dev/null; then
        log_success "OpenCV已安装"
        python3 -c "import cv2; print('OpenCV版本:', cv2.__version__)"
    else
        log_warning "OpenCV未安装或无法导入"
    fi

    # 检查相关依赖
    local deps=("numpy" "pillow" "matplotlib")
    for dep in "${deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            echo "✓ $dep 已安装"
        else
            echo "✗ $dep 未安装"
        fi
    done

    # 检查CUDA支持
    if python3 -c "import cv2; print('CUDA支持:', cv2.cuda.getCudaEnabledDeviceCount() > 0)" 2>/dev/null; then
        log_success "OpenCV CUDA支持已启用"
    else
        log_warning "OpenCV CUDA支持未启用"
    fi

    deactivate
}

# 修复OpenCV依赖
fix_opencv_deps() {
    log_info "修复OpenCV依赖..."

    local venv_path="$PROJECT_ROOT/ai_popup_env"

    if [ ! -d "$venv_path" ]; then
        log_error "虚拟环境不存在"
        exit 1
    fi

    # 激活虚拟环境
    source "$venv_path/bin/activate"

    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip wheel setuptools

    # 卸载可能有问题的包
    log_info "清理可能有问题的包..."
    pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless 2>/dev/null || true

    # 安装基础依赖
    log_info "安装基础依赖..."
    pip install numpy pillow matplotlib

    # 检查CUDA可用性
    local use_cuda=false
    if command -v nvidia-smi &> /dev/null && nvidia-smi &>/dev/null; then
        log_info "检测到NVIDIA GPU，尝试安装CUDA版本的OpenCV..."
        use_cuda=true
    else
        log_info "未检测到NVIDIA GPU，使用CPU版本的OpenCV..."
    fi

    # 安装OpenCV
    if [ "$use_cuda" = true ]; then
        log_info "安装OpenCV CUDA版本..."
        pip install opencv-contrib-python --index-url https://pypi.org/simple/

        # 验证CUDA支持
        if python3 -c "import cv2; print('CUDA设备数量:', cv2.cuda.getCudaEnabledDeviceCount())" 2>/dev/null; then
            log_success "OpenCV CUDA版本安装成功"
        else
            log_warning "OpenCV CUDA支持未启用，降级到CPU版本..."
            pip uninstall -y opencv-contrib-python
            pip install opencv-contrib-python
        fi
    else
        log_info "安装OpenCV CPU版本..."
        pip install opencv-contrib-python
    fi

    # 验证安装
    if python3 -c "import cv2; print('OpenCV版本:', cv2.__version__)" 2>/dev/null; then
        log_success "OpenCV安装成功"
        python3 -c "import cv2; print('OpenCV版本:', cv2.__version__)"
    else
        log_error "OpenCV安装失败"
        deactivate
        exit 1
    fi

    # 安装额外的图像处理库
    log_info "安装额外的图像处理库..."
    pip install scikit-image imutils dlib

    # 验证所有依赖
    local all_good=true
    local test_imports=("cv2" "numpy" "PIL" "matplotlib" "skimage" "imutils")

    for module in "${test_imports[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            echo "✓ $module 导入成功"
        else
            echo "✗ $module 导入失败"
            all_good=false
        fi
    done

    if [ "$all_good" = true ]; then
        log_success "所有依赖安装成功"
    else
        log_warning "部分依赖安装失败，请检查错误信息"
    fi

    deactivate
}

# 优化OpenCV性能
optimize_opencv_performance() {
    log_info "优化OpenCV性能..."

    local venv_path="$PROJECT_ROOT/ai_popup_env"
    source "$venv_path/bin/activate"

    # 设置OpenCV优化
    cat > "$PROJECT_ROOT/opencv_optimization.py" << 'EOF'
#!/usr/bin/env python3
"""
OpenCV性能优化配置
"""

import cv2
import numpy as np

def optimize_opencv():
    """优化OpenCV设置"""
    # 启用OpenCV优化
    cv2.setUseOptimized(True)
    
    # 检查优化状态
    print(f"OpenCV优化已启用: {cv2.useOptimized()}")
    
    # 设置线程数
    import os
    cpu_count = os.cpu_count() or 4
    cv2.setNumThreads(cpu_count)
    print(f"OpenCV线程数设置为: {cv2.getNumThreads()}")
    
    # 检查CUDA支持
    try:
        cuda_count = cv2.cuda.getCudaEnabledDeviceCount()
        print(f"CUDA设备数量: {cuda_count}")
        if cuda_count > 0:
            print("CUDA支持已启用")
        else:
            print("CUDA支持未启用")
    except:
        print("CUDA检查失败")

if __name__ == "__main__":
    optimize_opencv()
EOF

    python3 "$PROJECT_ROOT/opencv_optimization.py"

    # 清理临时文件
    rm -f "$PROJECT_ROOT/opencv_optimization.py"

    deactivate
    log_success "OpenCV性能优化完成"
}

# 测试OpenCV功能
test_opencv_functionality() {
    log_info "测试OpenCV功能..."

    local venv_path="$PROJECT_ROOT/ai_popup_env"
    source "$venv_path/bin/activate"

    # 创建测试脚本
    cat > "$PROJECT_ROOT/test_opencv.py" << 'EOF'
#!/usr/bin/env python3
"""
OpenCV功能测试
"""

import cv2
import numpy as np
import sys

def test_basic_functionality():
    """测试基本功能"""
    try:
        # 创建测试图像
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :, 0] = 255  # 蓝色
        
        # 基本图像操作
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 人脸检测测试 (如果有级联分类器)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            print(f"人脸检测测试通过，检测到 {len(faces)} 个人脸")
        else:
            print("人脸检测测试跳过 (无级联分类器)")
        
        print("✓ 基本图像处理功能正常")
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def test_advanced_functionality():
    """测试高级功能"""
    try:
        # SIFT特征检测
        sift = cv2.SIFT_create()
        img = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        keypoints, descriptors = sift.detectAndCompute(img, None)
        print(f"✓ SIFT特征检测正常，检测到 {len(keypoints)} 个关键点")
        
        return True
        
    except Exception as e:
        print(f"⚠ 高级功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始OpenCV功能测试...")
    
    basic_ok = test_basic_functionality()
    advanced_ok = test_advanced_functionality()
    
    if basic_ok:
        print("\n✓ OpenCV基本功能测试通过")
        sys.exit(0)
    else:
        print("\n✗ OpenCV功能测试失败")
        sys.exit(1)
EOF

    if python3 "$PROJECT_ROOT/test_opencv.py"; then
        log_success "OpenCV功能测试通过"
    else
        log_warning "OpenCV功能测试失败，请检查依赖"
    fi

    # 清理测试文件
    rm -f "$PROJECT_ROOT/test_opencv.py"

    deactivate
}

# 生成修复报告
generate_fix_report() {
    local start_time="$1"
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    local report_file="$PROJECT_ROOT/logs/opencv_fix_report_$(date +%Y%m%d_%H%M%S).txt"

    cat > "$report_file" << EOF
my_ai_popup_project OpenCV依赖修复报告
=======================================

修复时间: $(date)
修复耗时: ${duration}秒

系统信息:
$(check_system_info 2>&1)

修复前状态:
$(check_opencv_status 2>&1)

修复结果:
$(test_opencv_functionality 2>&1)

建议:
1. 如果仍有问题，请检查系统是否支持CUDA
2. 考虑使用Docker环境运行项目
3. 查看OpenCV官方文档获取更多帮助

=======================================
EOF

    log_success "修复报告已生成: $report_file"
}

# 主程序
ACTION="full_fix"

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            ACTION="full_fix"
            shift
            ;;
        --check)
            ACTION="check_only"
            shift
            ;;
        --test)
            ACTION="test_only"
            shift
            ;;
        --help|-h)
            echo "使用方法:"
            echo "  $0              # 完整修复 (检查+修复+测试)"
            echo "  $0 --full       # 完整修复"
            echo "  $0 --check      # 仅检查状态"
            echo "  $0 --test       # 仅测试功能"
            echo ""
            echo "修复流程:"
            echo "  1. 检查系统信息"
            echo "  2. 检查当前OpenCV状态"
            echo "  3. 修复OpenCV依赖"
            echo "  4. 优化性能设置"
            echo "  5. 测试功能完整性"
            echo "  6. 生成修复报告"
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
    full_fix)
        log_info "开始完整OpenCV修复流程..."
        check_system_info
        check_opencv_status
        fix_opencv_deps
        optimize_opencv_performance
        test_opencv_functionality
        generate_fix_report "$START_TIME"
        log_success "OpenCV依赖修复完成!"
        ;;

    check_only)
        check_system_info
        check_opencv_status
        ;;

    test_only)
        test_opencv_functionality
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "OpenCV依赖修复执行完成"
echo -e "==========================================${NC}"
