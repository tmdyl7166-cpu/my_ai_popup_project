# 脚本修复计划

## 问题分析

### 根本原因
用户可能使用 `python3` 而不是 `bash` 来执行 `.sh` 脚本文件，导致：
- 第20行的 `set -euo pipefail` 被 Python 解释
- 第223行的多行 Python 代码块被错误解析

### 错误表现
- "set -euo pipefail" - Bash 语法被 Python 执行
- 第223行有未终止的字符串
- 脚本无法正常启动

## 解决方案

### 方案1: 确保使用正确的解释器执行
**问题**: 用户可能执行了 `python3 start_server.sh` 而不是 `./start_server.sh`

**解决**: 
1. 确认脚本有正确的 shebang: `#!/bin/bash`
2. 确认脚本有执行权限
3. 使用正确的方式执行: `./start_server.sh` 或 `bash start_server.sh`

### 方案2: 修复可能的多行字符串问题
**问题**: 脚本中的 Python 代码块在某些情况下可能导致问题

**解决**: 将内嵌的 Python 代码提取到独立的 Python 文件中

## 具体修复步骤

### 步骤1: 创建独立的 Python 启动脚本

创建 `scripts/start_gui_py.py`:

```python
#!/usr/bin/env python3
import sys
import os

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

try:
    from gui.main_window import MainWindow
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
except ImportError as e:
    print(f'导入错误: {e}')
    print('请确保已安装必要的依赖: pip install PyQt6 opencv-python numpy')
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName('AISP')
    app.setApplicationVersion('1.0.0')
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
```

### 步骤2: 修改 start_gui.sh

将:
```bash
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
...
"
```

改为:
```bash
python3 "$PROJECT_ROOT/scripts/start_gui_py.py"
```

### 步骤3: 创建使用说明文档

## 验证步骤

1. 检查脚本执行权限
2. 使用正确的命令执行
3. 测试启动流程

