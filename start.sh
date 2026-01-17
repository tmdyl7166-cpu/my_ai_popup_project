#!/bin/bash
# AI弹窗项目 - 启动脚本
# 确保在任何情况下都能正确识别项目根目录

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "AI弹窗项目启动脚本"
echo "============================================"
echo "工作目录: $(pwd)"
echo "项目根目录: $SCRIPT_DIR"
echo "============================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请安装Python 3.10或更高版本"
    exit 1
fi

echo "Python版本: $(python3 --version)"

# 验证路径配置
echo ""
echo "验证路径配置..."
if python3 verify_paths.py; then
    echo "路径验证通过"
else
    echo "警告: 路径验证失败，但继续尝试启动..."
fi

# 检查并安装依赖
echo ""
echo "检查依赖..."
if [ -f "requirements.txt" ]; then
    # 检查是否需要安装依赖
    if python3 -c "import src" 2>/dev/null; then
        echo "依赖已安装"
    else
        echo "正在安装依赖..."
        python3 -m pip install -r requirements.txt -q
        if [ $? -ne 0 ]; then
            echo "错误: 依赖安装失败"
            exit 1
        fi
        echo "依赖安装完成"
    fi
else
    echo "警告: 未找到requirements.txt文件"
fi

# 启动应用
echo ""
echo "启动API服务..."
echo "访问地址: http://0.0.0.0:8000"
echo "API文档: http://0.0.0.0:8000/docs"
echo "============================================"

# 启动FastAPI应用
python3 -m src.main

