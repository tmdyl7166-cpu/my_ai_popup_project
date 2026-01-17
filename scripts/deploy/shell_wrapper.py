#!/usr/bin/env python3
"""
Shell脚本包装器
提供跨平台的脚本执行入口
"""

import os
import sys
from pathlib import Path


def create_bash_wrapper():
    """创建Bash入口脚本"""
    script_content = '''#!/bin/bash
#===============================================================================
# AI弹窗项目部署入口 (Bash版本)
#===============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "AI弹窗项目部署系统"
echo "=================="
echo "项目目录: $PROJECT_ROOT"
echo ""

# 激活虚拟环境
VENV_PATH="$PROJECT_ROOT/ai_popup_env"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "虚拟环境已激活"
fi

# 执行Python部署脚本
python3 "$SCRIPT_DIR/deploy_entry.py" "$@"
'''
    
    script_path = Path(__file__).parent / "deploy.sh"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    return script_path


def create_windows_wrapper():
    """创建Windows批处理入口脚本"""
    script_content = '''@echo off
REM===============================================================================
REM AI弹窗项目部署入口 (Windows版本)
REM===============================================================================

setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%~dp0.."

echo AI弹窗项目部署系统
echo ==================
echo 项目目录: %PROJECT_ROOT%
echo.

REM 激活虚拟环境
set "VENV_PATH=%PROJECT_DIR%\ai_popup_env"
if exist "%VENV_PATH%\Scripts\activate.bat" (
    call "%VENV_PATH%\Scripts\activate.bat"
    echo 虚拟环境已激活
)

REM 执行Python部署脚本
python "%SCRIPT_DIR%deploy_entry.py" %*

endlocal
'''
    
    script_path = Path(__file__).parent / "deploy.bat"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    return script_path


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--create-wrappers':
        # 创建包装脚本
        bash_path = create_bash_wrapper()
        print(f"已创建Bash入口: {bash_path}")
        
        win_path = create_windows_wrapper()
        print(f"已创建Windows入口: {win_path}")
        
        return 0
    
    # 转发到Python部署入口
    deploy_entry = Path(__file__).parent / "deploy_entry.py"
    
    if not deploy_entry.exists():
        print(f"错误: 部署入口文件不存在: {deploy_entry}")
        return 1
    
    # 执行部署
    os.chdir(Path(__file__).parent.parent.parent)
    
    import subprocess
    result = subprocess.run([sys.executable, str(deploy_entry)] + sys.argv[1:])
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())

