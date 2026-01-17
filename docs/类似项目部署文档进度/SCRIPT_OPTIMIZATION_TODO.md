# AISP 配置自动化脚本优化修复计划

## 问题汇总

### 1. 硬编码路径问题 (严重)
- `start_aisp_with_ollama.sh`: 硬编码 `PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/AISP"`
- `cleanup_env.sh`: 硬编码 `PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/AISP"`
- `api_opt_.sh`: 硬编码 `PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/夜灵AR多功能合成软件"`

### 2. 环境变量命名不一致 (中等)
- 使用了中文环境变量名 `"夜灵AR多功能合成软件_PROJECT_ROOT"`
- 应该统一使用英文环境变量名 `"AISP_PROJECT_ROOT"`
- 兼容旧的中文环境变量名

### 3. 路径检测函数不统一 (中等)
- 部分脚本使用动态路径检测函数 `get_project_root()`
- 部分脚本直接硬编码路径
- 需要统一所有脚本的路径检测逻辑

### 4. Shell脚本规范问题 (轻微)
- 部分脚本缺少 `set -euo pipefail`
- 颜色定义不完整
- 缺少错误处理

## 修复计划

### 阶段1: 修复 Shell 脚本硬编码路径
- [ ] 修复 `start_aisp_with_ollama.sh` - 使用动态路径检测
- [ ] 修复 `cleanup_env.sh` - 使用动态路径检测
- [ ] 修复 `api_opt_.sh` - 使用动态路径检测

### 阶段2: 统一环境变量命名
- [ ] 更新 `setup_env.sh` - 添加英文环境变量支持
- [ ] 更新 `backup.sh` - 统一环境变量名
- [ ] 更新 `log_rotate.sh` - 统一环境变量名
- [ ] 更新 `emergency_recovery.sh` - 统一环境变量名
- [ ] 更新所有 Python 脚本 - 统一环境变量名

### 阶段3: 统一路径检测函数
- [ ] 创建标准化的 `get_project_root()` 函数模板
- [ ] 更新所有 Shell 脚本使用统一的路径检测
- [ ] 更新所有 Python 脚本使用统一的路径检测

### 阶段4: 增强错误处理和日志
- [ ] 添加 `set -euo pipefail` 到所有 Shell 脚本
- [ ] 统一颜色定义
- [ ] 添加详细的日志输出

## 执行状态
- [x] 分析完成
- [ ] 开始实施修复

## 修复项详情

### 修复1: start_aisp_with_ollama.sh
```bash
# 修复前:
PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/AISP"

# 修复后:
get_project_root() {
    if [ -n "${AISP_PROJECT_ROOT:-}" ] && [ -d "$AISP_PROJECT_ROOT" ]; then
        echo "$AISP_PROJECT_ROOT"
        return 0
    fi
    
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

PROJECT_ROOT=$(get_project_root)
```

### 修复2: cleanup_env.sh
```bash
# 修复前:
PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/AISP"

# 修复后:
get_project_root() {
    if [ -n "${AISP_PROJECT_ROOT:-}" ] && [ -d "$AISP_PROJECT_ROOT" ]; then
        echo "$AISP_PROJECT_ROOT"
        return 0
    fi
    
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

PROJECT_ROOT=$(get_project_root)
```

### 修复3: api_opt_.sh
```bash
# 修复前:
PROJECT_ROOT="/home/vboxuser/桌面/BX/AI规则/夜灵AR多功能合成软件"

# 修复后:
get_project_root() {
    if [ -n "${AISP_PROJECT_ROOT:-}" ] && [ -d "$AISP_PROJECT_ROOT" ]; then
        echo "$AISP_PROJECT_ROOT"
        return 0
    fi
    
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

PROJECT_ROOT=$(get_project_root)
```

### 修复4: Python脚本环境变量统一
```python
# 修复前:
if os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
    return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])

# 修复后:
if os.environ.get("AISP_PROJECT_ROOT"):
    return Path(os.environ["AISP_PROJECT_ROOT"])
# 保留兼容性
if os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
    return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])
```

## 验证方法
运行以下脚本验证修复:
```bash
# 验证Shell脚本路径检测
bash scripts/start_aisp_with_ollama.sh --help

# 验证Python脚本路径检测
python3 scripts/verify_paths.py

# 运行健康检查
python3 scripts/health_check.py --check
```

## 影响范围
- 所有Shell脚本: `*.sh`
- 所有Python脚本: `*.py`
- 配置文件: `config/*.json`

