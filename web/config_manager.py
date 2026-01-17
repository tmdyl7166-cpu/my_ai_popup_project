"""
Config Manager
配置管理器 - 负责项目配置的读取、更新和管理
"""
import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_cache = {}
        self.config_files = {
            'project': 'project_config.json',
            'frontend': 'src/frontend/frontend_config.json',
            'backend': 'src/backend/backend_config.json',
            'scripts': 'scripts/scripts_config.json',
            'src': 'src/src_config.json',
            'web': 'web/web_config.json'
        }

    def get_component_config(self, component: str) -> Dict[str, Any]:
        """获取组件配置"""
        # Check cache first
        if component in self.config_cache:
            return self.config_cache[component]

        config_path = self._get_config_path(component)
        if not config_path:
            return {'error': f'组件 {component} 配置不存在'}

        try:
            config = self._load_config(config_path)
            self.config_cache[component] = config
            return config
        except Exception as e:
            logger.error(f'加载配置失败 {component}: {e}')
            return {'error': str(e)}

    def update_component_config(self, component: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新组件配置"""
        config_path = self._get_config_path(component)
        if not config_path:
            return {'status': 'error', 'message': f'组件 {component} 配置不存在'}

        try:
            # Validate config structure
            self._validate_config(config)

            # Write config to file
            self._save_config(config_path, config)

            # Update cache
            self.config_cache[component] = config

            logger.info(f'配置已更新: {component}')
            return {'status': 'success', 'message': f'{component} 配置已更新'}
        except Exception as e:
            logger.error(f'更新配置失败 {component}: {e}')
            return {'status': 'error', 'message': str(e)}

    def _get_config_path(self, component: str) -> Optional[Path]:
        """获取配置文件路径"""
        if component in self.config_files:
            config_name = self.config_files[component]
            config_path = self.project_root / config_name

            # Also check in config subdirectory
            if not config_path.exists():
                config_path = self.project_root / 'docs' / 'config' / config_name

            if config_path.exists():
                return config_path

        return None

    def _load_config(self, path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.suffix in ('.yaml', '.yml'):
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f'不支持的配置文件格式: {path.suffix}')

    def _save_config(self, path: Path, config: Dict[str, Any]):
        """保存配置文件"""
        # Create backup
        if path.exists():
            backup_path = path.with_suffix(path.suffix + '.bak')
            path.replace(backup_path)

        # Write new config
        if path.suffix == '.json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        elif path.suffix in ('.yaml', '.yml'):
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f'不支持的配置文件格式: {path.suffix}')

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置结构"""
        if not isinstance(config, dict):
            raise ValueError('配置必须是字典类型')

        # 可以添加更详细的验证逻辑
        return True

    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有组件配置"""
        configs = {}
        for component in self.config_files:
            config = self.get_component_config(component)
            if 'error' not in config:
                configs[component] = config
        return configs

    def reload_config(self, component: str) -> Dict[str, Any]:
        """重新加载配置（清除缓存）"""
        if component in self.config_cache:
            del self.config_cache[component]
        return self.get_component_config(component)

    def clear_cache(self):
        """清除所有缓存"""
        self.config_cache.clear()

    def compare_configs(self, component1: str, component2: str) -> Dict[str, Any]:
        """比较两个配置"""
        config1 = self.get_component_config(component1)
        config2 = self.get_component_config(component2)

        return {
            'component1': {
                'name': component1,
                'config': config1
            },
            'component2': {
                'name': component2,
                'config': config2
            },
            'are_equal': config1 == config2
        }

