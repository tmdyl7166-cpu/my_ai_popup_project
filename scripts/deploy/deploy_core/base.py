#!/usr/bin/env python3
"""
部署系统核心基类
定义部署模块的抽象基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from deploy_core import DeployContext, DeployStatus


class BaseDeployModule(ABC):
    """部署模块基类"""
    
    def __init__(self, name: str, context: DeployContext):
        self.name = name
        self.context = context
        self._logger = None
        self._config = None
    
    @property
    def logger(self):
        """获取日志记录器"""
        if self._logger is None:
            import logging
            self._logger = logging.getLogger(f"deploy.{self.name}")
        return self._logger
    
    @property
    def config(self):
        """获取配置"""
        if self._config is None:
            from deploy_utils.config import DeployConfig
            self._config = DeployConfig()
        return self._config
    
    @abstractmethod
    def check_prerequisites(self) -> bool:
        """检查前置条件
        
        Returns:
            bool: 前置条件是否满足
        """
        pass
    
    @abstractmethod
    def execute(self) -> bool:
        """执行部署
        
        Returns:
            bool: 是否执行成功
        """
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """回滚部署
        
        Returns:
            bool: 是否回滚成功
        """
        pass
    
    def run(self) -> bool:
        """运行完整的部署流程
        
        Returns:
            bool: 是否成功完成部署
        """
        self.context.add_step(self.name, "running", "开始执行")
        self.logger.info(f"开始执行模块: {self.name}")
        
        # 检查前置条件
        if not self.check_prerequisites():
            self.context.add_step(self.name, "failed", "前置条件检查失败")
            self.logger.error(f"模块 {self.name} 前置条件检查失败")
            return False
        
        # 执行部署
        try:
            if self.execute():
                self.context.add_step(self.name, "success", "执行成功")
                self.logger.info(f"模块 {self.name} 执行成功")
                return True
            else:
                self.context.add_step(self.name, "failed", "执行返回失败")
                self.logger.error(f"模块 {self.name} 执行返回失败")
                # 尝试回滚
                return self._try_rollback()
        except Exception as e:
            self.context.add_step(self.name, "failed", f"执行异常: {str(e)}")
            self.logger.exception(f"模块 {self.name} 执行异常")
            # 尝试回滚
            return self._try_rollback()
    
    def _try_rollback(self) -> bool:
        """尝试回滚"""
        self.context.add_step(self.name, "rolling_back", "正在回滚")
        self.logger.info(f"正在回滚模块: {self.name}")
        
        if self.rollback():
            self.context.add_step(self.name, "rolled_back", "回滚成功")
            self.logger.info(f"模块 {self.name} 回滚成功")
            return False  # 虽然回滚成功，但整体失败
        else:
            self.context.add_step(self.name, "failed", "回滚失败")
            self.logger.error(f"模块 {self.name} 回滚失败")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取模块状态"""
        return {
            "name": self.name,
            "status": self.context.status.value,
            "steps": self.context.steps
        }


class DeployStep:
    """部署步骤"""
    
    def __init__(self, name: str, description: str = "", timeout: int = 300):
        self.name = name
        self.description = description
        self.timeout = timeout
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = "pending"
        self.message = ""
        self.result: Optional[Dict[str, Any]] = None
    
    def __enter__(self):
        """进入步骤上下文"""
        self.start_time = datetime.now()
        self.status = "running"
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出步骤上下文"""
        self.end_time = datetime.now()
        if exc_type is None:
            self.status = "success"
        else:
            self.status = "failed"
            self.message = str(exc_val)
        return False  # 不抑制异常
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "timeout": self.timeout,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "message": self.message,
            "result": self.result
        }


class ModuleRegistry:
    """模块注册表"""
    
    _instance = None
    _modules: Dict[str, BaseDeployModule] = {}
    
    @classmethod
    def get_instance(cls):
        """获取单例"""
        if cls._instance is None:
            cls._instance = ModuleRegistry()
        return cls._instance
    
    @classmethod
    def register(cls, module: BaseDeployModule):
        """注册模块"""
        instance = cls.get_instance()
        instance._modules[module.name] = module
        return module
    
    @classmethod
    def get(cls, name: str) -> Optional[BaseDeployModule]:
        """获取模块"""
        instance = cls.get_instance()
        return instance._modules.get(name)
    
    @classmethod
    def list_all(cls) -> List[str]:
        """列出所有模块"""
        instance = cls.get_instance()
        return list(instance._modules.keys())
    
    @classmethod
    def clear(cls):
        """清空注册表"""
        instance = cls.get_instance()
        instance._modules.clear()


def create_module(name: str, context: DeployContext) -> BaseDeployModule:
    """工厂方法：创建部署模块
    
    Args:
        name: 模块名称
        context: 部署上下文
        
    Returns:
        BaseDeployModule: 部署模块实例
    """
    from deploy_modules.setup_env import SetupEnvModule
    from deploy_modules.install_deps import InstallDepsModule
    from deploy_modules.build_app import BuildAppModule
    from deploy_modules.deploy_app import DeployAppModule
    from deploy_modules.health_check import HealthCheckModule
    
    modules = {
        "setup_env": SetupEnvModule,
        "install_deps": InstallDepsModule,
        "build_app": BuildAppModule,
        "deploy_app": DeployAppModule,
        "health_check": HealthCheckModule
    }
    
    if name in modules:
        return modules[name](context)
    
    raise ValueError(f"未知模块: {name}")

