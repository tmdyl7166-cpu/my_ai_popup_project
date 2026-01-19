"""
部署监控器
负责部署进度和文档管理
"""
from pathlib import Path
from typing import Dict, Any

class DeploymentMonitor:
    """部署监控器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_deployment_progress(self) -> Dict[str, Any]:
        """获取部署进度"""
        progress_file = self.project_root / 'docs' / 'deployment_progress' / '03-current-deployment-progress.md'
        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'status': 'success', 'content': content}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        return {'status': 'not_found', 'message': '部署进度文件不存在'}
