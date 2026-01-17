@echo off
REM ================================
REM AI弹窗项目 - 依赖安装脚本
REM 最后更新: 2026-04-15
REM ================================

echo ================================
echo AI弹窗项目 - 依赖安装脚本
echo ================================

REM 检查是否在虚拟环境中
if not defined VIRTUAL_ENV (
    echo.
    echo 注意: 建议在虚拟环境中运行此脚本
    echo 如果尚未创建虚拟环境，请运行以下命令:
    echo python -m venv ai_popup_env
    echo 然后激活虚拟环境:
    echo Windows: ai_popup_env\Scripts\activate
    echo.
    pause
)

REM 更新pip到最新版本
echo 正在更新pip到最新版本...
python -m pip install --upgrade pip

REM 安装主项目依赖
echo 正在安装主项目依赖...
pip install -r requirements.txt

REM 安装Web监控中心依赖
echo 正在安装Web监控中心依赖...
pip install -r web/requirements.txt

REM 安装Deep-Live-Cam依赖
echo 正在安装Deep-Live-Cam依赖...
pip install -r assets/Deep-Live-Cam-main/requirements.txt

REM 安装Facefusion依赖
echo 正在安装Facefusion依赖...
pip install -r assets/facefusion-master/requirements.txt

REM 安装iRoopDeepFaceCam依赖
echo 正在安装iRoopDeepFaceCam依赖...
pip install -r assets/iRoopDeepFaceCam-main/requirements.txt

echo.
echo ================================
echo 所有依赖安装完成!
echo ================================

pause
