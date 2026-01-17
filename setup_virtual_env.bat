@echo off
REM ================================
REM AI弹窗项目 - 虚拟环境设置脚本
REM 最后更新: 2026-04-15
REM ================================

echo ================================
echo AI弹窗项目 - 虚拟环境设置脚本
echo ================================

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python解释器
    echo 请先安装Python 3.14或更高版本
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo 检测到Python版本: %PYTHON_VERSION%

REM 创建虚拟环境
echo 正在创建虚拟环境...
python -m venv ai_popup_env

REM 激活虚拟环境
echo 正在激活虚拟环境...
call ai_popup_env\Scripts\activate.bat

echo.
echo ================================
echo 虚拟环境已创建并激活!
echo 现在可以运行 install_dependencies.bat 来安装依赖
echo ================================

pause
