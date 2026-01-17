#!/usr/bin/env python3
"""
文档同步监控脚本
独立运行，监控文档更新状态和同步情况
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/docs_sync_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DocsSyncMonitor:
    """文档同步监控器"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.issues = []
        self.warnings = []
        self.recommendations = []

        # 文档路径定义
        self.docs_paths = {
            'docs_dir': self.project_root / 'docs',
            'project_docs': self.project_root / 'docs' / 'project_docs',
            'deployment_docs': self.project_root / 'docs' / 'deployment_progress',
            'readme': self.project_root / 'README.md',
            'todo': self.project_root / 'TODO.md'
        }

        logger.info(f"初始化文档同步监控器，项目根目录: {self.project_root}")

    def monitor_docs_sync(self) -> Dict[str, Any]:
        """监控文档同步状态"""
        logger.info("开始监控文档同步状态...")
        start_time = time.time()

        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'summary': {}
        }

        # 1. 检查文档结构完整性
        results['checks']['structure'] = self.check_docs_structure()

        # 2. 检查文档更新状态
        results['checks']['freshness'] = self.check_docs_freshness()

        # 3. 检查文档与代码同步
        results['checks']['code_sync'] = self.check_code_doc_sync()

        # 4. 检查文档间引用一致性
        results['checks']['cross_refs'] = self.check_cross_references()

        # 5. 生成文档更新建议
        results['checks']['update_suggestions'] = self.generate_update_suggestions()

        # 汇总结果
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        results['recommendations'] = self.recommendations
        results['summary'] = self.generate_summary(results)
        results['duration'] = time.time() - start_time

        logger.info(f"文档同步监控完成，耗时: {results['duration']:.2f}秒")
        return results

    def check_docs_structure(self) -> Dict[str, Any]:
        """检查文档结构完整性"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 必需文档列表
        required_docs = {
            'root': ['README.md', 'TODO.md'],
            'docs': ['docs_README.md', 'docs_config.json'],
            'project_docs': [
                '01-project-architecture.md',
                '02-runtime-logic.md',
                '03-dependencies-config.md',
                '04-frontend-backend-api.md',
                '05-automation-scripts.md'
            ],
            'deployment_docs': [
                '01-overall-progress.md',
                '02-optimization-opportunities.md',
                '03-current-deployment-progress.md',
                '04-task-tracking.md'
            ]
        }

        for category, docs in required_docs.items():
            for doc in docs:
                if category == 'root':
                    doc_path = self.project_root / doc
                elif category == 'docs':
                    doc_path = self.docs_paths['docs_dir'] / doc
                elif category == 'project_docs':
                    doc_path = self.docs_paths['project_docs'] / doc
                elif category == 'deployment_docs':
                    doc_path = self.docs_paths['deployment_docs'] / doc

                if not doc_path.exists():
                    result['issues'].append(f"缺少{category}文档: {doc}")
                    result['status'] = 'fail'
                else:
                    result['details'][f"{category}/{doc}"] = 'exists'

        # 检查文档配置
        docs_config_path = self.docs_paths['docs_dir'] / 'docs_config.json'
        if docs_config_path.exists():
            try:
                with open(docs_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                if 'structure' not in config:
                    result['warnings'].append("文档配置缺少结构定义")

            except Exception as e:
                result['issues'].append(f"文档配置解析失败: {e}")
                result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_docs_freshness(self) -> Dict[str, Any]:
        """检查文档更新状态"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        now = datetime.now()
        freshness_thresholds = {
            'critical': timedelta(days=1),  # 部署进度、TODO
            'important': timedelta(days=7),  # 项目文档
            'normal': timedelta(days=30)  # 配置文档
        }

        # 检查各文档的更新时间
        docs_to_check = {
            'README.md': 'normal',
            'TODO.md': 'critical',
            'docs/docs_README.md': 'normal',
            'docs/docs_config.json': 'normal'
        }

        # 添加项目文档
        if self.docs_paths['project_docs'].exists():
            for doc_file in self.docs_paths['project_docs'].glob('*.md'):
                docs_to_check[str(doc_file.relative_to(self.project_root))] = 'important'

        # 添加部署文档
        if self.docs_paths['deployment_docs'].exists():
            for doc_file in self.docs_paths['deployment_docs'].glob('*.md'):
                docs_to_check[str(doc_file.relative_to(self.project_root))] = 'critical'

        for doc_path_str, priority in docs_to_check.items():
            doc_path = self.project_root / doc_path_str
            if doc_path.exists():
                mtime = datetime.fromtimestamp(doc_path.stat().st_mtime)
                age = now - mtime
                threshold = freshness_thresholds[priority]

                result['details'][doc_path_str] = {
                    'last_modified': mtime.isoformat(),
                    'age_days': age.days,
                    'priority': priority,
                    'status': 'fresh' if age <= threshold else 'stale'
                }

                if age > threshold:
                    if priority == 'critical':
                        result['issues'].append(f"紧急文档过期: {doc_path_str} ({age.days}天未更新)")
                        result['status'] = 'fail'
                    elif priority == 'important':
                        result['warnings'].append(f"重要文档过期: {doc_path_str} ({age.days}天未更新)")
                    else:
                        result['warnings'].append(f"文档过期: {doc_path_str} ({age.days}天未更新)")

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_code_doc_sync(self) -> Dict[str, Any]:
        """检查文档与代码同步"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查主要配置文件是否在文档中提及
        config_files = [
            'project_config.json',
            'requirements.txt',
            'src/src_config.json',
            'scripts/scripts_config.json'
        ]

        # 检查README.md是否包含配置说明
        readme_path = self.docs_paths['readme']
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read().lower()

                for config_file in config_files:
                    if config_file not in readme_content:
                        result['warnings'].append(f"README.md未提及配置文件: {config_file}")

            except Exception as e:
                result['issues'].append(f"README.md读取失败: {e}")
                result['status'] = 'fail'

        # 检查TODO.md与部署进度同步
        todo_path = self.docs_paths['todo']
        deployment_progress_path = self.docs_paths['deployment_docs'] / '04-task-tracking.md'

        if todo_path.exists() and deployment_progress_path.exists():
            try:
                with open(todo_path, 'r', encoding='utf-8') as f:
                    todo_content = f.read()

                with open(deployment_progress_path, 'r', encoding='utf-8') as f:
                    progress_content = f.read()

                # 检查主要任务是否同步
                todo_tasks = len([line for line in todo_content.split('\n') if line.strip().startswith('- [')])
                progress_tasks = len([line for line in progress_content.split('\n') if '任务' in line or 'TODO' in line])

                if abs(todo_tasks - progress_tasks) > 2:
                    result['warnings'].append(f"TODO.md与任务跟踪文档任务数量不一致: TODO({todo_tasks}) vs 跟踪({progress_tasks})")

            except Exception as e:
                result['issues'].append(f"任务文档同步检查失败: {e}")
                result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def check_cross_references(self) -> Dict[str, Any]:
        """检查文档间引用一致性"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        # 检查文档间相互引用
        cross_ref_patterns = {
            'README.md': ['docs/', 'src/', 'scripts/'],
            'docs/docs_README.md': ['project_docs/', 'deployment_progress/'],
            'TODO.md': ['docs/deployment_progress/']
        }

        for doc_file, expected_refs in cross_ref_patterns.items():
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()

                    missing_refs = []
                    for ref in expected_refs:
                        if ref not in content:
                            missing_refs.append(ref)

                    if missing_refs:
                        result['warnings'].append(f"{doc_file} 缺少对以下内容的引用: {', '.join(missing_refs)}")

                except Exception as e:
                    result['issues'].append(f"文档引用检查失败 {doc_file}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def generate_update_suggestions(self) -> Dict[str, Any]:
        """生成文档更新建议"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        suggestions = []

        # 检查配置文件变更
        config_files = [
            'project_config.json',
            'requirements.txt',
            'src/src_config.json'
        ]

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                # 查找对应的文档
                doc_mapping = {
                    'project_config.json': 'docs/project_docs/01-project-architecture.md',
                    'requirements.txt': 'docs/project_docs/03-dependencies-config.md',
                    'src/src_config.json': 'docs/project_docs/01-project-architecture.md'
                }

                doc_path = self.project_root / doc_mapping.get(config_file, '')
                if doc_path.exists():
                    config_mtime = config_path.stat().st_mtime
                    doc_mtime = doc_path.stat().st_mtime

                    if config_mtime > doc_mtime:
                        days_diff = (datetime.now() - datetime.fromtimestamp(doc_mtime)).days
                        suggestions.append({
                            'type': 'config_doc_sync',
                            'config': config_file,
                            'doc': str(doc_path.relative_to(self.project_root)),
                            'days_outdated': days_diff,
                            'priority': 'high' if days_diff > 7 else 'medium'
                        })

        # 检查代码变更是否需要文档更新
        code_dirs = ['src', 'scripts']
        for code_dir in code_dirs:
            code_path = self.project_root / code_dir
            if code_path.exists():
                # 查找最近修改的代码文件
                recent_changes = []
                for py_file in code_path.rglob('*.py'):
                    if py_file.stat().st_mtime > (datetime.now().timestamp() - 86400 * 7):  # 7天内
                        recent_changes.append(str(py_file.relative_to(self.project_root)))

                if recent_changes:
                    suggestions.append({
                        'type': 'code_changes',
                        'directory': code_dir,
                        'recent_files': recent_changes[:5],  # 最多显示5个
                        'suggestion': f"检查{code_dir}目录的近期代码变更是否需要文档更新"
                    })

        result['details']['suggestions'] = suggestions
        self.recommendations.extend([s['suggestion'] for s in suggestions if 'suggestion' in s])

        return result

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成监控摘要"""
        summary = {
            'total_checks': len(results['checks']),
            'passed_checks': 0,
            'failed_checks': 0,
            'warning_checks': 0,
            'total_issues': len(results['issues']),
            'total_warnings': len(results['warnings']),
            'total_recommendations': len(results['recommendations']),
            'sync_score': 0.0
        }

        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            if status == 'pass':
                summary['passed_checks'] += 1
            elif status == 'fail':
                summary['failed_checks'] += 1
            elif status == 'warning':
                summary['warning_checks'] += 1

        summary['sync_score'] = (summary['passed_checks'] / summary['total_checks']) * 100 if summary['total_checks'] > 0 else 0.0

        return summary

    def save_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """保存监控报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/docs_sync_report_{timestamp}.json"

        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"文档同步监控报告已保存到: {output_path}")
        return str(output_path)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='文档同步监控器')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--quiet', action='store_true', help='静默模式')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    monitor = DocsSyncMonitor(args.project_root)
    results = monitor.monitor_docs_sync()

    # 保存报告
    report_path = monitor.save_report(results, args.output)

    # 输出摘要
    summary = results['summary']
    print(f"\n文档同步监控摘要:")
    print(f"总检查数: {summary['total_checks']}")
    print(f"通过: {summary['passed_checks']}")
    print(f"失败: {summary['failed_checks']}")
    print(f"警告: {summary['warning_checks']}")
    print(f"同步评分: {summary['sync_score']:.1f}%")
    print(f"发现问题: {summary['total_issues']}")
    print(f"警告信息: {summary['total_warnings']}")
    print(f"更新建议: {summary['total_recommendations']}")
    print(f"报告路径: {report_path}")

    # 返回退出码
    return 0 if summary['failed_checks'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
