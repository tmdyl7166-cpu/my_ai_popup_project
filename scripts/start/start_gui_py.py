#!/usr/bin/env python3
"""
my_ai_popup_project GUI启动脚本

功能:
    - 启动PyQt5/PyQt6 GUI界面
    - 支持多种启动模式
    - 环境检查和依赖验证

使用方法:
    python3 scripts/start/start_gui_py.py
    python3 scripts/start/start_gui_py.py --debug
    python3 scripts/start/start_gui_py.py --style fusion
"""

import sys
import os
from pathlib import Path


def check_environment():
    """检查运行环境"""
    print("检查运行环境...")

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False

    print(f"Python版本: {sys.version}")

    # 检查显示
    display = os.environ.get('DISPLAY', '')
    if not display:
        print("警告: 未检测到DISPLAY环境变量")
        print("  如果在无头环境中运行，请使用 --headless 参数")

    # 检查虚拟环境
    is_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    if is_venv:
        print("虚拟环境: 已激活")
    else:
        print("警告: 未检测到虚拟环境，建议使用虚拟环境运行")

    return True


def check_dependencies():
    """检查依赖"""
    print("\n检查依赖...")

    # GUI框架
    gui_framework = None
    try:
        import PyQt6
        gui_framework = 'PyQt6'
        print(f"  ✓ PyQt6")
    except ImportError:
        try:
            import PyQt5
            gui_framework = 'PyQt5'
            print(f"  ✓ PyQt5")
        except ImportError:
            print("  ✗ PyQt5/PyQt6 (缺失)")
            print("\n请安装GUI框架:")
            print("  pip install PyQt6")
            print("  或")
            print("  pip install PyQt5")
            return False

    return gui_framework


def start_gui(framework=None, debug=False, style=None, headless=False):
    """启动GUI"""
    if headless:
        print("\n警告: 在无头模式运行，GUI将不可见")

    print(f"\n启动GUI界面...")
    print(f"  框架: {framework or 'auto-detect'}")
    print(f"  调试模式: {'是' if debug else '否'}")
    print(f"  样式: {style or '默认'}")
    print()

    try:
        # 动态导入GUI框架
        if framework == 'PyQt6' or (framework is None and 'PyQt6' in sys.modules):
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            print("使用 PyQt6")
        else:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
            print("使用 PyQt5")

        # 创建应用
        app = QApplication(sys.argv)

        # 设置应用信息
        app.setApplicationName("my_ai_popup_project")
        app.setApplicationVersion("1.0.0")

        # 设置样式
        if style:
            app.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #2d2d2d;
                }}
                QWidget {{
                    color: #ffffff;
                    background-color: #2d2d2d;
                }}
            """)

        # 设置调试模式
        if debug:
            print("\n调试模式已启用")
            os.environ['QT_DEBUG_PLUGINS'] = '1'

        # 启动GUI主窗口
        from src.frontend.main_window import MainWindow

        window = MainWindow()
        window.show()

        print("\nGUI已启动")
        print("  按 Ctrl+C 退出")
        print()

        return app.exec()

    except ImportError as e:
        print(f"导入错误: {e}")
        print("\nGUI框架未安装，请先安装:")
        print("  pip install PyQt6")
        return 1

    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """主函数"""
    print("=" * 50)
    print("my_ai_popup_project GUI启动")
    print("=" * 50)

    # 检查环境
    if not check_environment():
        sys.exit(1)

    # 检查依赖
    framework = check_dependencies()
    if not framework:
        sys.exit(1)

    # 解析命令行参数
    debug = False
    style = None
    headless = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--debug':
            debug = True
            i += 1
        elif args[i] == '--style' and i + 1 < len(args):
            style = args[i + 1]
            i += 2
        elif args[i] == '--headless':
            headless = True
            i += 1
        elif args[i] == '--framework' and i + 1 < len(args):
            framework = args[i + 1]
            i += 2
        elif args[i] in ['--help', '-h']:
            print("使用方法:")
            print("  python3 scripts/start/start_gui_py.py")
            print("  python3 scripts/start/start_gui_py.py --debug")
            print("  python3 scripts/start/start_gui_py.py --style fusion")
            print("  python3 scripts/start/start_gui_py.py --headless")
            print("  python3 scripts/start/start_gui_py.py --framework PyQt6")
            sys.exit(0)
        else:
            i += 1

    # 启动GUI
    exit_code = start_gui(framework=framework, debug=debug, style=style, headless=headless)

    print("\nGUI已退出")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

