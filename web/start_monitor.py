#!/usr/bin/env python3
"""
AI弹窗项目Web监控中心启动脚本
自动检测环境、安装依赖、启动监控服务
"""

import os
import sys
import subprocess
import argparse
import socket
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 10):
        print("❌ Python版本过低，需要Python 3.10+")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖是否已安装"""
    # Web监控中心专用依赖
    web_required_modules = [
        'jinja2', 'aiofiles', 'websockets', 'socketio', 'schedule'
    ]

    # 主项目依赖（Web监控中心也需要）
    main_required_modules = [
        'fastapi', 'uvicorn', 'python-multipart', 'psutil'
    ]

    missing = []

    # 检查Web专用依赖
    for module in web_required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)

    # 检查主项目依赖
    for module in main_required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)

    return missing

def install_dependencies():
    """安装依赖"""
    print("📦 正在安装依赖...")
    requirements_file = Path(__file__).parent / 'requirements.txt'

    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False

    try:
        # 尝试使用国内源加速安装
        sources = [
            'https://pypi.tuna.tsinghua.edu.cn/simple/',
            'https://pypi.mirrors.ustc.edu.cn/simple/',
            'https://pypi.org/simple/'
        ]

        for source in sources:
            try:
                print(f"🔄 尝试从 {source} 安装依赖...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file),
                    '-i', source, '--quiet'
                ], capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    print("✅ 依赖安装成功")
                    return True
                else:
                    print(f"⚠️ 从 {source} 安装失败，尝试其他源...")
            except subprocess.TimeoutExpired:
                print(f"⏰ 从 {source} 安装超时，尝试其他源...")
                continue

        print("❌ 所有安装源都失败了")
        return False

    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def find_available_port(start_port=8080, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def check_project_structure():
    """检查项目结构"""
    project_root = Path(__file__).parent.parent
    required_files = [
        'project_config.json',
        'requirements.txt',
        'README.md',
        'src',
        'assets',
        'rules',
        'scripts'
    ]

    missing = []
    for file in required_files:
        if not (project_root / file).exists():
            missing.append(file)

    if missing:
        print(f"⚠️ 缺少项目文件: {', '.join(missing)}")
        return False

    print("✅ 项目结构检查通过")
    return True

def start_monitoring_app(host='0.0.0.0', port=8080):
    """启动监控应用"""
    print(f"🚀 启动Web监控中心: http://{host}:{port}")

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent)

        # 启动应用
        result = subprocess.run([
            sys.executable, 'web/app.py',
            '--host', host,
            '--port', str(port)
        ], env=env)

        return result.returncode == 0

    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在关闭...")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI弹窗项目Web监控中心')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, help='监听端口（自动查找可用端口）')
    parser.add_argument('--auto-install', action='store_true', help='自动安装依赖')
    parser.add_argument('--skip-checks', action='store_true', help='跳过环境检查')

    args = parser.parse_args()

    print("🎯 AI弹窗项目Web监控中心启动器")
    print("=" * 50)

    # 1. 检查Python版本
    if not args.skip_checks:
        if not check_python_version():
            return 1

    # 2. 检查项目结构
    if not args.skip_checks:
        if not check_project_structure():
            print("⚠️ 项目结构不完整，但继续启动...")

    # 3. 检查依赖
    missing_deps = check_dependencies()
    if missing_deps:
        if args.auto_install:
            print(f"📦 发现缺少依赖: {', '.join(missing_deps)}")
            if not install_dependencies():
                return 1
        else:
            print(f"❌ 缺少依赖，请运行以下命令安装:")
            print(f"pip install -r web/requirements.txt")
            print("或者使用 --auto-install 参数自动安装")
            return 1
    else:
        print("✅ 依赖检查通过")

    # 4. 查找可用端口
    if args.port:
        port = args.port
    else:
        port = find_available_port()
        if not port:
            print("❌ 无法找到可用端口")
            return 1

    print(f"🌐 使用端口: {port}")

    # 5. 显示访问信息
    print("\n" + "=" * 50)
    print("🎉 准备启动Web监控中心!")
    print(f"📱 访问地址: http://localhost:{port}")
    print("📊 功能包括:")
    print("   • 实时脚本状态监控")
    print("   • 系统资源使用情况")
    print("   • 部署进度跟踪")
    print("   • 配置管理")
    print("   • 日志查看")
    print("   • API调试")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")
    print("=" * 50 + "\n")

    # 等待用户确认
    try:
        input("按回车键启动服务...")
    except KeyboardInterrupt:
        print("\n👋 再见!")
        return 0

    # 6. 启动应用
    success = start_monitoring_app(args.host, port)

    if success:
        print("\n✅ 服务已停止")
        return 0
    else:
        print("\n❌ 服务异常退出")
        return 1

if __name__ == '__main__':
    sys.exit(main())
