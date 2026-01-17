"""
文件清理工具
专门负责清理项目中的沉积文件和临时文件
"""
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FileCleanupUtil:
    """文件清理工具"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def cleanup_stale_files(self) -> Dict[str, Any]:
        """清理沉积文件"""
        logger.info("清理沉积文件...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        # 定义需要清理的文件模式
        cleanup_patterns = [
            '*.tmp',
            '*.log',
            '*.pyc',
            '__pycache__',
            '.DS_Store',
            'Thumbs.db'
        ]

        total_cleaned = 0
        now = datetime.now()

        # 清理日志文件（超过7天的）
        logs_dir = self.project_root / 'logs'
        if logs_dir.exists():
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < (now.timestamp() - 7*24*3600):
                    try:
                        log_file.unlink()
                        total_cleaned += 1
                    except Exception as e:
                        result['issues'].append(f"清理日志文件失败 {log_file.name}: {e}")
                        result['status'] = 'fail'

        # 清理临时文件
        for pattern in cleanup_patterns:
            for file_path in self.project_root.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        total_cleaned += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        total_cleaned += 1
                except Exception as e:
                    result['issues'].append(f"清理文件失败 {file_path}: {e}")
                    result['status'] = 'fail'

        result['details']['files_cleaned'] = total_cleaned
        logger.info(f"文件清理完成，清理了 {total_cleaned} 个文件")
        return result
