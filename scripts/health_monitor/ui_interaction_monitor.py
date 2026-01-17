#!/usr/bin/env python3
"""
UI交互健康检测脚本
专门检测前端交互、弹窗管理、数据传递、缓存清理等UI相关问题
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import ast

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ui_interaction_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UIInteractionMonitor:
    """UI交互健康检测主类"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.issues = []
        self.warnings = []
        self.recommendations = []

        # UI相关路径
        self.ui_paths = {
            'frontend': self.project_root / 'src' / 'frontend',
            'components': self.project_root / 'src' / 'frontend' / 'components',
            'styles': self.project_root / 'src' / 'frontend' / 'styles',
            'main_window': self.project_root / 'src' / 'frontend' / 'main_window.py',
            'popup_window': self.project_root / 'src' / 'frontend' / 'popup_window.py',
            'config': self.project_root / 'src' / 'frontend' / 'frontend_config.json'
        }

        logger.info(f"初始化UI交互检测系统，项目根目录: {self.project_root}")

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """运行全面UI交互检查"""
        logger.info("开始全面UI交互检查...")
        start_time = time.time()

        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'summary': {}
        }

        # 1. 弹窗管理检查
        results['checks']['popup_management'] = self.check_popup_management()

        # 2. 事件处理检查
        results['checks']['event_handling'] = self.check_event_handling()

        # 3. 数据传递检查
        results['checks']['data_passing'] = self.check_data_passing()

        # 4. 缓存管理检查
        results['checks']['cache_management'] = self.check_cache_management()

        # 5. 异步加载检查
        results['checks']['async_loading'] = self.check_async_loading()

        # 6. 适配性检查
        results['checks']['responsiveness'] = self.check_responsiveness()

        # 7. 安全检查
        results['checks']['security'] = self.check_security()

        # 8. 性能检查
        results['checks']['performance'] = self.check_performance()

        # 汇总结果
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        results['recommendations'] = self.recommendations
        results['summary'] = self.generate_summary(results)
        results['duration'] = time.time() - start_time

        logger.info(f"UI交互检查完成，耗时: {results['duration']:.2f}秒")
        return results

    def check_popup_management(self) -> Dict[str, Any]:
        """检查弹窗管理"""
        logger.info("检查弹窗管理...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查弹窗文件
        popup_files = [
            'main_window.py',
            'popup_window.py',
            'video_panel.py',
            'image_panel.py',
            'control_buttons.py'
        ]

        for file in popup_files:
            path = self.ui_paths['frontend'] / file
            if not path.exists():
                result['issues'].append(f"缺少弹窗相关文件: {file}")
                result['status'] = 'fail'
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查弹窗层级管理
                if 'closeEvent' in content or 'close' in content:
                    if 'parent' not in content.lower():
                        result['warnings'].append(f"{file}: 弹窗关闭可能缺少父窗口引用")

                # 检查事件冒泡防护
                if 'event' in content.lower():
                    if 'accept()' not in content and 'ignore()' not in content:
                        result['warnings'].append(f"{file}: 可能缺少事件冒泡控制")

                # 检查嵌套弹窗管理
                if 'show()' in content and 'exec_' in content:
                    if 'modal' not in content.lower():
                        result['warnings'].append(f"{file}: 嵌套弹窗可能缺少模态设置")

            except Exception as e:
                result['issues'].append(f"弹窗文件分析失败 {file}: {e}")
                result['status'] = 'fail'

        # 检查弹窗配置
        config_path = self.ui_paths['config']
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 检查弹窗配置完整性
                ui_config = config.get('ui', {})
                if 'window' not in ui_config:
                    result['issues'].append("前端配置缺少窗口设置")
                    result['status'] = 'fail'

                # 检查弹窗动画配置
                interaction = config.get('interaction', {})
                if 'animations' not in interaction:
                    result['warnings'].append("建议添加弹窗动画配置")

            except Exception as e:
                result['issues'].append(f"弹窗配置检查失败: {e}")
                result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_event_handling(self) -> Dict[str, Any]:
        """检查事件处理"""
        logger.info("检查事件处理...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查事件处理模式
        event_patterns = [
            r'connect\s*\(',
            r'signal',
            r'slot',
            r'clicked',
            r'triggered',
            r'activated'
        ]

        components_dir = self.ui_paths['components']
        if components_dir.exists():
            for py_file in components_dir.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查事件绑定
                    event_connections = len(re.findall(r'connect\s*\(', content))
                    result['details'][py_file.name] = {'event_connections': event_connections}

                    # 检查事件冒泡防护
                    if 'event' in content.lower():
                        if not re.search(r'accept\(\)|ignore\(\)', content):
                            result['warnings'].append(f"{py_file.name}: 事件处理可能缺少冒泡控制")

                    # 检查异步事件处理
                    if 'thread' in content.lower() or 'async' in content.lower():
                        if 'signal' not in content.lower():
                            result['warnings'].append(f"{py_file.name}: 异步操作建议使用信号机制")

                except Exception as e:
                    result['issues'].append(f"事件处理检查失败 {py_file.name}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_data_passing(self) -> Dict[str, Any]:
        """检查数据传递"""
        logger.info("检查数据传递...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查数据传递模式
        data_patterns = [
            r'setData|data\(\)',
            r'signal.*emit',
            r'callback',
            r'lambda',
            r'partial'
        ]

        # 检查主要UI文件
        ui_files = ['main_window.py', 'popup_window.py']
        for file in ui_files:
            path = self.ui_paths['frontend'] / file
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查数据传递机制
                    has_signals = 'signal' in content.lower()
                    has_callbacks = 'callback' in content.lower()
                    has_data_methods = bool(re.search(r'data\(\)|setData', content))

                    if not (has_signals or has_callbacks or has_data_methods):
                        result['warnings'].append(f"{file}: 建议添加明确的数据传递机制")

                    # 检查数据验证
                    if 'data' in content.lower():
                        if not re.search(r'validate|check|verify', content.lower()):
                            result['warnings'].append(f"{file}: 数据传递建议添加验证")

                except Exception as e:
                    result['issues'].append(f"数据传递检查失败 {file}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_cache_management(self) -> Dict[str, Any]:
        """检查缓存管理"""
        logger.info("检查缓存管理...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查缓存清理机制
        cache_patterns = [
            r'clear|cleanup|flush',
            r'cache',
            r'temp',
            r'gc\.collect',
            r'del\s+\w+'
        ]

        # 检查工具模块
        utils_dir = self.project_root / 'src' / 'utils'
        if utils_dir.exists():
            for py_file in utils_dir.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查缓存清理
                    has_cleanup = any(re.search(pattern, content, re.IGNORECASE) for pattern in cache_patterns)
                    if has_cleanup:
                        result['details'][py_file.name] = {'has_cache_cleanup': True}
                    else:
                        result['warnings'].append(f"{py_file.name}: 建议添加缓存清理机制")

                    # 检查内存管理
                    if 'cache' in content.lower():
                        if not re.search(r'memory|gc|del', content.lower()):
                            result['warnings'].append(f"{py_file.name}: 缓存管理建议添加内存清理")

                except Exception as e:
                    result['issues'].append(f"缓存管理检查失败 {py_file.name}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_async_loading(self) -> Dict[str, Any]:
        """检查异步加载"""
        logger.info("检查异步加载...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查异步加载模式
        async_patterns = [
            r'QThread',
            r'Worker',
            r'async|await',
            r'concurrent',
            r'thread',
            r'future'
        ]

        # 检查前端组件
        components_dir = self.ui_paths['components']
        if components_dir.exists():
            for py_file in components_dir.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查异步操作
                    has_async = any(re.search(pattern, content, re.IGNORECASE) for pattern in async_patterns)
                    if has_async:
                        result['details'][py_file.name] = {'has_async_operations': True}

                        # 检查进度反馈
                        if not re.search(r'progress|signal|emit', content.lower()):
                            result['warnings'].append(f"{py_file.name}: 异步操作建议添加进度反馈")

                        # 检查错误处理
                        if not re.search(r'except|try|error', content.lower()):
                            result['warnings'].append(f"{py_file.name}: 异步操作建议添加错误处理")

                    # 检查懒加载
                    if 'load' in content.lower():
                        if not re.search(r'lazy|on_demand|dynamic', content.lower()):
                            result['warnings'].append(f"{py_file.name}: 加载操作建议考虑懒加载")

                except Exception as e:
                    result['issues'].append(f"异步加载检查失败 {py_file.name}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_responsiveness(self) -> Dict[str, Any]:
        """检查适配性"""
        logger.info("检查适配性...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查响应式设计
        responsive_patterns = [
            r'resizeEvent',
            r'sizeHint',
            r'minimumSize|maximumSize',
            r'scale|dpi',
            r'adjustSize'
        ]

        # 检查配置文件
        config_path = self.ui_paths['config']
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 检查窗口配置
                window_config = config.get('ui', {}).get('window', {})
                if 'minSize' not in window_config:
                    result['warnings'].append("建议添加最小窗口尺寸配置")

                if 'maxSize' not in window_config:
                    result['warnings'].append("建议添加最大窗口尺寸配置")

                # 检查布局配置
                layout_config = config.get('ui', {}).get('layout', {})
                if not layout_config:
                    result['warnings'].append("建议添加布局适配配置")

            except Exception as e:
                result['issues'].append(f"适配性配置检查失败: {e}")
                result['status'] = 'fail'

        # 检查代码中的响应式处理
        main_window_path = self.ui_paths['main_window']
        if main_window_path.exists():
            try:
                with open(main_window_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                has_responsive = any(re.search(pattern, content) for pattern in responsive_patterns)
                if not has_responsive:
                    result['warnings'].append("主窗口建议添加响应式处理")

            except Exception as e:
                result['issues'].append(f"响应式代码检查失败: {e}")
                result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_security(self) -> Dict[str, Any]:
        """检查安全"""
        logger.info("检查安全...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查安全模式
        security_patterns = [
            r'validate|check|sanitize',
            r'escape|quote',
            r'safe_load',
            r'permission|access'
        ]

        # 检查数据处理
        backend_dir = self.project_root / 'src' / 'backend'
        if backend_dir.exists():
            for py_file in backend_dir.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查输入验证
                    if 'input' in content.lower() or 'data' in content.lower():
                        has_validation = any(re.search(pattern, content, re.IGNORECASE) for pattern in security_patterns)
                        if not has_validation:
                            result['warnings'].append(f"{py_file.name}: 数据输入建议添加验证")

                    # 检查SQL注入防护
                    if 'sql' in content.lower() or 'query' in content.lower():
                        if not re.search(r'parameter|bind|prepared', content.lower()):
                            result['warnings'].append(f"{py_file.name}: 数据库操作建议使用参数化查询")

                except Exception as e:
                    result['issues'].append(f"安全检查失败 {py_file.name}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_performance(self) -> Dict[str, Any]:
        """检查性能"""
        logger.info("检查性能...")
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查性能模式
        performance_patterns = [
            r'QTimer',
            r'optimize|performance',
            r'cache',
            r'lazy',
            r'batch'
        ]

        # 检查组件性能
        components_dir = self.ui_paths['components']
        if components_dir.exists():
            for py_file in components_dir.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查性能优化
                    has_performance = any(re.search(pattern, content, re.IGNORECASE) for pattern in performance_patterns)
                    if not has_performance and len(content) > 1000:
                        result['warnings'].append(f"{py_file.name}: 大型组件建议添加性能优化")

                    # 检查内存泄漏风险
                    if '__del__' not in content and 'QObject' in content:
                        result['warnings'].append(f"{py_file.name}: QObject子类建议检查内存管理")

                except Exception as e:
                    result['issues'].append(f"性能检查失败 {py_file.name}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检查摘要"""
        summary = {
            'total_checks': len(results['checks']),
            'passed_checks': 0,
            'failed_checks': 0,
            'warning_checks': 0,
            'total_issues': len(results['issues']),
            'total_warnings': len(results['warnings']),
            'health_score': 0.0
        }

        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            if status == 'pass':
                summary['passed_checks'] += 1
            elif status == 'fail':
                summary['failed_checks'] += 1
            elif status == 'warning':
                summary['warning_checks'] += 1

        summary['health_score'] = (summary['passed_checks'] / summary['total_checks']) * 100 if summary['total_checks'] > 0 else 0.0

        return summary

    def save_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """保存检查报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/ui_interaction_report_{timestamp}.json"

        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"UI交互检查报告已保存到: {output_path}")
        return str(output_path)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='UI交互健康检测系统')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--quiet', action='store_true', help='静默模式')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    monitor = UIInteractionMonitor(args.project_root)
    results = monitor.run_comprehensive_check()

    # 保存报告
    report_path = monitor.save_report(results, args.output)

    # 输出摘要
    summary = results['summary']
    print(f"\nUI交互检查摘要:")
    print(f"总检查数: {summary['total_checks']}")
    print(f"通过: {summary['passed_checks']}")
    print(f"失败: {summary['failed_checks']}")
    print(f"警告: {summary['warning_checks']}")
    print(f"健康评分: {summary['health_score']:.1f}%")
    print(f"发现问题: {summary['total_issues']}")
    print(f"警告信息: {summary['total_warnings']}")
    print(f"报告路径: {report_path}")

    # 返回退出码
    return 0 if summary['failed_checks'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
