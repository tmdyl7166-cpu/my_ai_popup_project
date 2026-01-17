#!/usr/bin/env python3
"""
脚本系统主控制器
统一管理所有自动化脚本的执行和调度
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import importlib
import inspect

# 导入工具模块
from utils.logging_utils import get_script_logger, setup_global_logging
from utils.file_utils import read_json, write_json

class ScriptModule:
    """脚本模块包装器"""

    def __init__(self, name: str, module_path: str, class_name: str):
        self.name = name
        self.module_path = module_path
        self.class_name = class_name
        self.instance = None
        self.logger = get_script_logger(name)

    def load(self):
        """加载模块"""
        try:
            module = importlib.import_module(self.module_path)
            cls = getattr(module, self.class_name)
            self.instance = cls()
            self.logger.info(f"模块加载成功: {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"模块加载失败: {self.name}", {"error": str(e)})
            return False

    def execute(self, method_name: str, *args, **kwargs) -> Any:
        """执行模块方法"""
        if not self.instance:
            if not self.load():
                return None

        try:
            method = getattr(self.instance, method_name)
            self.logger.info(f"执行方法: {self.name}.{method_name}")
            result = method(*args, **kwargs)
            self.logger.info(f"方法执行成功: {self.name}.{method_name}")
            return result
        except Exception as e:
            self.logger.error(f"方法执行失败: {self.name}.{method_name}", {"error": str(e)})
            return None

class ScriptController:
    """脚本控制器"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.logger = get_script_logger("main_controller")

        # 注册所有脚本模块
        self.modules = self._register_modules()

        # 加载配置
        self.config = self._load_config()

    def _register_modules(self) -> Dict[str, ScriptModule]:
        """注册所有脚本模块"""
        modules = {}

        # 配置管理模块
        modules['config_loader'] = ScriptModule(
            'config_loader', 'config.config_loader', 'ConfigLoader'
        )
        modules['config_validator'] = ScriptModule(
            'config_validator', 'config.config_validator', 'ConfigValidator'
        )

        # 健康检查模块
        modules['system_integrity'] = ScriptModule(
            'system_integrity', 'health.system_integrity', 'SystemIntegrityChecker'
        )
        modules['dependency_check'] = ScriptModule(
            'dependency_check', 'health.dependency_check', 'DependencyChecker'
        )
        modules['performance_monitor'] = ScriptModule(
            'performance_monitor', 'health.performance_monitor', 'PerformanceMonitor'
        )

        # 文档管理模块
        modules['docs_sync'] = ScriptModule(
            'docs_sync', 'docs.sync_monitor', 'DocsSyncMonitor'
        )
        modules['freshness_check'] = ScriptModule(
            'freshness_check', 'docs.freshness_check', 'FreshnessChecker'
        )

        # UI监控模块
        modules['ui_event_monitor'] = ScriptModule(
            'ui_event_monitor', 'ui.event_monitor', 'UIEventMonitor'
        )
        modules['ui_performance'] = ScriptModule(
            'ui_performance', 'ui.performance_check', 'UIPerformanceChecker'
        )

        # 报告生成模块
        modules['html_reporter'] = ScriptModule(
            'html_reporter', 'reports.html_reporter', 'HTMLReporter'
        )
        modules['json_reporter'] = ScriptModule(
            'json_reporter', 'reports.json_reporter', 'JSONReporter'
        )

        return modules

    def _load_config(self) -> Dict[str, Any]:
        """加载控制器配置"""
        config_path = self.project_root / 'scripts' / 'scripts_config.json'
        try:
            return read_json(config_path)
        except Exception as e:
            self.logger.warning(f"无法加载配置，使用默认配置: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "executionRules": {
                "permissions": {
                    "execution": {"user": "system", "group": "automation"}
                },
                "errorHandling": {
                    "retryPolicy": {"maxRetries": 3, "backoff": "exponential"}
                }
            },
            "monitoring": {
                "metrics": {
                    "executionTime": {"enabled": True, "threshold": 300}
                }
            }
        }

    def execute_module(self, module_name: str, method_name: str = 'run', *args, **kwargs) -> Any:
        """执行指定模块的方法"""
        if module_name not in self.modules:
            self.logger.error(f"未知模块: {module_name}")
            return None

        module = self.modules[module_name]
        return module.execute(method_name, *args, **kwargs)

    def run_health_check(self) -> Dict[str, Any]:
        """运行完整健康检查"""
        self.logger.info("开始运行完整健康检查")

        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {}
        }

        # 系统完整性检查
        results['checks']['system_integrity'] = self.execute_module('system_integrity', 'check_integrity')

        # 配置验证
        results['checks']['config_validation'] = self.execute_module('config_validator', 'validate_all')

        # 依赖检查
        results['checks']['dependencies'] = self.execute_module('dependency_check', 'check_dependencies')

        # 文档同步检查
        results['checks']['docs_sync'] = self.execute_module('docs_sync', 'check_sync')

        # 性能监控
        results['checks']['performance'] = self.execute_module('performance_monitor', 'monitor_performance')

        # 生成摘要
        results['summary'] = self._generate_summary(results)

        self.logger.info("健康检查完成")
        return results

    def run_config_management(self) -> Dict[str, Any]:
        """运行配置管理任务"""
        self.logger.info("开始运行配置管理")

        results = {
            'timestamp': datetime.now().isoformat(),
            'tasks': {}
        }

        # 加载配置
        results['tasks']['config_loading'] = self.execute_module('config_loader', 'load_all_configs')

        # 验证配置
        results['tasks']['config_validation'] = self.execute_module('config_validator', 'validate_all')

        return results

    def run_docs_management(self) -> Dict[str, Any]:
        """运行文档管理任务"""
        self.logger.info("开始运行文档管理")

        results = {
            'timestamp': datetime.now().isoformat(),
            'tasks': {}
        }

        # 文档同步检查
        results['tasks']['sync_check'] = self.execute_module('docs_sync', 'check_sync')

        # 新鲜度检查
        results['tasks']['freshness_check'] = self.execute_module('freshness_check', 'check_freshness')

        return results

    def run_ui_monitoring(self) -> Dict[str, Any]:
        """运行UI监控任务"""
        self.logger.info("开始运行UI监控")

        results = {
            'timestamp': datetime.now().isoformat(),
            'monitoring': {}
        }

        # 事件监控
        results['monitoring']['events'] = self.execute_module('ui_event_monitor', 'monitor_events')

        # 性能检查
        results['monitoring']['performance'] = self.execute_module('ui_performance', 'check_performance')

        return results

    def generate_report(self, data: Dict[str, Any], format: str = 'json') -> str:
        """生成报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'json':
            reporter = self.modules.get('json_reporter')
            if reporter:
                return reporter.execute('generate', data, f"report_{timestamp}.json")
        elif format == 'html':
            reporter = self.modules.get('html_reporter')
            if reporter:
                return reporter.execute('generate', data, f"report_{timestamp}.html")

        # 默认JSON格式
        report_path = self.project_root / 'reports' / f"report_{timestamp}.json"
        write_json(report_path, data)
        return str(report_path)

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检查摘要"""
        checks = results.get('checks', {})
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check and check.get('status') == 'pass')

        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }

    def list_available_modules(self) -> List[str]:
        """列出所有可用模块"""
        return list(self.modules.keys())

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """获取模块信息"""
        if module_name not in self.modules:
            return None

        module = self.modules[module_name]
        return {
            'name': module.name,
            'module_path': module.module_path,
            'class_name': module.class_name,
            'loaded': module.instance is not None
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI弹窗项目脚本系统主控制器')
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

    # 创建控制器
    controller = ScriptController(args.project_root)

    # 处理命令
    if args.list_modules:
        modules = controller.list_available_modules()
        print("可用模块:")
        for module in modules:
            print(f"  - {module}")
        return 0

    if args.module_info:
        info = controller.get_module_info(args.module_info)
        if info:
            print(f"模块信息: {args.module_info}")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"模块不存在: {args.module_info}")
        return 0

    if args.module:
        # 执行指定模块
        result = controller.execute_module(args.module, args.method)
        if result:
            print(f"模块执行结果: {result}")
        return 0

    # 执行任务
    if args.task == 'health-check':
        results = controller.run_health_check()
    elif args.task == 'config-management':
        results = controller.run_config_management()
    elif args.task == 'docs-management':
        results = controller.run_docs_management()
    elif args.task == 'ui-monitoring':
        results = controller.run_ui_monitoring()
    else:
        print(f"未知任务: {args.task}")
        return 1

    # 生成报告
    report_path = controller.generate_report(results, args.output_format)

    # 输出结果
    if not args.quiet:
        summary = results.get('summary', {})
        print(f"\n任务执行完成")
        print(f"报告路径: {report_path}")
        if 'success_rate' in summary:
            print(f"成功率: {summary['success_rate']:.1f}%")

    return 0

if __name__ == '__main__':
    sys.exit(main())
