#!/usr/bin/env python3
"""
配置加载器模块
负责加载和管理项目的所有配置文件
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, read_yaml, FileUtils

class ConfigLoader:
    """配置加载器"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent.parent)
        self.logger = get_script_logger('config_loader')

        # 配置文件的标准位置
        self.config_paths = {
            'project': self.project_root / 'project_config.json',
            'docs': self.project_root / 'docs' / 'docs_config.json',
            'scripts': self.project_root / 'scripts' / 'scripts_config.json',
            'rules_js': self.project_root / 'rules' / 'rules.config.js',
            'src': self.project_root / 'src' / 'src_config.json',
            'ai': self.project_root / 'src' / 'ai' / 'ai_config.json',
            'backend': self.project_root / 'src' / 'backend' / 'backend_config.json',
            'frontend': self.project_root / 'src' / 'frontend' / 'frontend_config.json',
            'processing': self.project_root / 'src' / 'processing' / 'processing_config.json',
            'integrations': self.project_root / 'src' / 'integrations' / 'integrations_config.json',
            'utils': self.project_root / 'src' / 'utils' / 'utils_config.json',
            'config': self.project_root / 'src' / 'config' / 'config_config.json'
        }

        # 缓存加载的配置
        self._config_cache = {}
        self._load_timestamp = None

        self.logger.info(f"配置加载器初始化完成，项目根目录: {self.project_root}")

    def load_all_configs(self) -> Dict[str, Any]:
        """加载所有配置文件"""
        self.logger.info("开始加载所有配置文件")

        results = {
            'timestamp': datetime.now().isoformat(),
            'configs': {},
            'summary': {}
        }

        loaded_count = 0
        failed_count = 0

        for config_name, config_path in self.config_paths.items():
            try:
                config_data = self.load_config(config_name)
                if config_data:
                    results['configs'][config_name] = {
                        'status': 'loaded',
                        'path': str(config_path),
                        'data': config_data
                    }
                    loaded_count += 1
                else:
                    results['configs'][config_name] = {
                        'status': 'failed',
                        'path': str(config_path),
                        'error': '加载失败'
                    }
                    failed_count += 1
            except Exception as e:
                results['configs'][config_name] = {
                    'status': 'error',
                    'path': str(config_path),
                    'error': str(e)
                }
                failed_count += 1
                self.logger.error(f"加载配置失败: {config_name}", {'error': str(e)})

        results['summary'] = {
            'total_configs': len(self.config_paths),
            'loaded_configs': loaded_count,
            'failed_configs': failed_count,
            'success_rate': (loaded_count / len(self.config_paths)) * 100 if self.config_paths else 0
        }

        self._load_timestamp = datetime.now()
        self.logger.info(f"配置加载完成: {loaded_count}成功, {failed_count}失败")
        return results

    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """加载指定配置文件"""
        if config_name not in self.config_paths:
            self.logger.warning(f"未知的配置文件: {config_name}")
            return None

        config_path = self.config_paths[config_name]

        # 检查缓存
        if config_name in self._config_cache:
            cache_time, cached_data = self._config_cache[config_name]
            # 如果文件未修改，使用缓存
            if config_path.exists() and config_path.stat().st_mtime <= cache_time.timestamp():
                return cached_data

        try:
            if not config_path.exists():
                self.logger.warning(f"配置文件不存在: {config_path}")
                return None

            # 根据文件扩展名选择加载方式
            if config_path.suffix == '.json':
                config_data = read_json(config_path)
            elif config_path.suffix == '.yaml' or config_path.suffix == '.yml':
                config_data = read_yaml(config_path)
            elif config_path.suffix == '.js':
                # 简单处理JS配置文件
                content = FileUtils.read_text(config_path)
                # 这里可以添加更复杂的JS解析逻辑
                config_data = {'content': content, 'type': 'javascript'}
            else:
                self.logger.warning(f"不支持的配置文件格式: {config_path}")
                return None

            # 验证配置基本结构
            if not self._validate_config_structure(config_name, config_data):
                self.logger.warning(f"配置结构验证失败: {config_name}")
                return None

            # 缓存配置
            self._config_cache[config_name] = (datetime.now(), config_data)

            self.logger.debug(f"配置加载成功: {config_name}")
            return config_data

        except Exception as e:
            self.logger.error(f"加载配置异常: {config_name}", {'error': str(e)})
            return None

    def get_config(self, config_name: str, key_path: Optional[str] = None) -> Any:
        """获取配置值"""
        config_data = self.load_config(config_name)
        if not config_data:
            return None

        if key_path:
            # 支持点分隔的键路径，如 "ui.theme.colors.primary"
            keys = key_path.split('.')
            current = config_data
            try:
                for key in keys:
                    current = current[key]
                return current
            except (KeyError, TypeError):
                self.logger.warning(f"配置键不存在: {config_name}.{key_path}")
                return None

        return config_data

    def reload_config(self, config_name: str) -> bool:
        """重新加载指定配置"""
        if config_name in self._config_cache:
            del self._config_cache[config_name]

        return self.load_config(config_name) is not None

    def reload_all_configs(self) -> Dict[str, Any]:
        """重新加载所有配置"""
        self._config_cache.clear()
        return self.load_all_configs()

    def list_available_configs(self) -> List[str]:
        """列出所有可用的配置文件"""
        return list(self.config_paths.keys())

    def get_config_info(self, config_name: str) -> Optional[Dict[str, Any]]:
        """获取配置文件的详细信息"""
        if config_name not in self.config_paths:
            return None

        config_path = self.config_paths[config_name]
        info = {
            'name': config_name,
            'path': str(config_path),
            'exists': config_path.exists(),
            'size': config_path.stat().st_size if config_path.exists() else 0,
            'modified': datetime.fromtimestamp(config_path.stat().st_mtime).isoformat() if config_path.exists() else None,
            'cached': config_name in self._config_cache
        }

        return info

    def validate_config_integrity(self) -> Dict[str, Any]:
        """验证配置完整性"""
        self.logger.info("开始验证配置完整性")

        results = {
            'timestamp': datetime.now().isoformat(),
            'validations': {},
            'issues': [],
            'summary': {}
        }

        for config_name in self.config_paths.keys():
            validation = self._validate_single_config(config_name)
            results['validations'][config_name] = validation

            if not validation['valid']:
                results['issues'].extend(validation['issues'])

        results['summary'] = {
            'total_configs': len(self.config_paths),
            'valid_configs': sum(1 for v in results['validations'].values() if v['valid']),
            'invalid_configs': sum(1 for v in results['validations'].values() if not v['valid']),
            'total_issues': len(results['issues'])
        }

        self.logger.info(f"配置完整性验证完成，发现问题: {len(results['issues'])}")
        return results

    def _validate_config_structure(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """验证配置基本结构"""
        if not isinstance(config_data, dict):
            return False

        # 检查必需的顶级字段
        required_fields = {
            'project': ['meta', 'project'],
            'docs': ['meta', 'structure'],
            'scripts': ['meta', 'structure'],
            'src': ['meta'],
            'ai': ['meta'],
            'backend': ['meta'],
            'frontend': ['meta', 'ui'],
            'processing': ['meta'],
            'integrations': ['meta'],
            'utils': ['meta'],
            'config': ['meta']
        }

        if config_name in required_fields:
            for field in required_fields[config_name]:
                if field not in config_data:
                    self.logger.warning(f"配置缺少必需字段: {config_name}.{field}")
                    return False

        return True

    def _validate_single_config(self, config_name: str) -> Dict[str, Any]:
        """验证单个配置文件"""
        result = {
            'config_name': config_name,
            'valid': True,
            'issues': [],
            'warnings': []
        }

        config_data = self.load_config(config_name)
        if not config_data:
            result['valid'] = False
            result['issues'].append(f"无法加载配置: {config_name}")
            return result

        # 结构验证
        if not self._validate_config_structure(config_name, config_data):
            result['valid'] = False
            result['issues'].append(f"配置结构无效: {config_name}")

        # 内容验证（根据配置类型）
        content_issues = self._validate_config_content(config_name, config_data)
        result['issues'].extend(content_issues)

        # 引用验证
        reference_issues = self._validate_config_references(config_name, config_data)
        result['warnings'].extend(reference_issues)

        return result

    def _validate_config_content(self, config_name: str, config_data: Dict[str, Any]) -> List[str]:
        """验证配置内容"""
        issues = []

        # 项目配置验证
        if config_name == 'project':
            if 'subprojects' in config_data:
                subprojects = config_data['subprojects']
                for sub_name, sub_info in subprojects.items():
                    if not isinstance(sub_info, dict):
                        issues.append(f"子项目配置格式错误: {sub_name}")

        # 前端配置验证
        elif config_name == 'frontend':
            ui_config = config_data.get('ui', {})
            if 'window' not in ui_config:
                issues.append("前端配置缺少窗口设置")

        return issues

    def _validate_config_references(self, config_name: str, config_data: Dict[str, Any]) -> List[str]:
        """验证配置引用"""
        warnings = []

        # 检查路径引用
        if 'paths' in config_data:
            paths = config_data['paths']
            for path_key, path_value in paths.items():
                if isinstance(path_value, str) and not Path(path_value).exists():
                    warnings.append(f"引用的路径不存在: {path_key} -> {path_value}")

        return warnings

    def export_config_summary(self, output_path: Optional[str] = None) -> str:
        """导出配置摘要"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"logs/config_summary_{timestamp}.json"

        summary = {
            'export_time': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'configs': {}
        }

        for config_name in self.config_paths.keys():
            info = self.get_config_info(config_name)
            if info:
                summary['configs'][config_name] = info

        # 保存到文件
        output_file = self.project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.logger.info(f"配置摘要已导出到: {output_file}")
        return str(output_file)

# 便捷函数
def load_project_config() -> Optional[Dict[str, Any]]:
    """加载项目主配置"""
    loader = ConfigLoader()
    return loader.load_config('project')

def get_config_value(config_name: str, key_path: str) -> Any:
    """获取配置值"""
    loader = ConfigLoader()
    return loader.get_config(config_name, key_path)
