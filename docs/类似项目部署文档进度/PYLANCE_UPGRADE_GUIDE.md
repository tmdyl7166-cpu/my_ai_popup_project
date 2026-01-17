# Pylance升级指南 (Python 3.12)

## 问题描述

Python 3.12对类型系统进行了增强，导致与旧版Pylance存在兼容性问题。

### 典型错误
```
无法将"Literal[b\"/\", '/']"类型的参数分配给函数"startswith"中类型为"str | tuple[str, ...]"的参数"prefix"
  类型"Literal[b\"/", '/']"不可分配给类型"str | tuple[str, ...]"
    类型"Literal[b\"/"]"不可分配给类型"str"
    类型"Literal[b\"/"]"不可分配给类型"tuple[str, ...]"
```

### 问题位置
- **文件**: `/usr/lib/python3.12/posixpath.py`
- **行号**: 83
- **函数**: `startswith`

### 根本原因
Python 3.12在标准库中引入了更严格的类型注解，但旧版Pylance的类型检查器不完全支持这些新的类型语法，导致类型推断冲突。

## 解决方案

### 方案1：升级Pylance扩展（推荐）

**步骤：**
1. 打开VSCode
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 在搜索框中输入 "Pylance"
4. 找到 "Pylance" 扩展（作者：Microsoft）
5. 如果有更新按钮，点击 "更新"
6. 重启VSCode

**命令行方式：**
```bash
# 安装最新版本
code --install-extension ms-python.vscode-pylance@latest

# 或者指定版本（推荐2024.1.5+）
code --install-extension ms-python.vscode-pylance@2024.1.5
```

### 方案2：更新VSCode

有时需要同时更新VSCode才能支持最新Pylance：
1. 按 `Ctrl+Shift+P`
2. 输入 "Check for Updates"
3. 如果有更新，安装并重启

### 方案3：工作区配置排除（临时解决方案）

项目已在 `.vscode/settings.json` 中添加了排除配置，排除所有系统库和虚拟环境：

```json
{
    "python.analysis.exclude": [
        "/usr/lib/python3.12/**",
        "/usr/lib/python3.13/**",
        "/usr/local/lib/python3.12/**",
        "/usr/local/lib/python3.13/**",
        "${env:HOME}/.local/lib/python3.12/**",
        "${env:HOME}/.local/lib/python3.13/**",
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**"
    ]
}
```

这将排除：
- Python 3.12/3.13 系统库
- 虚拟环境目录 (`.venv`, `venv`)
- 缓存目录 (`__pycache__`)

避免显示第三方库的类型检查错误。

## 版本兼容性

| Python版本 | 最低Pylance版本 | 推荐Pylance版本 | 状态 |
|------------|-----------------|-----------------|------|
| 3.12.x     | 2024.1.0        | 2024.1.5+       | 需要升级 |
| 3.11.x     | 2023.3.3        | 2023.3.3+       | 兼容 |
| 3.10.x     | 2022.12.1       | 2022.12.1+      | 兼容 |

## 验证修复

### 方法1：运行检测脚本
```bash
cd /workspaces/AISP
python scripts/check_pylance_version.py --check-only
```

期望输出：
```
✓ Python 3.12兼容性问题已解决
✓ Pylance版本兼容
```

### 方法2：重启VSCode
1. 完全关闭VSCode
2. 重新打开项目
3. 检查错误是否消失

### 方法3：重新加载窗口
在VSCode中按 `Ctrl+Shift+P`，输入 "Reload Window"

## 排查步骤

如果问题仍然存在：

1. **检查Pylance版本**
   - 在VSCode中按 `Ctrl+Shift+P`
   - 输入 "Developer: Show Running Extensions"
   - 查找 "Pylance" 查看版本号

2. **检查Python版本**
   ```bash
   python --version
   ```

3. **清除缓存并重新加载**
   - 按 `Ctrl+Shift+P`
   - 输入 "Python: Restart Language Server"
   - 选择 "Reload Window"

4. **检查配置文件**
   确保 `.vscode/settings.json` 中没有冲突的设置。

## 相关信息

- [Pylance GitHub](https://github.com/microsoft/pylance-release)
- [Python 3.12发行说明](https://docs.python.org/3.12/whatsnew/3.12.html)
- [PEP 701 - 语法形式化注解](https://peps.python.org/pep-0701/)
- [VSCode Python扩展](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

## 项目配置

本项目已采取以下措施来缓解此问题：

1. ✅ 在 `.vscode/settings.json` 中排除Python 3.12系统库
2. ✅ 创建了 `scripts/check_pylance_version.py` 检测脚本
3. ✅ 设置了 `basic` 类型检查模式（较宽松）

## 常见问题FAQ

**Q: 这个错误会影响程序运行吗？**
A: 不会。这只是类型检查器的警告，不影响程序的实际运行。

**Q: 为什么只排除Python系统库？**
A: Python标准库的类型注解在不断改进，某些新语法可能与类型检查器不完全兼容。排除系统库可以避免这些误报，同时保持项目代码的类型检查。

**Q: 升级Pylance后需要做什么？**
A: 重启VSCode或重新加载窗口（`Ctrl+Shift+P` -> "Reload Window"）。

**Q: 可以完全禁用类型检查吗？**
A: 可以，但不推荐。在设置中设置 `"python.analysis.typeCheckingMode": "off"` 将禁用类型检查。

---

*文档生成时间: 2024*
*适用项目: AISP*

