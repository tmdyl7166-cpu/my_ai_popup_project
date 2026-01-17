"""
项目结构检查器
专门负责检查项目结构完整性
"""
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ProjectStructureChecker:
    """项目结构检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.required_structure = {
            'dirs': [
                'src', 'docs', 'assets', 'rules', 'logs', 'scripts',
                'src/ai', 'src/backend', 'src/frontend', 'src/processing',
                'src/integrations', 'src/utils', 'src/config',
                'docs/project_docs', 'docs/deployment_progress',
                'assets/models', 'assets/images', 'assets/videos',
                'scripts/health', 'scripts/utils', 'scripts/core'
            ],
            'files': [
                'project_config.json', 'requirements.txt', 'README.md',
                'TODO.md', 'start.sh', 'verify_paths.py',
                'src/main.py', 'src/__init__.py',
                'rules/L1-meta-goal.json', 'rules/L2-understanding.json',
                'rules/L3-constraints.json', 'rules/L4-decisions.json',
                'rules/L5-execution.json'
            ]
        }

    def check_structure(self) -> Dict[str, Any]:
        """检查项目结构"""
        logger.info("检查项目结构...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        # 检查必需目录
        missing_dirs = []
        for dir_path in self.required_structure['dirs']:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                result['status'] = 'fail'

        # 检查必需文件
        missing_files = []
        for file_path in self.required_structure['files']:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                result['status'] = 'fail'

        result['details'] = {
            'missing_dirs': missing_dirs,
            'missing_files': missing_files,
            'total_dirs_checked': len(self.required_structure['dirs']),
            'total_files_checked': len(self.required_structure['files'])
        }

        if missing_dirs:
            result['issues'].extend([f"缺少目录: {d}" for d in missing_dirs])
        if missing_files:
            result['issues'].extend([f"缺少文件: {f}" for f in missing_files])

        logger.info(f"项目结构检查完成，发现 {len(result['issues'])} 个问题")
        return result
