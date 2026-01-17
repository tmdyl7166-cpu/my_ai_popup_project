#!/usr/bin/env python3
"""
AI弹窗项目健康监控系统
提供全面的自动化健康检查、文档同步和项目维护功能
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import subprocess
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """项目健康监控主类"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.config_cache = {}
        self.last_check = None
        self.issues = []

        # 关键路径定义
        self.paths = {
            'project_config': self.project_root / 'project_config.json',
            'docs_config': self.project_root / 'docs' / 'docs_config.json',
            'todo': self.project_root / 'TODO.md',
            'rules': self.project_root / 'rules',
            'src': self.project_root / 'src',
            'assets': self.project_root / 'assets',
            'docs': self.project_root / 'docs',
            'logs': self.project_root / 'logs'
        }

        logger.info(f"初始化健康监控系统，项目根目录: {self.project_root}")

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

        # 1. 基础结构检查
        results['checks']['structure'] = self.check_project_structure()

        # 2. 配置一致性检查
        results['checks']['config'] = self.check_config_consistency()

        # 3. 规则系统检查
        results['checks']['rules'] = self.check_rules_system()

        # 4. 文档同步检查
        results['checks']['docs'] = self.check_docs_sync()

        # 5. 依赖检查
        results['checks']['dependencies'] = self.check_dependencies()

        # 6. 任务文档统一
        results['checks']['tasks'] = self.unify_task_docs()

        # 7. 清理沉积文件
        results['checks']['cleanup'] = self.cleanup_stale_files()

        # 汇总结果
        results['issues'] = self.issues
        results['summary'] = self.generate_summary(results)
        results['duration'] = time.time() - start_time

        logger.info(f"健康检查完成，耗时: {results['duration']:.2f}秒")
        return results

    def check_project_structure(self) -> Dict[str, Any]:
        """检查项目基础结构"""
        logger.info("检查项目基础结构...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        required_paths = [
            'project_config.json',
            'requirements.txt',
            'README.md',
            'src',
            'assets',
            'rules',
            'docs',
            'logs'
        ]

        for path_name in required_paths:
            path = self.project_root / path_name
            if path.exists():
                result['details'][path_name] = 'exists'
            else:
                result['details'][path_name] = 'missing'
                result['issues'].append(f"缺少必需路径: {path_name}")
                result['status'] = 'fail'

        # 检查子项目结构
        subprojects = ['src', 'assets', 'rules', 'docs']
        for sub in subprojects:
            sub_path = self.project_root / sub
            if sub_path.exists():
                config_file = sub_path / f"{sub}_config.json"
                readme_file = sub_path / f"{sub}_README.md"
                if not config_file.exists():
                    result['issues'].append(f"缺少配置文件: {config_file}")
                    result['status'] = 'fail'
                if not readme_file.exists():
                    result['issues'].append(f"缺少说明文档: {readme_file}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        return result

    def check_config_consistency(self) -> Dict[str, Any]:
        """检查配置一致性"""
        logger.info("检查配置一致性...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        # 加载主要配置
        configs = {}
        config_files = [
            'project_config.json',
            'docs/docs_config.json',
            'rules/rules.config.js',
            'src/src_config.json'
        ]

        for config_file in config_files:
            path = self.project_root / config_file
            if path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(path, 'r', encoding='utf-8') as f:
                            configs[config_file] = json.load(f)
                    elif config_file.endswith('.js'):
                        # 简单处理JS配置文件
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            configs[config_file] = {'content': content}
                except Exception as e:
                    result['issues'].append(f"配置加载失败 {config_file}: {e}")
                    result['status'] = 'fail'

        # 检查路径一致性
        if 'project_config.json' in configs and 'docs/docs_config.json' in configs:
            project_paths = configs['project_config.json'].get('deployment', {}).get('paths', {})
            docs_paths = configs['docs/docs_config.json'].get('structure', {})

            # 检查关键路径匹配
            for key, path in project_paths.items():
                if key in docs_paths:
                    if path != docs_paths[key]:
                        result['issues'].append(f"路径不一致: {key} - 项目:{path}, 文档:{docs_paths[key]}")
                        result['status'] = 'fail'

        result['details'] = {'loaded_configs': list(configs.keys())}
        self.issues.extend(result['issues'])
        return result

    def check_rules_system(self) -> Dict[str, Any]:
        """检查规则系统"""
        logger.info("检查规则系统...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        rules_dir = self.paths['rules']
        required_files = [
            'L1-meta-goal.json',
            'L2-understanding.json',
            'L3-constraints.json',
            'L4-decisions.json',
            'L5-execution.json',
            'rules.config.js'
        ]

        for file in required_files:
            path = rules_dir / file
            if not path.exists():
                result['issues'].append(f"缺少规则文件: {file}")
                result['status'] = 'fail'
            else:
                try:
                    if file.endswith('.json'):
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # 检查基本结构
                            if 'meta' not in data:
                                result['issues'].append(f"规则文件结构不完整: {file}")
                                result['status'] = 'fail'
                except Exception as e:
                    result['issues'].append(f"规则文件解析失败 {file}: {e}")
                    result['status'] = 'fail'

        # 检查层级依赖
        if result['status'] == 'pass':
            try:
                l1 = json.loads((rules_dir / 'L1-meta-goal.json').read_text(encoding='utf-8'))
                l2 = json.loads((rules_dir / 'L2-understanding.json').read_text(encoding='utf-8'))

                # 检查L2是否引用L1
                if 'goals' in l1 and 'architecture' in l2:
                    result['details']['layer_consistency'] = 'consistent'
                else:
                    result['issues'].append("规则层级依赖关系不清晰")
                    result['status'] = 'fail'
            except Exception as e:
                result['issues'].append(f"层级依赖检查失败: {e}")
                result['status'] = 'fail'

        self.issues.extend(result['issues'])
        return result

    def check_docs_sync(self) -> Dict[str, Any]:
        """检查文档同步状态"""
        logger.info("检查文档同步状态...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        docs_dir = self.paths['docs']

        # 检查文档结构
        required_docs = [
            'docs_README.md',
            'docs_config.json'
        ]

        project_docs = [
            '01-project-architecture.md',
            '02-runtime-logic.md',
            '03-dependencies-config.md',
            '04-frontend-backend-api.md',
            '05-automation-scripts.md'
        ]

        deployment_docs = [
            '01-overall-progress.md',
            '02-optimization-opportunities.md',
            '03-current-deployment.md'
        ]

        for doc in required_docs + project_docs + deployment_docs:
            path = docs_dir / 'project_docs' / doc if doc in project_docs else \
                   docs_dir / 'deployment_progress' / doc if doc in deployment_docs else \
                   docs_dir / doc
            if not path.exists():
                result['issues'].append(f"缺少文档: {doc}")
                result['status'] = 'fail'

        # 检查文档更新时间
        if result['status'] == 'pass':
            doc_files = [docs_dir / 'docs_config.json'] + \
                       [docs_dir / 'project_docs' / d for d in project_docs] + \
                       [docs_dir / 'deployment_progress' / d for d in deployment_docs]

            now = datetime.now()
            outdated = []
            for doc_file in doc_files:
                if doc_file.exists():
                    mtime = datetime.fromtimestamp(doc_file.stat().st_mtime)
                    if (now - mtime) > timedelta(days=7):
                        outdated.append(doc_file.name)

            if outdated:
                result['issues'].append(f"文档需要更新: {', '.join(outdated)}")
                result['status'] = 'warning'

        result['details'] = {'checked_docs': len(required_docs + project_docs + deployment_docs)}
        self.issues.extend(result['issues'])
        return result

    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖状态"""
        logger.info("检查依赖状态...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        # 检查requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    result['details']['declared_deps'] = len(deps)

                # 尝试导入关键依赖
                key_deps = ['PyQt5', 'fastapi', 'torch', 'opencv-python']
                missing_deps = []
                for dep in key_deps:
                    try:
                        __import__(dep.replace('-', '_'))
                    except ImportError:
                        missing_deps.append(dep)

                if missing_deps:
                    result['issues'].append(f"缺少关键依赖: {', '.join(missing_deps)}")
                    result['status'] = 'fail'

            except Exception as e:
                result['issues'].append(f"依赖检查失败: {e}")
                result['status'] = 'fail'
        else:
            result['issues'].append("缺少requirements.txt文件")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        return result

    def unify_task_docs(self) -> Dict[str, Any]:
        """统一任务文档"""
        logger.info("统一任务文档...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        todo_file = self.paths['todo']
        deployment_docs_dir = self.paths['docs'] / 'deployment_progress'

        if not todo_file.exists():
            result['issues'].append("缺少根目录TODO.md文件")
            result['status'] = 'fail'
            self.issues.extend(result['issues'])
            return result

        # 读取TODO.md
        try:
            with open(todo_file, 'r', encoding='utf-8') as f:
                todo_content = f.read()

            # 解析任务
            tasks = self.parse_todo_content(todo_content)
            result['details']['total_tasks'] = len(tasks)

            # 检查部署进度文档
            progress_files = list(deployment_docs_dir.glob('*.md'))
            for progress_file in progress_files:
                if progress_file.name.startswith(('01-', '02-', '03-')):
                    try:
                        with open(progress_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 检查是否与TODO同步
                            if 'TODO.md' in content or '任务' in content:
                                result['details']['synced_docs'] = result['details'].get('synced_docs', 0) + 1
                    except Exception as e:
                        result['issues'].append(f"进度文档读取失败 {progress_file.name}: {e}")
                        result['status'] = 'fail'

        except Exception as e:
            result['issues'].append(f"TODO文档处理失败: {e}")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        return result

    def cleanup_stale_files(self) -> Dict[str, Any]:
        """清理沉积文件"""
        logger.info("清理沉积文件...")
        result = {'status': 'pass', 'details': {}, 'issues': []}

        # 定义需要清理的模式
        stale_patterns = [
            '*.pyc',
            '__pycache__',
            '*.log',
            'temp_*',
            '*.tmp'
        ]

        cleaned_files = []
        for pattern in stale_patterns:
            for path in self.project_root.rglob(pattern):
                if path.is_file():
                    try:
                        path.unlink()
                        cleaned_files.append(str(path.relative_to(self.project_root)))
                    except Exception as e:
                        result['issues'].append(f"清理失败 {path}: {e}")
                        result['status'] = 'fail'
                elif path.is_dir():
                    try:
                        shutil.rmtree(path)
                        cleaned_files.append(str(path.relative_to(self.project_root)))
                    except Exception as e:
                        result['issues'].append(f"清理失败 {path}: {e}")
                        result['status'] = 'fail'

        result['details']['cleaned_files'] = cleaned_files
        self.issues.extend(result['issues'])
        return result

    def parse_todo_content(self, content: str) -> List[Dict[str, Any]]:
        """解析TODO内容"""
        tasks = []
        lines = content.split('\n')
        current_task = None

        for line in lines:
            line = line.strip()
            if line.startswith('- ['):
                # 新任务
                if current_task:
                    tasks.append(current_task)

                completed = '[x]' in line
                title = line.split('] ', 1)[1] if '] ' in line else line
                current_task = {
                    'title': title,
                    'completed': completed,
                    'details': []
                }
            elif current_task and line.startswith('  '):
                # 任务详情
                current_task['details'].append(line.strip())

        if current_task:
            tasks.append(current_task)

        return tasks

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检查摘要"""
        summary = {
            'total_checks': len(results['checks']),
            'passed_checks': 0,
            'failed_checks': 0,
            'warning_checks': 0,
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

        summary['health_score'] = (summary['passed_checks'] / summary['total_checks']) * 100 if summary['total_checks'] > 0 else 0

        return summary

    def save_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """保存检查报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/health_report_{timestamp}.json"

        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"健康检查报告已保存到: {output_path}")
        return str(output_path)

    def auto_fix_issues(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """自动修复发现的问题"""
        logger.info("开始自动修复...")
        fixes = {'applied': [], 'failed': []}

        for issue in results['issues']:
            try:
                if '缺少必需路径' in issue:
                    # 创建缺失的目录
                    path_name = issue.split(': ')[1]
                    path = self.project_root / path_name
                    if not path.exists():
                        if '.' in path_name:
                            # 文件
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.touch()
                        else:
                            # 目录
                            path.mkdir(parents=True, exist_ok=True)
                        fixes['applied'].append(f"创建了 {path_name}")
                elif '缺少配置文件' in issue:
                    # 创建基础配置文件
                    config_path = issue.split(': ')[1]
                    path = self.project_root / config_path
                    if not path.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        base_config = {
                            "meta": {
                                "name": f"{path.parent.name} 配置",
                                "version": "1.0.0",
                                "createdAt": datetime.now().isoformat()
                            }
                        }
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(base_config, f, indent=2, ensure_ascii=False)
                        fixes['applied'].append(f"创建了配置文件 {config_path}")
            except Exception as e:
                fixes['failed'].append(f"修复失败 {issue}: {e}")

        return fixes

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AI弹窗项目健康监控系统')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--auto-fix', action='store_true', help='自动修复发现的问题')
    parser.add_argument('--quiet', action='store_true', help='静默模式')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    monitor = HealthMonitor(args.project_root)
    results = monitor.run_full_check()

    # 保存报告
    report_path = monitor.save_report(results, args.output)

    # 自动修复
    if args.auto_fix:
        fixes = monitor.auto_fix_issues(results)
        print(f"自动修复结果: {fixes}")

    # 输出摘要
    summary = results['summary']
    print(f"\n健康检查摘要:")
    print(f"总检查数: {summary['total_checks']}")
    print(f"通过: {summary['passed_checks']}")
    print(f"失败: {summary['failed_checks']}")
    print(f"警告: {summary['warning_checks']}")
    print(f"健康评分: {summary['health_score']:.1f}%")
    print(f"发现问题: {summary['total_issues']}")
    print(f"报告路径: {report_path}")

    # 返回退出码
    return 0 if summary['failed_checks'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
