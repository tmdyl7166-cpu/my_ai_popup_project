"""
Web模块统一入口脚本
负责启动Web监控应用
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .web_monitor import app_instance

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI弹窗项目Web监控中心')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    
    args = parser.parse_args()
    
    app_instance.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
