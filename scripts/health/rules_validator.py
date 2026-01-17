"""
规则验证器
专门负责验证规则系统的完整性和一致性
"""
from pathlib import Path
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class RulesValidator:
    """规则验证器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def validate_rules(self) -> Dict[str, Any]:
        """验证规则系统"""
        logger.info("验证规则系统...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        rules_dir = self.project_root / 'rules'
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

        logger.info(f"规则验证完成，发现 {len(result['issues'])} 个问题")
        return result
