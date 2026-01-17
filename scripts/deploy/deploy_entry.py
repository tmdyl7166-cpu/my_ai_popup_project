#!/usr/bin/env python3
"""
部署系统统一入口
提供命令行接口执行部署流程
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 导入部署核心模块
from deploy_core import DeployCore, DeployContext, DeployStatus
from deploy_core.base import create_module
from deploy_utils.logger import setup_global_logging, get_logger


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="AI弹窗项目自动化部署系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python deploy_entry.py --task full          # 执行完整部署
  python deploy_entry.py --task setup         # 只执行环境准备
  python deploy_entry.py --task deps          # 只执行依赖安装
  python deploy_entry.py --task health        # 只执行健康检查
  python deploy_entry.py --task verify        # 验证部署结果
        """
    )
    
    parser.add_argument(
        '--task',
        choices=['full', 'setup', 'deps', 'health', 'verify', 'rollback'],
        default='full',
        help='执行的任务类型 (默认: full)'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        help='项目根目录路径 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='deploy_result.json',
        help='输出结果文件路径'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '--skip-health',
        action='store_true',
        help='跳过健康检查'
    )
    
    return parser


def get_deploy_modules(context: DeployContext, skip_health: bool = False) -> List:
    """获取部署模块列表"""
    modules = []
    
    # 任务到模块的映射
    module_map = {
        'setup': ['setup_env'],
        'deps': ['setup_env', 'install_deps'],
        'health': ['health_check'],
        'full': ['setup_env', 'install_deps', 'health_check'],
        'verify': ['health_check']
    }
    
    task_modules = module_map.get(context.status.value, module_map['full'])
    
    for module_name in task_modules:
        if module_name == 'health_check' and skip_health:
            continue
        
        try:
            module = create_module(module_name, context)
            modules.append(module)
        except Exception as e:
            logger = get_logger("deploy_entry")
            logger.error(f"创建模块失败: {module_name} - {e}")
    
    return modules


def run_rollback(project_root: Path) -> bool:
    """执行回滚"""
    logger = get_logger("deploy_entry")
    logger.info("开始执行回滚")
    
    try:
        backup_dir = project_root / "backup" / "deploy"
        
        if not backup_dir.exists():
            logger.warning("没有找到备份目录")
            return True
        
        # 查找最新的备份
        backups = sorted(backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backups:
            logger.warning("没有找到备份文件")
            return True
        
        # 执行回滚
        from deploy_core import RollbackManager
        rollback_manager = RollbackManager(backup_dir)
        
        if rollback_manager.rollback_all():
            logger.info("回滚成功")
            return True
        else:
            logger.error("回滚失败")
            return False
            
    except Exception as e:
        logger.exception(f"回滚异常: {e}")
        return False


def run_deploy(args: argparse.Namespace) -> bool:
    """执行部署"""
    # 设置日志
    setup_global_logging()
    logger = get_logger("deploy_entry")
    
    # 确定项目根目录
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = Path(__file__).parent.parent.parent.resolve()
    
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"执行任务: {args.task}")
    
    # 创建部署上下文
    context = DeployContext(project_root)
    
    # 获取需要执行的模块
    modules = get_deploy_modules(context, args.skip_health)
    
    if not modules:
        logger.error("没有可执行的模块")
        return False
    
    # 创建部署核心
    deploy_core = DeployCore(project_root)
    
    # 执行部署
    success = deploy_core.run_all(modules)
    
    # 保存结果
    result = deploy_core.get_status()
    result["task"] = args.task
    result["success"] = success
    
    output_path = project_root / args.output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"部署结果已保存: {output_path}")
    except Exception as e:
        logger.error(f"保存结果失败: {e}")
    
    # 输出摘要
    print("\n" + "=" * 50)
    print("部署摘要")
    print("=" * 50)
    print(f"状态: {'成功' if success else '失败'}")
    print(f"任务: {args.task}")
    print(f"步骤数: {len(result.get('steps', []))}")
    
    if result.get('steps'):
        print("\n执行步骤:")
        for step in result.get('steps', []):
            status_icon = "✅" if step['status'] == 'success' else "❌" if step['status'] == 'failed' else "⏳"
            print(f"  {status_icon} {step['name']}: {step['status']}")
    
    print("=" * 50)
    
    return success


def main() -> int:
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        if args.task == 'rollback':
            # 执行回滚
            project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).parent.parent.parent.resolve()
            success = run_rollback(project_root)
        else:
            # 执行部署
            success = run_deploy(args)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        return 130
    except Exception as e:
        logger = get_logger("deploy_entry")
        logger.exception(f"部署异常: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

