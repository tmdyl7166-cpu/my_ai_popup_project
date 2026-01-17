"""
文档同步检查器
专门负责检查文档同步状态和更新情况
"""
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DocsSyncChecker:
    """文档同步检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def check_docs_sync(self) -> Dict[str, Any]:
        """检查文档同步状态"""
        logger.info("检查文档同步状态...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        docs_dir = self.project_root / 'docs'

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

        all_docs = required_docs + project_docs + deployment_docs

        for doc in all_docs:
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

        result['details']['checked_docs'] = len(all_docs)
        logger.info(f"文档同步检查完成，发现 {len(result['issues'])} 个问题")
        return result
