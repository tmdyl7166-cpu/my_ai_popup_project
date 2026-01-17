#!/usr/bin/env python3
"""
my_ai_popup_project 简易后端启动脚本

功能:
    - 快速启动后端服务
    - 简化的启动流程
    - 适合开发和测试使用

使用方法:
    python3 scripts/start_backend_simple.py
"""

import sys
import os
from pathlib import Path

# 获取项目根目录并添加到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 设置PYTHONPATH环境变量
os.environ['PYTHONPATH'] = str(PROJECT_ROOT)


def check_environment():
    """检查运行环境"""
    print("检查运行环境...")

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False

    print(f"Python版本: {sys.version}")

    # 检查虚拟环境
    is_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    if is_venv:
        print("虚拟环境: 已激活")
    else:
        print("警告: 未检测到虚拟环境，建议使用虚拟环境运行")

    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"Python路径: {sys.path[0]}")

    return True


def check_dependencies():
    """检查依赖"""
    print("\n检查依赖...")

    required_modules = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
    ]

    missing = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (缺失)")
            missing.append(name)

    if missing:
        print(f"\n缺失依赖: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False

    return True


def start_server(host='0.0.0.0', port=8000, reload=False):
    """启动服务器"""
    print(f"\n启动后端服务...")
    print(f"  主机: {host}")
    print(f"  端口: {port}")
    print(f"  自动重载: {'是' if reload else '否'}")
    print()

    try:
        import uvicorn
        from src.backend.control_core.server import app

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        return True

    except ImportError as e:
        print(f"导入错误: {e}")
        print("\n尝试备用启动方式...")

        # 备用：直接运行uvicorn
        try:
            cmd = [
                sys.executable, '-m', 'uvicorn',
                'src.backend.control_core.server:app',
                '--host', host,
                '--port', str(port)
            ]
            if reload:
                cmd.append('--reload')

            os.execv(sys.executable, cmd)
            return True

        except Exception as e:
            print(f"备用启动失败: {e}")
            return False

    except Exception as e:
        print(f"启动失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("my_ai_popup_project 简易后端启动")
    print("=" * 50)

    # 检查环境
    if not check_environment():
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 解析命令行参数
    host = '0.0.0.0'
    port = 8000
    reload = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--host' and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif args[i] == '--port' and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == '--reload':
            reload = True
            i += 1
        elif args[i] in ['--help', '-h']:
            print("使用方法:")
            print("  python3 scripts/start_backend_simple.py")
            print("  python3 scripts/start_backend_simple.py --host 127.0.0.1")
            print("  python3 scripts/start_backend_simple.py --port 8080")
            print("  python3 scripts/start_backend_simple.py --reload")
            sys.exit(0)
        else:
            i += 1

    # 启动服务器
    if start_server(host=host, port=port, reload=reload):
        print("\n服务已停止")
    else:
        print("\n启动失败")
        sys.exit(1)


if __name__ == '__main__':
    main()

