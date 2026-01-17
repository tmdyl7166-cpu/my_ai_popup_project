"""
任务文档统一器
专门负责统一和管理任务文档
"""
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class TaskDocsUnifier:
    """任务文档统一器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def unify_task_docs(self) -> Dict[str, Any]:
        """统一任务文档"""
        logger.info("统一任务文档...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        todo_file = self.project_root / 'TODO.md'
        deployment_docs_dir = self.project_root / 'docs' / 'deployment_progress'

        if not todo_file.exists():
            result['issues'].append("缺少根目录TODO.md文件")
            result['status'] = 'fail'
            logger.warning("TODO.md文件不存在")
            return result

        # 读取TODO.md
        try:
            with open(todo_file, 'r', encoding='utf-8') as f:
                todo_content = f.read()

            # 解析任务
            tasks = self._parse_todo_content(todo_content)
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

        logger.info(f"任务文档统一完成，发现 {len(result['issues'])} 个问题")
        return result

    def _parse_todo_content(self, content: str) -> List[Dict[str, Any]]:
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
