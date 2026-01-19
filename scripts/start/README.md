# Scripts目录 - 启动脚本

## 启动脚本列表

| 文件                    | 说明                |
| ----------------------- | ------------------- |
| main_launcher.py        | 主启动器 - 统一入口 |
| start_backend_simple.py | 启动后端服务        |
| start_gui_py.py         | 启动GUI窗口         |
| start_hot_window.sh     | 启动热窗口 (Shell)  |
| unified_launcher.py     | 统一启动器          |

## 使用方法

### 统一启动器

```bash
python scripts/start/unified_launcher.py --mode all
```

### 启动后端

```bash
python scripts/start/start_backend_simple.py --host 0.0.0.0 --port 8080
```

### 启动GUI

```bash
python scripts/start/start_gui_py.py
```

### 启动热窗口

```bash
bash scripts/start/start_hot_window.sh
```

---

_创建时间: 2026-01-19_
