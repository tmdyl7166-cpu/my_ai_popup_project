"""
脚本系统统一入口
负责调度和执行所有自动化脚本
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.core.script_registry import ScriptRegistry
from scripts.health.health_monitor_orchestrator import HealthMonitorOrchestrator
from scripts.utils.logging_utils import get_script_logger, setup_global_logging
from scripts.utils.file_utils import read_json, write_json

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI弹窗项目脚本系统')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--task', choices=[
        'health-check', 'config-management', 'docs-management', 'ui-monitoring'
    ], default='health-check', help='要执行的任务')
    parser.add_argument('--module', help='指定执行的模块')
    parser.add_argument('--method', default='run', help='指定执行的方法')
    parser.add_argument('--output-format', choices=['json', 'html'], default='json', help='输出格式')
    parser.add_argument('--output-file', help='输出文件路径')
    parser.add_argument('--list-modules', action='store_true', help='列出所有可用模块')
    parser.add_argument('--module-info', help='显示模块信息')
    parser.add_argument('--quiet', action='store_true', help='静默模式')

    args = parser.parse_args()

    # 设置全局日志
    if not args.quiet:
        setup_global_logging()

    logger = get_script_logger("entry")
    project_root = Path(args.project_root or PROJECT_ROOT)

    # 初始化脚本注册器
    registry = ScriptRegistry(project_root / 'scripts')
    registry.discover_scripts()

    # 处理命令
    if args.list_modules:
        modules = registry.list_available_modules()
        print("可用模块:")
        for module in modules:
            print(f"  - {module}")
        return 0

    if args.module_info:
        info = registry.get_module_info(args.module_info)
        if info:
            print(f"模块信息: {args.module_info}")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"模块不存在: {args.module_info}")
        return 0

    if args.module:
        # 执行指定模块
        result = execute_module(registry, args.module, args.method, project_root)
        if result:
            print(f"模块执行结果: {result}")
        return 0

    # 执行任务
    if args.task == 'health-check':
        result = run_health_check(project_root, args.output_format, args.output_file)
    elif args.task == 'config-management':
        result = run_config_management(registry, project_root)
    elif args.task == 'docs-management':
        result = run_docs_management(project_root)
    elif args.task == 'ui-monitoring':
        result = run_ui_monitoring(project_root)
    else:
        print(f"未知任务: {args.task}")
        return 1

    # 输出结果
    if not args.quiet:
        print(f"\n任务执行完成")
        if 'summary' in result:
            summary = result['summary']
            if 'success_rate' in summary:
                print(f"成功率: {summary['success_rate']:.1f}%")

    return 0

def execute_module(registry: ScriptRegistry, module_name: str, method_name: str, project_root: Path) -> Any:
    """执行指定模块"""
    # 这里可以实现模块动态加载和执行逻辑
    # 暂时返回模拟结果
    return {"status": "executed", "module": module_name, "method": method_name}

def run_health_check(project_root: Path, output_format: str, output_file: Optional[str]) -> Dict[str, Any]:
    """运行健康检查"""
    monitor = HealthMonitorOrchestrator(project_root)
    results = monitor.run_full_check()

    # 保存报告
    report_path = save_report(results, output_format, output_file, project_root)

    print(f"健康检查报告已保存到: {report_path}")
    return results

def run_config_management(registry: ScriptRegistry, project_root: Path) -> Dict[str, Any]:
    """运行配置管理"""
    # 这里可以实现配置管理逻辑
    return {"status": "completed", "task": "config-management"}

def run_docs_management(project_root: Path) -> Dict[str, Any]:
    """运行文档管理"""
    # 这里可以实现文档管理逻辑
    return {"status": "completed", "task": "docs-management"}

def run_ui_monitoring(project_root: Path) -> Dict[str, Any]:
    """运行UI监控"""
    # 这里可以实现UI监控逻辑
    return {"status": "completed", "task": "ui-monitoring"}

def save_report(results: Dict[str, Any], output_format: str, output_file: Optional[str], project_root: Path) -> str:
    """保存报告"""
    if output_file:
        report_path = project_root / output_file
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'json' if output_format == 'json' else 'md'
        report_path = project_root / 'logs' / f'health_report_{timestamp}.{ext}'

    report_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == 'json':
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    else:
        # 生成Markdown报告
        content = generate_markdown_report(results)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return str(report_path)

def generate_markdown_report(results: Dict[str, Any]) -> str:
    """生成Markdown报告"""
    lines = ["# 健康检查报告", ""]
    lines.append(f"生成时间: {results['timestamp']}")
    lines.append("")

    if 'summary' in results:
        summary = results['summary']
        lines.extend([
            "## 检查摘要",
            f"- 总检查数: {summary['total_checks']}",
            f"- 通过: {summary['passed_checks']}",
            f"- 失败: {summary['failed_checks']}",
            f"- 警告: {summary['warning_checks']}",
            f"- 健康评分: {summary['health_score']:.1f}%",
            ""
        ])

    if results.get('issues'):
        lines.extend(["## 发现的问题", ""])
        for issue in results['issues']:
            lines.append(f"- {issue}")
        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    sys.exit(main())
