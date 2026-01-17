# AISP 脚本优化修复计划

## 问题汇总

### 1. 硬编码路径问题
- `health_check.py`: 硬编码 `/home/vboxuser/桌面/BX/AI规则/AISP`
- `verify_paths.py`: 硬编码 `/home/vboxuser/桌面/BX/AI规则/夜灵AR多功能合成软件`
- `path_config.py`: 硬编码 `/home/vboxuser/桌面/BX/AI规则/AISP/venv`

### 2. 环境变量命名不一致
- 使用了中文项目名 "夜灵AR多功能合成软件" 作为环境变量
- 应该在所有脚本中使用统一的英文环境变量 `AISP_PROJECT_ROOT`

### 3. 脚本导入路径问题
- `main.py`: 尝试导入 `scripts.path_config`，但在项目根目录运行时可能失败
- `verify_deployment.py`: 添加 backend 到路径，但方式不正确

### 4. 缺失的依赖检查
- 多个脚本的 `check_dependencies` 函数不完整

## 修复计划

### 阶段1: 修复路径配置 (path_config.py)
- [ ] 移除硬编码路径
- [ ] 使用统一的动态路径检测

### 阶段2: 修复健康检查 (health_check.py)
- [ ] 使用动态路径检测
- [ ] 统一导入方式

### 阶段3: 修复验证脚本
- [ ] `verify_paths.py`: 移除硬编码路径
- [ ] `verify_deployment.py`: 修复导入路径

### 阶段4: 修复资源监控脚本
- [ ] `resource_alert.py`: 使用统一路径配置
- [ ] `disk_monitor.py`: 使用统一路径配置

### 阶段5: 统一环境变量名
- [ ] 将所有 "夜灵AR多功能合成软件_PROJECT_ROOT" 改为 "AISP_PROJECT_ROOT"

## 执行状态
- [x] 分析完成
- [ ] 开始实施修复

## 详细修复项

### 修复1: health_check.py
```python
# 修复前:
config_path = "/home/vboxuser/桌面/BX/AI规则/AISP/config/health_check_config.json"
project_root = Path("/home/vboxuser/桌面/BX/AI规则/AISP")

# 修复后:
PROJECT_ROOT = Path(__file__).parent.parent
config_path = PROJECT_ROOT / "config" / "health_check_config.json"
```

### 修复2: path_config.py
```python
# 修复前:
common_venvs = [
    get_project_root() / "venv",
    get_project_root() / ".venv",
    Path("/home/vboxuser/桌面/BX/AI规则/AISP/venv"),  # 硬编码
]

# 修复后:
common_venvs = [
    get_project_root() / "venv",
    get_project_root() / ".venv",
]
```

### 修复3: daemon_guard.py, disk_monitor.py, resource_alert.py
```python
# 修复前:
if os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
    return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])

# 修复后:
if os.environ.get("AISP_PROJECT_ROOT"):
    return Path(os.environ["AISP_PROJECT_ROOT"])
```

### 修复4: main.py
```python
# 修复前:
from scripts.path_config import get_project_root
from scripts.logging_utils import setup_logger, get_logger

# 修复后:
try:
    from scripts.path_config import get_project_root
    from scripts.logging_utils import setup_logger, get_logger
    USE_UNIFIED_CONFIG = True
except ImportError:
    USE_UNIFIED_CONFIG = False
    # 使用备用方案
```

### 修复5: verify_paths.py
```python
# 修复前:
project_root = Path("/home/vboxuser/桌面/BX/AI规则/夜灵AR多功能合成软件")

# 修复后:
if USE_UNIFIED_CONFIG:
    project_root = get_project_root()
else:
    project_root = Path.cwd()
```

## 验证方法
运行以下脚本验证修复:
```bash
python3 scripts/verify_paths.py
python3 scripts/health_check.py --check
python3 scripts/main.py --status
```

