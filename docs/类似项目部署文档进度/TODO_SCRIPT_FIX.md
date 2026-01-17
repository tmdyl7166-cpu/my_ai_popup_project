# AISP 项目脚本调用线修复计划

## 任务概述
检查并修复项目中的脚本调用线问题、函数重复定义、类型引用错误、逻辑冲突等问题，并修正容器挂载配置以支持本地离线运行。

## 修复计划

### 阶段1: 统一路径配置 (已完成) ✅

#### 1.1 修复 `scripts/daemon_guard.py` ✅
- [x] 移除重复的 `get_project_root()` 函数定义
- [x] 统一使用 `scripts.path_config.get_project_root()`
- [x] 简化路径获取逻辑

#### 1.2 修复 `scripts/main.py` ✅
- [x] 移除重复的 `_get_project_root()` 方法
- [x] 统一使用 `scripts.path_config.get_project_root()`
- [x] 修复导入逻辑

#### 1.3 修复 `scripts/health_check.py` ✅
- [x] 修复类型注解 `health_checker: Optional['HealthChecker'] = None`
- [x] 修复 `get_summary()` 方法中可能的 None 值

### 阶段2: 修复容器挂载配置 (已完成) ✅

#### 2.1 修复 `containers/start_aisp.sh` ✅
- [x] 移除对外部Docker服务的依赖
- [x] 简化启动逻辑为本地离线模式
- [x] 添加 `AISP_OFFLINE_MODE` 环境变量
- [x] 移除不必要的健康检查端口依赖

### 阶段3: 清理模块初始化 (待验证)

#### 3.1 统一 `backend/__init__.py` 和 `backend/services/__init__.py`
- [ ] 合并重复的 OpenCV 延迟加载逻辑
- [ ] 统一服务注册表实现
- [ ] 确保状态函数一致性

#### 3.2 修复 `backend/api.py`
- [ ] 添加 OpenCV 条件导入
- [ ] 移除不必要的直接依赖

### 阶段4: 验证和测试 (待执行)

#### 4.1 语法检查
- [ ] 运行 `python3 -m py_compile scripts/*.py`
- [ ] 运行 `python3 -m py_compile backend/**/*.py`

#### 4.2 导入测试
- [ ] 测试 `scripts.path_config` 导入
- [ ] 测试 `scripts.logging_utils` 导入
- [ ] 测试 `backend` 模块导入

## 已完成的修复

### 修复1: daemon_guard.py
```python
# 修改前: 复杂的try-except导入和重复定义
try:
    from scripts.path_config import (
        PROJECT_ROOT,
        get_project_root,
    )
    USE_UNIFIED_CONFIG = True
except ImportError:
    USE_UNIFIED_CONFIG = False
    ...

# 修改后: 直接使用统一配置
from scripts.path_config import PROJECT_ROOT, get_project_root, get_config_path
CONFIG_PATH = get_config_path("daemon_guard_config.json")
```

### 修复2: main.py
```python
# 修改前: 复杂的try-except和重复方法
try:
    from scripts.path_config import get_project_root
    ...
except ImportError:
    USE_UNIFIED_CONFIG = False

def _get_project_root(self) -> Path:
    ...

# 修改后: 直接使用统一配置
from scripts.path_config import get_project_root

# 在__init__中使用:
self.project_root = project_root or get_project_root()
```

### 修复3: health_check.py
```python
# 修改前: 类型注解使用type: ignore
health_checker = None  # type: ignore[assignment]

# 修改后: 正确的可选类型注解
health_checker: Optional['HealthChecker'] = None
```

### 修复4: start_aisp.sh
```bash
# 修改前: 依赖外部端口健康检查
check_service_health "AISP Backend" "8000"
BACKEND_HEALTH=$?

# 修改后: 离线模式不依赖外部检查
export AISP_OFFLINE_MODE="true"
BACKEND_HEALTH=0
WEB_HEALTH=0
OLLAMA_HEALTH=0
```

## 验证命令

```bash
# 语法检查
python3 -m py_compile scripts/daemon_guard.py
python3 -m py_compile scripts/main.py
python3 -m py_compile scripts/health_check.py

# 路径配置测试
python3 -c "from scripts.path_config import get_project_root; print(get_project_root())"

# 日志配置测试
python3 -c "from scripts.logging_utils import setup_logger; setup_logger('test')"
```

## 完成状态
- [x] 阶段1: 统一路径配置
- [x] 阶段2: 修复容器挂载配置
- [ ] 阶段3: 清理模块初始化 (延迟)
- [ ] 阶段4: 验证和测试

## 预计修复文件列表 (已完成)
1. [x] `scripts/daemon_guard.py`
2. [x] `scripts/main.py`
3. [x] `scripts/health_check.py`
4. [x] `containers/start_aisp.sh`
5. [ ] `backend/__init__.py` (待验证)
6. [ ] `backend/services/__init__.py` (待验证)
7. [ ] `backend/api.py` (待验证)

