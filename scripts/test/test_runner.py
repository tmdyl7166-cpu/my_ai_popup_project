#!/usr/bin/env python3
"""
测试运行器

功能:
    - 统一调度所有测试模块
    - 生成综合测试报告
    - 支持按需运行特定测试

使用方法:
    cd /workspaces/my_ai_popup_project
    python3 scripts/test/test_runner.py                    # 运行所有测试
    python3 scripts/test/test_runner.py --launch          # 只运行启动配置测试
    python3 scripts/test/test_runner.py --frontend        # 只运行前后端测试
    python3 scripts/test/test_runner.py --deps            # 只运行依赖检查
    python3 scripts/test/test_runner.py --error           # 只运行错误处理测试
    python3 scripts/test/test_runner.py --all             # 运行所有测试并生成报告
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = {}
        self.summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'skipped': 0
        }

    def log(self, message: str, level: str = 'INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {'INFO': '[INFO]', 'WARNING': '[WARNING]', 'ERROR': '[ERROR]', 'SUCCESS': '[SUCCESS]'}.get(level, '[INFO]')
        print(f"{timestamp} {prefix} {message}")

    def run_launch_config_test(self) -> Dict:
        """运行启动配置测试"""
        self.log("=" * 60)
        self.log("运行启动配置测试")
        self.log("=" * 60)
        
        try:
            from scripts.test.test_launch_config import LaunchConfigTester
            tester = LaunchConfigTester()
            return tester.run_all_tests()
        except Exception as e:
            self.log(f"启动配置测试执行失败: {e}", 'ERROR')
            return {'overall_status': 'error', 'error': str(e)}

    def run_frontend_backend_test(self) -> Dict:
        """运行前后端联动测试"""
        self.log("=" * 60)
        self.log("运行前后端联动测试")
        self.log("=" * 60)
        
        try:
            from scripts.test.test_frontend_backend import FrontendBackendTester
            tester = FrontendBackendTester()
            return tester.run_all_tests()
        except Exception as e:
            self.log(f"前后端联动测试执行失败: {e}", 'ERROR')
            return {'overall_status': 'error', 'error': str(e)}

    def run_dependency_test(self) -> Dict:
        """运行依赖检查"""
        self.log("=" * 60)
        self.log("运行依赖检查")
        self.log("=" * 60)
        
        try:
            from scripts.test.test_dependencies import DependencyChecker
            checker = DependencyChecker()
            return checker.run_all_checks()
        except Exception as e:
            self.log(f"依赖检查执行失败: {e}", 'ERROR')
            return {'overall_status': 'error', 'error': str(e)}

    def run_error_handling_test(self) -> Dict:
        """运行错误处理测试"""
        self.log("=" * 60)
        self.log("运行错误处理测试")
        self.log("=" * 60)
        
        try:
            from scripts.test.test_error_handling import ErrorHandlingTester
            tester = ErrorHandlingTester()
            return tester.run_all_tests()
        except Exception as e:
            self.log(f"错误处理测试执行失败: {e}", 'ERROR')
            return {'overall_status': 'error', 'error': str(e)}

    def update_summary(self, results: Dict, test_name: str):
        """更新汇总信息"""
        self.test_results[test_name] = results
        
        if 'summary' in results:
            self.summary['total_tests'] += results['summary'].get('total', 0)
            self.summary['passed'] += results['summary'].get('passed', 0)
            self.summary['failed'] += results['summary'].get('failed', 0)
            self.summary['warnings'] += results['summary'].get('warnings', 0)
            self.summary['skipped'] += results['summary'].get('skipped', 0)

    def generate_final_report(self) -> Dict:
        """生成最终报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'summary': self.summary,
            'overall_status': self.calculate_overall_status()
        }
        return report

    def calculate_overall_status(self) -> str:
        """计算总体状态"""
        if self.summary['failed'] > 0:
            return 'fail'
        elif self.summary['warnings'] > 0:
            return 'warning'
        elif self.summary['passed'] > 0:
            return 'pass'
        else:
            return 'skip'

    def print_final_summary(self, report: Dict):
        """打印最终汇总"""
        self.log("\n" + "=" * 60)
        self.log("最终测试汇总")
        self.log("=" * 60)
        self.log(f"总测试数: {self.summary['total_tests']}")
        self.log(f"通过: {self.summary['passed']}")
        self.log(f"失败: {self.summary['failed']}")
        self.log(f"警告: {self.summary['warnings']}")
        self.log(f"跳过: {self.summary['skipped']}")
        self.log(f"\n总体状态: {report['overall_status']}")
        self.log("=" * 60)

    def save_report(self, report: Dict):
        """保存报告"""
        report_dir = self.project_root / 'logs' / 'test_reports'
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'full_test_report_{timestamp}.json'

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"完整测试报告已保存: {report_file}")
        return report_file

    def run_all(self):
        """运行所有测试"""
        self.log("=" * 60)
        self.log("开始完整测试套件")
        self.log("=" * 60)

        # 运行各个测试
        self.update_summary(self.run_launch_config_test(), 'launch_config')
        self.update_summary(self.run_dependency_test(), 'dependencies')
        self.update_summary(self.run_error_handling_test(), 'error_handling')
        self.update_summary(self.run_frontend_backend_test(), 'frontend_backend')

        # 生成报告
        report = self.generate_final_report()
        self.print_final_summary(report)
        self.save_report(report)

        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI弹窗项目测试运行器')
    parser.add_argument('--launch', action='store_true', help='运行启动配置测试')
    parser.add_argument('--frontend', action='store_true', help='运行前后端联动测试')
    parser.add_argument('--deps', action='store_true', help='运行依赖检查')
    parser.add_argument('--error', action='store_true', help='运行错误处理测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    
    args = parser.parse_args()

    print("=" * 60)
    print("AI弹窗项目测试运行器")
    print("=" * 60)

    runner = TestRunner()
    
    # 如果没有指定参数，运行所有测试
    if not any([args.launch, args.frontend, args.deps, args.error]):
        report = runner.run_all()
    else:
        # 运行指定测试
        if args.launch:
            runner.update_summary(runner.run_launch_config_test(), 'launch_config')
        if args.deps:
            runner.update_summary(runner.run_dependency_test(), 'dependencies')
        if args.error:
            runner.update_summary(runner.run_error_handling_test(), 'error_handling')
        if args.frontend:
            runner.update_summary(runner.run_frontend_backend_test(), 'frontend_backend')
        
        report = runner.generate_final_report()
        runner.print_final_summary(report)
        runner.save_report(report)

    # 返回退出码
    sys.exit(0 if report['overall_status'] in ['pass', 'skip'] else 1)


if __name__ == '__main__':
    main()

