#!/usr/bin/env python3
"""
部署系统配置工具
提供配置加载和验证功能
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent.parent.parent
        self._configs: Dict[str, Any] = {}
    
    def load(self, filename: str) -> Dict[str, Any]:
        """加载配置文件"""
        if filename in self._configs:
            return self._configs[filename]
        
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            self._configs[filename] = {}
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._configs[filename] = config
                return config
        except Exception as e:
            print(f"加载配置文件失败 {filename}: {e}")
            self._configs[filename] = {}
            return {}
    
    def load_all(self, filenames: List[str]) -> Dict[str, Any]:
        """加载多个配置文件"""
        result = {}
        for filename in filenames:
            result[filename] = self.load(filename)
        return result
    
    def get(self, filename: str, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.load(filename)
        
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_required(config: Dict[str, Any], required_keys: List[str]) -> List[str]:
        """验证必需键"""
        missing = []
        for key in required_keys:
            if key not in config:
                missing.append(key)
        return missing
    
    @staticmethod
    def validate_types(config: Dict[str, Any], type_spec: Dict[str, type]) -> List[str]:
        """验证类型"""
        errors = []
        for key, expected_type in type_spec.items():
            if key in config and config[key] is not None:
                if not isinstance(config[key], expected_type):
                    errors.append(f"{key} 应该是 {expected_type.__name__} 类型")
        return errors
    
    @staticmethod
    def validate_path(config: Dict[str, Any], path_keys: List[str]) -> List[str]:
        """验证路径是否存在"""
        errors = []
        for key in path_keys:
            if key in config:
                path = Path(config[key])
                if not path.exists():
                    errors.append(f"路径不存在: {config[key]}")
        return errors
    
    @staticmethod
    def validate_version(config: Dict[str, Any], version_key: str, min_version: str) -> List[str]:
        """验证版本号"""
        errors = []
        if version_key in config:
            current = config[version_key]
            if not ConfigValidator._compare_versions(current, min_version):
                errors.append(f"版本 {current} 低于最低要求 {min_version}")
        return errors
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> bool:
        """比较版本号"""
        parts1 = [int(p) for p in v1.split('.')]
        parts2 = [int(p) for p in v2.split('.')]
        
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return True
            elif p1 < p2:
                return False
        
        return True  # 相等


@dataclass
class DeployConfigData:
    """部署配置数据类"""
    environment: str = "development"
    max_retries: int = 3
    retry_delay: int = 5
    timeout: int = 300
    venv_name: str = "ai_popup_env"
    logs_path: str = "./logs"
    data_path: str = "./data"
    assets_path: str = "./assets"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeployConfigData':
        """从字典创建"""
        return cls(
            environment=data.get("environment", "development"),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 5),
            timeout=data.get("timeout", 300),
            venv_name=data.get("venv_name", "ai_popup_env"),
            logs_path=data.get("logs_path", "./logs"),
            data_path=data.get("data_path", "./data"),
            assets_path=data.get("assets_path", "./assets")
        )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_loader = ConfigLoader(self.project_root)
    
    def get_project_config(self) -> Dict[str, Any]:
        """获取项目配置"""
        return self.config_loader.load("project_config.json")
    
    def get_scripts_config(self) -> Dict[str, Any]:
        """获取脚本配置"""
        return self.config_loader.load("scripts/scripts_config.json")
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web配置"""
        return self.config_loader.load("web/web_config.json")
    
    def get_deploy_config(self) -> DeployConfigData:
        """获取部署配置"""
        project_config = self.get_project_config()
        deployment = project_config.get("deployment", {})
        return DeployConfigData.from_dict(deployment)
    
    def validate_all(self) -> Dict[str, Any]:
        """验证所有配置"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "overall_status": "valid"
        }
        
        # 验证项目配置
        project_config = self.get_project_config()
        required_paths = project_config.get("validation", {}).get("requiredPaths", [])
        missing = ConfigValidator.validate_path(project_config, required_paths)
        
        results["validations"]["project_config"] = {
            "status": "valid" if not missing else "invalid",
            "missing_paths": missing
        }
        
        if missing:
            results["overall_status"] = "invalid"
        
        return results


# 导出
__all__ = [
    'ConfigLoader',
    'ConfigValidator',
    'DeployConfigData',
    'ConfigManager'
]

