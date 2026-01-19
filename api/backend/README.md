# API Backend - 后端路由模块

## 目录说明

此目录包含从 web/ 移动过来的 Python 后端脚本。

## 文件列表

| 文件                  | 说明            |
| --------------------- | --------------- |
| app.py                | Flask应用主程序 |
| config_manager.py     | 配置管理        |
| deployment_monitor.py | 部署监控        |
| entry.py              | 入口脚本        |
| script_manager.py     | 脚本管理        |
| security.py           | 安全模块        |
| socket_events.py      | WebSocket事件   |
| system_monitor.py     | 系统监控        |
| web_monitor.py        | Web监控         |

## 路由注册

所有后端路由在 app.py 中定义，使用 Flask 框架。

### 快速启动

```bash
# 从项目根目录启动
cd /home/vboxuser/桌面/BX/HC/my_ai_popup_project
python -m api.backend.app

# 或使用 uvicorn (如果使用 FastAPI)
uvicorn api.backend.app:app --host 0.0.0.0 --port 8080
```

### 配置

默认配置:

- Host: 0.0.0.0
- Port: 8080
- Debug: False

---

_创建时间: 2026-01-19_
