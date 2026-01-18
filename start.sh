#!/bin/bash
# AI弹窗项目 - 启动脚本
# 确保在任何情况下都能正确识别项目根目录
# 支持 Linux 和 Windows (WSL) 环境

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "AI弹窗项目启动脚本"
echo "============================================"
echo "工作目录: $(pwd)"
echo "项目根目录: $SCRIPT_DIR"
echo "============================================"

# 检测并选择正确的Python解释器
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON_CMD=""

# 优先使用虚拟环境 - 增强检测逻辑
detect_venv_python() {
    local venv_path="$1"
    
    # 检查虚拟环境是否存在且有效
    if [ ! -d "$venv_path" ]; then
        return 1
    fi
    
    # 检查必要的目录结构
    if [ ! -d "$venv_path/lib" ]; then
        return 1
    fi
    
    # 查找 Python 解释器
    if [ -f "$venv_path/bin/python3" ]; then
        PYTHON_CMD="$venv_path/bin/python3"
        return 0
    fi
    
    if [ -f "$venv_path/bin/python" ]; then
        PYTHON_CMD="$venv_path/bin/python"
        return 0
    fi
    
    # 尝试查找版本目录下的 python
    local python_versions=$(ls -d "$venv_path/lib/python"* 2>/dev/null | head -1)
    if [ -n "$python_versions" ] && [ -f "$python_versions/bin/python3" ]; then
        PYTHON_CMD="$python_versions/bin/python3"
        return 0
    fi
    
    return 2
}

# 尝试使用虚拟环境
if detect_venv_python "$VENV_PATH"; then
    echo "✓ 使用虚拟环境 Python: $PYTHON_CMD"
else
    # 虚拟环境无效，尝试修复
    echo "⚠ 虚拟环境无效或损坏，尝试重新创建..."
    
    # 备份现有虚拟环境（如果存在）
    if [ -d "$VENV_PATH" ]; then
        mv "$VENV_PATH" "${VENV_PATH}_backup_$(date +%s)"
    fi
    
    # 创建新的虚拟环境
    if command -v python3 &> /dev/null; then
        echo "正在创建新的虚拟环境..."
        python3 -m venv "$VENV_PATH"
        
        if detect_venv_python "$VENV_PATH"; then
            echo "✓ 虚拟环境已重新创建"
            echo "正在升级 pip..."
            "$PYTHON_CMD" -m pip install --upgrade pip -q
        else
            echo "❌ 虚拟环境创建失败"
        fi
    else
        echo "错误: 未找到 python3，无法创建虚拟环境"
    fi
fi

# 如果虚拟环境仍然不可用，使用系统 Python
if [ -z "$PYTHON_CMD" ] || [ ! -f "$PYTHON_CMD" ]; then
    echo "⚠ 使用系统 Python 作为后备"
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "使用系统 Python: $PYTHON_CMD"
    else
        echo "错误: 未找到 python3，请安装 Python 3.10 或更高版本"
        exit 1
    fi
fi

echo "Python版本: $($PYTHON_CMD --version)"

# 验证路径配置
echo ""
echo "验证路径配置..."
if $PYTHON_CMD scripts/verify_paths.py; then
    echo "路径验证通过"
else
    echo "警告: 路径验证失败，但继续尝试启动..."
fi

# 检查并安装依赖
echo ""
echo "检查依赖..."
if [ -f "requirements.txt" ]; then
    # 检查是否需要安装依赖
    if $PYTHON_CMD -c "import src" 2>/dev/null; then
        echo "依赖已安装"
    else
        echo "正在安装依赖..."
        $PYTHON_CMD -m pip install -r requirements.txt -q
        if [ $? -ne 0 ]; then
            echo "错误: 依赖安装失败"
            echo "请手动运行: $PYTHON_CMD -m pip install -r requirements.txt"
            exit 1
        fi
        echo "依赖安装完成"
    fi
else
    echo "警告: 未找到requirements.txt文件"
fi

# 启动应用选项
echo ""
echo "============================================"
echo "请选择启动模式:"
echo "1. 启动 Web 监控中心 (推荐)"
echo "2. 启动 API 服务"
echo "3. 运行健康检查"
echo "4. 验证配置"
echo "============================================"
echo -n "请输入选项 [1-4]: "
read choice

case $choice in
    1)
        echo ""
        echo "启动 Web 监控中心..."
        echo "访问地址: http://0.0.0.0:8080"
        echo "============================================"
        $PYTHON_CMD web/app.py --host 0.0.0.0 --port 8080
        ;;
    2)
        echo ""
        echo "启动 API 服务..."
        echo "访问地址: http://0.0.0.0:8000"
        echo "============================================"
        $PYTHON_CMD -m src.backend.api_server
        ;;
    3)
        echo ""
        echo "运行健康检查..."
        $PYTHON_CMD scripts/entry.py --task health-check
        ;;
    4)
        echo ""
        echo "验证配置..."
        $PYTHON_CMD scripts/validate_configs.py
        ;;
    *)
        echo ""
        echo "无效选项，默认启动 Web 监控中心..."
        $PYTHON_CMD web/app.py --host 0.0.0.0 --port 8080
        ;;
esac

