"""
健康监控编排器
负责协调所有健康检查模块的执行
"""
from pathlib import Path
from typing import Dict, List, Any
import time
import logging
from datetime import datetime

from .structure_checker import ProjectStructureChecker
from .config_consistency_checker import ConfigConsistencyChecker
from .rules_validator import RulesValidator
from .docs_sync_checker import DocsSyncChecker
from .dependency_checker import DependencyChecker
from .task_docs_unifier import TaskDocsUnifier
from .file_cleanup_util import FileCleanupUtil

logger = logging.getLogger(__name__)

class HealthMonitorOrchestrator:
    """健康监控编排器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []

        # 初始化所有检查器
        self.structure_checker = ProjectStructureChecker(project_root)
        self.config_checker = ConfigConsistencyChecker(project_root)
        self.rules_validator = RulesValidator(project_root)
        self.docs_checker = DocsSyncChecker(project_root)
        self.dependency_checker = DependencyChecker(project_root)
        self.task_unifier = TaskDocsUnifier(project_root)
        self.file_cleaner = FileCleanupUtil(project_root)

    def run_full_check(self) -> Dict[str, Any]:
        """运行完整健康检查"""
        logger.info("开始完整健康检查...")
        start_time = time.time()

        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'issues': [],
            'recommendations': [],
            'summary': {}
        }

        # 依次执行所有检查
        check_methods = [
            ('structure', self.structure_checker.check_structure),
            ('config', self.config_checker.check_consistency),
            ('rules', self.rules_validator.validate_rules),
            ('docs', self.docs_checker.check_docs_sync),
            ('dependencies', self.dependency_checker.check_dependencies),
            ('tasks', self.task_unifier.unify_task_docs),
            ('cleanup', self.file_cleaner.cleanup_stale_files)
        ]

        for check_name, check_method in check_methods:
            try:
                logger.info(f"执行检查: {check_name}")
                results['checks'][check_name] = check_method()
            except Exception as e:
                logger.error(f"检查 {check_name} 失败: {e}")
                results['checks'][check_name] = {
                    'status': 'error',
                    'error': str(e)
                }

        # 汇总结果
        results['issues'] = self._collect_issues(results)
        results['summary'] = self._generate_summary(results)
        results['duration'] = time.time() - start_time

        logger.info(f"健康检查完成，耗时: {results['duration']:.2f}秒")
        return results

    def _collect_issues(self, results: Dict[str, Any]) -> List[str]:
        """收集所有问题"""
        issues = []
        for check_name, check_result in results['checks'].items():
            if 'issues' in check_result:
                issues.extend(check_result['issues'])
        return issues

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检查摘要"""
        summary = {
            'total_checks': len(results['checks']),
            'passed_checks': 0,
            'failed_checks': 0,
            'warning_checks': 0,
            'error_checks': 0,
            'total_issues': len(results['issues'])
        }

        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            if status == 'pass':
                summary['passed_checks'] += 1
            elif status == 'fail':
                summary['failed_checks'] += 1
            elif status == 'warning':
                summary['warning_checks'] += 1
            elif status == 'error':
                summary['error_checks'] += 1

        summary['health_score'] = float((summary['passed_checks'] / summary['total_checks']) * 100) if summary['total_checks'] > 0 else 0.0

        return summary
