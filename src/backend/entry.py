"""
后端模块统一入口脚本
负责启动后端服务
"""
import sys
import asyncio
from pathlib import Path

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .task_manager import get_task_manager
from .scheduler import get_scheduler, start_scheduler, stop_scheduler

async def main():
    """主函数"""
    print("启动后端模块...")
    
    # 初始化任务管理器
    task_manager = get_task_manager()
    print("✅ 任务管理器初始化完成")
    
    # 启动调度器
    await start_scheduler()
    print("✅ 调度器启动完成")
    
    try:
        # 保持运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止后端服务...")
        await stop_scheduler()
        print("✅ 后端服务已停止")

if __name__ == "__main__":
    asyncio.run(main())
