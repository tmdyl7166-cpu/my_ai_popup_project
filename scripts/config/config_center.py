#!/usr/bin/env python3
"""
统一配置调度中心
负责所有JSON配置的加载、验证、热更新和调度

遵循规则：
- 所有配置通过JSON格式定义
- 配置变更自动触发相关模块更新
- 支持配置版本控制和回滚
- 提供统一的配置访问接口
"""

import os
import json
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConfigChangeType(Enum):
    """配置变更类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELOAD = "reload"


@dataclass
class ConfigInfo:
    """配置信息"""
    name: str
    path: str
    version: str
    last_modified: datetime
    checksum: str
    change_type: ConfigChangeType = ConfigChangeType.UPDATE


@dataclass
class ConfigChange:
    """配置变更记录"""
    config_name: str
    change_type: ConfigChangeType
    old_version: str
    new_version: str
    timestamp: datetime
    checksum_before: str
    checksum_after: str
    triggered_modules: List[str] = field(default_factory=list)


class ConfigDispatcher:
    """
    统一配置调度中心
    管理所有项目配置，提供配置变更通知和自动更新
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.project_root = Path(__file__).parent.parent.parent
        
        # 配置缓存
        self._configs: Dict[str, Dict] = {}
        self._config_info: Dict[str, ConfigInfo] = {}
        
        # 变更历史
        self._change_history: List[ConfigChange] = []
        
        # 订阅者管理
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # 监听器
        self._file_watchers: Dict[str, float] = {}
        self._watch_interval = 5.0  # 秒
        self._watch_thread = None
        self._watching = False
        
        # 配置规则引用
        self._rules_reference = {
            "L1": self.project_root / "rules" / "L1-meta-goal.json",
            "L2": self.project_root / "rules" / "L2-understanding.json",
            "L3": self.project_root / "rules" / "L3-constraints.json",
            "L4": self.project_root / "rules" / "L4-decisions.json",
            "L5": self.project_root / "rules" / "L5-execution.json"
        }
        
        # 默认配置列表
        self._default_configs = [
            # 核心配置
            {"name": "project", "path": "project_config.json"},
            {"name": "api_config", "path": "api/config/api_config.json"},
            {"name": "web_config", "path": "web/web_config.json"},
            {"name": "scripts_config", "path": "scripts/scripts_config.json"},
            {"name": "assets_config", "path": "assets/assets_config.json"},
            {"name": "src_config", "path": "src/src_config.json"},
            
            # 重构版配置
            {"name": "web_config_refactor", "path": "web/web_config_refactor.json"},
            {"name": "scripts_config_refactor", "path": "scripts/scripts_config_refactor.json"},
            {"name": "src_config_refactor", "path": "src/src_config_refactor.json"},
            
            # 映射配置
            {"name": "api_mapping", "path": "api/mapping/api_mapping.json"},
            
            # src子模块配置
            {"name": "ai_config", "path": "src/ai/ai_config.json"},
            {"name": "backend_config", "path": "src/backend/backend_config.json"},
            {"name": "frontend_config", "path": "src/frontend/frontend_config.json"},
            {"name": "integrations_config", "path": "src/integrations/integrations_config.json"},
            {"name": "processing_config", "path": "src/processing/processing_config.json"},
            {"name": "utils_config", "path": "src/utils/utils_config.json"},
        ]
        
        # 加载所有配置
        self._load_all_configs()
        
        # 启动文件监控
        self._start_watching()
        
        logger.info("配置调度中心初始化完成")
    
    def _calculate_checksum(self, content: str) -> str:
        """计算内容校验和"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _calculate_dict_checksum(self, data: Dict) -> str:
        """计算字典数据校验和"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return self._calculate_checksum(content)
    
    def _load_config(self, config_path: Path) -> Optional[Dict]:
        """加载单个配置文件"""
        try:
            if not config_path.exists():
                logger.warning(f"配置文件不存在: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON解析错误: {config_path}, {e}")
            return None
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_path}, {e}")
            return None
    
    def _load_all_configs(self):
        """加载所有默认配置"""
        logger.info("加载所有配置文件...")
        
        for config_def in self._default_configs:
            config_name = config_def["name"]
            config_rel_path = config_def["path"]
            config_path = self.project_root / config_rel_path
            
            data = self._load_config(config_path)
            if data is not None:
                # 计算校验和
                checksum = self._calculate_dict_checksum(data)
                
                # 获取修改时间
                try:
                    last_modified = datetime.fromtimestamp(config_path.stat().st_mtime)
                except:
                    last_modified = datetime.now()
                
                # 创建配置信息
                info = ConfigInfo(
                    name=config_name,
                    path=str(config_path),
                    version=self._get_version(data),
                    last_modified=last_modified,
                    checksum=checksum
                )
                
                self._configs[config_name] = data
                self._config_info[config_name] = info
                
                logger.debug(f"已加载配置: {config_name} (v{info.version})")
        
        logger.info(f"共加载 {len(self._configs)} 个配置文件")
    
    def _get_version(self, data: Dict) -> str:
        """从配置数据中获取版本号"""
        if "meta" in data and "version" in data["meta"]:
            return data["meta"]["version"]
        elif "version" in data:
            return str(data["version"])
        else:
            return "1.0.0"
    
    def get(self, config_name: str, default: Any = None) -> Any:
        """获取配置"""
        return self._configs.get(config_name, default)
    
    def get_all(self) -> Dict[str, Dict]:
        """获取所有配置"""
        return self._configs.copy()
    
    def get_info(self, config_name: str) -> Optional[ConfigInfo]:
        """获取配置信息"""
        return self._config_info.get(config_name)
    
    def get_all_info(self) -> Dict[str, ConfigInfo]:
        """获取所有配置信息"""
        return self._config_info.copy()
    
    def set(self, config_name: str, data: Dict, save: bool = True):
        """设置配置"""
        # 验证数据
        if not isinstance(data, dict):
            raise ValueError("配置数据必须是字典类型")
        
        # 计算新的校验和
        new_checksum = self._calculate_dict_checksum(data)
        
        # 获取旧的配置信息
        old_info = self._config_info.get(config_name)
        old_checksum = old_info.checksum if old_info else ""
        
        # 保存配置
        self._configs[config_name] = data
        
        # 更新配置信息
        info = ConfigInfo(
            name=config_name,
            path=old_info.path if old_info else "",
            version=self._get_version(data),
            last_modified=datetime.now(),
            checksum=new_checksum
        )
        self._config_info[config_name] = info
        
        # 如果需要保存到文件
        if save and old_info and old_info.path:
            self._save_to_file(config_name, data, old_info.path)
        
        # 创建变更记录
        change = ConfigChange(
            config_name=config_name,
            change_type=ConfigChangeType.UPDATE,
            old_version=old_info.version if old_info else "1.0.0",
            new_version=info.version,
            timestamp=datetime.now(),
            checksum_before=old_checksum,
            checksum_after=new_checksum
        )
        self._change_history.append(change)
        
        # 通知订阅者
        self._notify_subscribers(config_name, ConfigChangeType.UPDATE, data)
        
        logger.info(f"配置已更新: {config_name}")
    
    def _save_to_file(self, config_name: str, data: Dict, path: str):
        """保存配置到文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug(f"配置已保存: {path}")
        except Exception as e:
            logger.error(f"保存配置失败: {path}, {e}")
    
    def reload(self, config_name: str) -> bool:
        """重新加载配置"""
        info = self._config_info.get(config_name)
        if not info:
            logger.warning(f"配置不存在: {config_name}")
            return False
        
        data = self._load_config(Path(info.path))
        if data is None:
            return False
        
        # 保存旧版本信息
        old_version = info.version
        old_checksum = info.checksum
        
        # 重新加载
        self._configs[config_name] = data
        new_checksum = self._calculate_dict_checksum(data)
        
        # 更新配置信息
        info.version = self._get_version(data)
        info.last_modified = datetime.now()
        info.checksum = new_checksum
        
        # 创建变更记录
        change = ConfigChange(
            config_name=config_name,
            change_type=ConfigChangeType.RELOAD,
            old_version=old_version,
            new_version=info.version,
            timestamp=datetime.now(),
            checksum_before=old_checksum,
            checksum_after=new_checksum
        )
        self._change_history.append(change)
        
        # 通知订阅者
        self._notify_subscribers(config_name, ConfigChangeType.RELOAD, data)
        
        logger.info(f"配置已重新加载: {config_name}")
        return True
    
    def reload_all(self):
        """重新加载所有配置"""
        for config_name in list(self._configs.keys()):
            self.reload(config_name)
    
    def subscribe(self, config_name: str, callback: Callable):
        """订阅配置变更"""
        if config_name not in self._subscribers:
            self._subscribers[config_name] = []
        self._subscribers[config_name].append(callback)
    
    def unsubscribe(self, config_name: str, callback: Callable):
        """取消订阅"""
        if config_name in self._subscribers:
            try:
                self._subscribers[config_name].remove(callback)
            except ValueError:
                pass
    
    def _notify_subscribers(self, config_name: str, change_type: ConfigChangeType, data: Dict):
        """通知订阅者"""
        if config_name in self._subscribers:
            for callback in self._subscribers[config_name]:
                try:
                    callback(config_name, change_type, data)
                except Exception as e:
                    logger.error(f"配置变更通知失败: {e}")
    
    def _start_watching(self):
        """启动文件监控"""
        if self._watching:
            return
        
        self._watching = True
        self._watch_thread = threading.Thread(target=self._watch_files, daemon=True)
        self._watch_thread.start()
        logger.info("配置文件监控已启动")
    
    def _watch_files(self):
        """监控文件变化"""
        while self._watching:
            try:
                for config_name, info in self._config_info.items():
                    config_path = Path(info.path)
                    if config_path.exists():
                        mtime = config_path.stat().st_mtime
                        last_mtime = self._file_watchers.get(config_name, 0)
                        
                        if mtime > last_mtime:
                            self._file_watchers[config_name] = mtime
                            
                            # 检测到文件变化，重新加载
                            logger.info(f"检测到配置文件变化: {config_name}")
                            self.reload(config_name)
            except Exception as e:
                logger.error(f"文件监控错误: {e}")
            
            time.sleep(self._watch_interval)
    
    def stop_watching(self):
        """停止文件监控"""
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=5)
        logger.info("配置文件监控已停止")
    
    def get_change_history(self, config_name: Optional[str] = None, 
                          limit: int = 100) -> List[ConfigChange]:
        """获取配置变更历史"""
        if config_name:
            changes = [c for c in self._change_history if c.config_name == config_name]
        else:
            changes = self._change_history
        
        return changes[-limit:]
    
    def validate(self, config_name: str, schema: Optional[Dict] = None) -> Dict:
        """验证配置"""
        data = self._configs.get(config_name)
        if not data:
            return {
                "valid": False,
                "error": f"配置不存在: {config_name}"
            }
        
        # 基础验证
        if "meta" not in data:
            return {
                "valid": False,
                "error": "配置缺少meta字段"
            }
        
        if "version" not in data["meta"]:
            return {
                "valid": False,
                "error": "配置缺少version字段"
            }
        
        return {
            "valid": True,
            "config_name": config_name,
            "version": data["meta"]["version"],
            "checksum": self._config_info[config_name].checksum
        }
    
    def get_rules_compliance(self) -> Dict:
        """获取规则符合度"""
        compliance = {}
        
        for rule_name, rule_path in self._rules_reference.items():
            if rule_path.exists():
                rule_data = self._load_config(rule_path)
                if rule_data:
                    # 检查规则中定义的配置是否已实现
                    required_configs = self._extract_required_configs(rule_data)
                    implemented = []
                    missing = []
                    
                    for req_config in required_configs:
                        if req_config in self._configs:
                            implemented.append(req_config)
                        else:
                            missing.append(req_config)
                    
                    compliance[rule_name] = {
                        "implemented": len(implemented),
                        "missing": len(missing),
                        "missing_configs": missing,
                        "compliance_rate": len(implemented) / max(len(required_configs), 1) * 100
                    }
            else:
                compliance[rule_name] = {
                    "error": f"规则文件不存在: {rule_path}"
                }
        
        return compliance
    
    def _extract_required_configs(self, rule_data: Dict) -> List[str]:
        """从规则数据中提取需要的配置列表"""
        configs = []
        
        # 递归提取
        def extract(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.endswith("_config") or key.endswith("Config"):
                        if isinstance(value, str):
                            configs.append(value)
                        elif isinstance(value, dict) and "path" in value:
                            path = value["path"]
                            if isinstance(path, str):
                                configs.append(path.split("/")[-1].replace(".json", ""))
                    extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item)
        
        extract(rule_data)
        return list(set(configs))
    
    def export(self, config_names: Optional[List[str]] = None) -> Dict:
        """导出配置"""
        if config_names is None:
            config_names = list(self._configs.keys())
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "configs": {}
        }
        
        for name in config_names:
            if name in self._configs:
                export_data["configs"][name] = {
                    "data": self._configs[name],
                    "info": {
                        "version": self._config_info[name].version,
                        "last_modified": self._config_info[name].last_modified.isoformat(),
                        "checksum": self._config_info[name].checksum
                    }
                }
        
        return export_data
    
    def destroy(self):
        """销毁配置调度中心"""
        self.stop_watching()
        self._configs.clear()
        self._config_info.clear()
        self._subscribers.clear()
        self._change_history.clear()
        logger.info("配置调度中心已销毁")


# 全局单例
_config_dispatcher = None


def get_config_dispatcher() -> ConfigDispatcher:
    """获取配置调度中心单例"""
    global _config_dispatcher
    if _config_dispatcher is None:
        _config_dispatcher = ConfigDispatcher()
    return _config_dispatcher


def init_config_dispatcher() -> ConfigDispatcher:
    """初始化配置调度中心"""
    return get_config_dispatcher()


if __name__ == "__main__":
    # 测试配置调度中心
    logging.basicConfig(level=logging.INFO)
    
    dispatcher = init_config_dispatcher()
    
    # 获取项目配置
    project_config = dispatcher.get("project")
    print(f"项目配置: {project_config['project']['name'] if project_config else 'N/A'}")
    
    # 获取规则符合度
    compliance = dispatcher.get_rules_compliance()
    print(f"规则符合度: {json.dumps(compliance, indent=2, ensure_ascii=False)}")
    
    # 订阅配置变更
    def on_config_change(name, change_type, data):
        print(f"配置变更: {name} - {change_type.value}")
    
    dispatcher.subscribe("project", on_config_change)
    
    # 模拟配置更新
    if project_config:
        project_config["project"]["status"] = "testing"
        dispatcher.set("project", project_config)

