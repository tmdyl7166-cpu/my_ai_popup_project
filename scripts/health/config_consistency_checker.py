"""
配置一致性检查器
专门负责检查项目配置的一致性和完整性
"""
from pathlib import Path
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)

class ConfigConsistencyChecker:
    """配置一致性检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_cache = {}

    def check_consistency(self) -> Dict[str, Any]:
        """检查配置一致性"""
        logger.info("检查配置一致性...")
        result = {
            'status': 'pass',
            'details': {},
            'issues': []
        }

        # 加载主要配置
        configs = self._load_configs()
        result['details']['loaded_configs'] = list(configs.keys())

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

        logger.info(f"配置一致性检查完成，发现 {len(result['issues'])} 个问题")
        return result

    def _load_configs(self) -> Dict[str, Any]:
        """加载配置"""
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
                    logger.warning(f"配置加载失败 {config_file}: {e}")

        return configs
