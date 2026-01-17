# AISP 项目问题修复计划

## 问题汇总分析

### 1. 中文项目名硬编码问题
- **严重程度**: 高
- **影响范围**: 5个脚本文件
- **问题描述**: 多个脚本使用中文"夜灵AR多功能合成软件"作为项目名称

### 2. 路径配置冗余
- **严重程度**: 中
- **影响范围**: 2个路径配置模块
- **问题描述**: `scripts/path_config.py` 和 `backend/path_utils.py` 功能重叠

### 3. 环境变量命名不一致
- **严重程度**: 中
- **影响范围**: 4个脚本
- **问题描述**: 使用中文环境变量名 `夜灵AR多功能合成软件_PROJECT_ROOT`

---

## 修复计划

### 阶段1: 创建统一的路径配置模块 (修复1)

#### 1.1 更新 `scripts/path_config.py`
- [ ] 移除冗余代码，保持与 `backend/path_utils.py` 一致
- [ ] 统一导出接口
- [ ] 保持向后兼容性

#### 1.2 更新 `backend/path_utils.py`
- [ ] 确保所有路径函数使用统一的环境变量 `AISP_PROJECT_ROOT`
- [ ] 添加对旧中文环境变量的兼容支持
- [ ] 优化导入逻辑

### 阶段2: 修复中文项目名硬编码 (修复2)

#### 2.1 修复 `scripts/daemon_guard.py`
```python
# 修复前:
if os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
    return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])

# 修复后:
if os.environ.get("AISP_PROJECT_ROOT"):
    return Path(os.environ["AISP_PROJECT_ROOT"])
# 保留兼容层:
elif os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
    return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])
```

#### 2.2 修复 `scripts/disk_monitor.py`
- [ ] 更新环境变量检查
- [ ] 更新日志输出中的项目名称
- [ ] 更新帮助信息

#### 2.3 修复 `scripts/resource_alert.py`
- [ ] 更新环境变量检查
- [ ] 更新日志输出中的项目名称
- [ ] 更新帮助信息

#### 2.4 修复 `scripts/verify_paths.py`
- [ ] 更新打印输出中的项目名称
- [ ] 更新注释信息

#### 2.5 修复 `scripts/validate_configs.py`
- [ ] 更新项目名称引用
- [ ] 更新帮助信息

### 阶段3: 统一路径引用 (修复3)

#### 3.1 验证并更新所有脚本的路径引用
- [ ] 确保所有脚本使用 `from scripts.path_config import get_project_root`
- [ ] 或使用 `from backend.path_utils import get_project_root`
- [ ] 移除所有硬编码路径

### 阶段4: 验证与测试 (修复4)

#### 4.1 验证脚本修复
```bash
# 运行验证脚本
python3 scripts/verify_paths.py
python3 scripts/health_check.py
python3 scripts/daemon_guard.py --status
python3 scripts/disk_monitor.py --status
python3 scripts/resource_alert.py --status
```

#### 4.2 运行完整健康检查
```bash
python3 scripts/health_check.py --check
```

---

## 详细修复项

### 修复1: scripts/daemon_guard.py

```python
# 文件开头添加统一导入
from scripts.path_config import get_project_root

# 修改 get_project_root 函数
def get_project_root() -> Path:
    """获取项目根目录 - 统一版本"""
    # 优先使用统一的环境变量名
    if os.environ.get("AISP_PROJECT_ROOT"):
        return Path(os.environ["AISP_PROJECT_ROOT"])
    
    # 兼容旧的中文环境变量名（临时兼容层）
    if os.environ.get("夜灵AR多功能合成软件_PROJECT_ROOT"):
        return Path(os.environ["夜灵AR多功能合成软件_PROJECT_ROOT"])
    
    # 尝试从当前文件位置推断
    current_file = Path(__file__).resolve()
    return current_file.parent.parent

# 修改日志输出
print("=" * 60)
print("AISP 进程守护状态")  # 替代 "夜灵AR多功能合成软件 进程守护状态"
print("=" * 60)

# 修改帮助信息
parser = argparse.ArgumentParser(description="AISP 进程守护脚本")  # 替代 "夜灵AR多功能合成软件 进程守护脚本"
```

### 修复2: scripts/disk_monitor.py

```python
# 修改日志输出
print("\n" + "=" * 60)
print("AISP 磁盘空间监控状态")  # 替代 "夜灵AR多功能合成软件 磁盘空间监控状态"
print("=" * 60)

# 修改帮助信息
parser = argparse.ArgumentParser(description="AISP 磁盘空间监控脚本")  # 替代 "夜灵AR多功能合成软件 磁盘空间监控脚本"
```

### 修复3: scripts/resource_alert.py

```python
# 修改日志输出
print("\n" + "=" * 60)
print("AISP 资源监控状态")  # 替代 "夜灵AR多功能合成软件 资源监控状态"
print("=" * 60)

# 修改帮助信息
parser = argparse.ArgumentParser(description="AISP 资源告警脚本")  # 替代 "夜灵AR多功能合成软件 资源告警脚本"
```

### 修复4: scripts/verify_paths.py

```python
# 修改打印输出
print("=" * 70)
print("AISP 路径验证")  # 替代 "夜灵AR多功能合成软件 路径验证"
print("=" * 70)
```

### 修复5: scripts/validate_configs.py

```python
# 修改项目名称
print("=" * 60)
print("AISP 配置验证工具 v1.1.0")  # 替代 "夜灵AR多功能合成软件 配置验证工具 v1.1.0"
print("=" * 60)

# 修改帮助信息
parser = argparse.ArgumentParser(description="AISP 配置验证工具")  # 替代 "夜灵AR多功能合成软件 配置验证工具"
```

---

## 验证方法

运行以下命令验证修复:

```bash
# 1. 验证路径
python3 scripts/verify_paths.py

# 2. 验证健康检查
python3 scripts/health_check.py --check

# 3. 验证进程守护
python3 scripts/daemon_guard.py --status

# 4. 验证磁盘监控
python3 scripts/disk_monitor.py --status

# 5. 验证资源告警
python3 scripts/resource_alert.py --status

# 6. 运行完整部署验证
python3 scripts/verify_deployment.py
```

---

## 预期结果

修复后:
1. 所有脚本使用统一的环境变量名 `AISP_PROJECT_ROOT`
2. 项目名称统一使用 "AISP"
3. 路径配置模块功能一致，无冗余
4. 所有脚本可正常运行，无硬编码路径错误

---

## 执行状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| 阶段1 | 待执行 | 创建统一路径配置 |
| 阶段2 | 待执行 | 修复中文项目名 |
| 阶段3 | 待执行 | 统一路径引用 |
| 阶段4 | 待执行 | 验证与测试 |

