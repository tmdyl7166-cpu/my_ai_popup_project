# Scripts目录整理任务

## 任务目标
整理 `/home/vboxuser/桌面/BX/HC/my_ai_popup_project/scripts` 目录：
- 在scripts根目录只保留3个文件（启动项+配置+说明文档）
- 其他脚本全部迁移到对应的子目录

## 保留在根目录的文件（3个）
- [ ] `entry.py` - 统一入口脚本
- [ ] `scripts_config.json` - JS配置
- [ ] `scripts_README.md` - 说明文档

## 迁移计划

### 迁移到 `start/` 目录（4个文件）
- [ ] `start_backend_simple.py`
- [ ] `start_gui_py.py`
- [ ] `start_health_monitor.py`
- [ ] `start_hot_window.sh`

### 迁移到 `health/` 目录（1个文件）
- [ ] `health_check.py`

### 迁移到 `deploy/` 目录（3个文件）
- [ ] `deploy.sh`
- [ ] `emergency_recovery.sh`
- [ ] `fix_opencv_deps.sh`

### 迁移到 `verify/` 目录（4个文件）
- [ ] `verify_paths.py`
- [ ] `validate_configs.py`
- [ ] `verify_venv.py`
- [ ] `check_pylance_version.py`

### 迁移到 `core/` 目录（3个文件）
- [ ] `main_controller.py`
- [ ] `main_launcher.py`
- [ ] `unified_launcher.py`

### 迁移到 `utils/` 目录（3个文件）
- [ ] `path_config.py`
- [ ] `sync_web_config.sh`
- [ ] `system_diagnostic`

## 待处理文件
- [ ] `__init__.py` - 检查是否需要保留
- [ ] `SCRIPTS_INDEX.md` - 考虑合并到scripts_README.md
- [ ] `scripts_config_refactor.json` - 考虑合并到scripts_config.json

## 后续更新
- [ ] 更新 `scripts_README.md` 文档
- [ ] 更新 `scripts_config.json` 配置
- [ ] 更新其他引用这些脚本的文件

## 开始时间
2026-01-18

