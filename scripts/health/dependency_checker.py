"""
依赖检查器
专门负责检查项目依赖状态
"""
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DependencyChecker:
    """依赖检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖状态"""
        logger.info("检查依赖状态...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

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

        logger.info(f"依赖检查完成，发现 {len(result['issues'])} 个问题")
        return result
