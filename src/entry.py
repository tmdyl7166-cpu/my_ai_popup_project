"""
SRC模块统一入口脚本
负责启动整个SRC模块
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .main import main as start_main

def main():
    """主函数"""
    print("启动SRC模块...")
    
    # 启动主应用
    start_main()

if __name__ == "__main__":
    main()
