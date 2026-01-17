# AISP 部署错误修复任务清单

## 任务概述
修复以下部署错误:
1. FileNotFoundError: /workspaces/AISP/venv/lib/python3.12/dist-packages
2. ImportError: libGL.so.1: cannot open shared object file

## 修复计划执行状态

### 阶段1: 系统依赖安装脚本 ✅ 完成
- [x] 创建 `scripts/fix_opencv_deps.sh`
- [x] 支持 Ubuntu/Debian, CentOS/RHEL, Fedora
- [x] 包含虚拟环境路径修复

### 阶段2: backend/__init__.py 延迟导入 ✅ 完成
- [x] 实现 `_try_load_cv2()` 延迟加载机制
- [x] 添加 `_CV2_LOADED`, `_CV2_LOAD_ERROR`, `_FALLBACK_MODE` 状态跟踪
- [x] 非 cv2 依赖模块优先加载
- [x] 添加状态查询函数 (is_cv2_loaded, is_fallback_mode, get_cv2_load_error)

### 阶段3: backend/services/__init__.py 延迟导入 ✅ 完成
- [x] 实现服务注册表 `_SERVICE_REGISTRY`
- [x] 分离 cv2 依赖和非 cv2 依赖服务
- [x] 添加 `require_service()` 安全获取服务接口
- [x] 添加 `reload_services()` 重新加载功能

### 阶段4: verify_deployment.py 隔离检查 ✅ 完成
- [x] 实现 `_safe_import_cv2()` 安全导入
- [x] OpenCV 降级模式不阻塞其他模块验证
- [x] 添加 OpenCV 状态报告和修复建议

### 阶段5: 虚拟环境路径修复 ✅ 完成
- [x] 创建 `dist-packages` -> `site-packages` 软链接
- [x] 更新 `fix_opencv_deps.sh` 脚本自动修复此问题
- [x] OpenCV 版本 4.12.0 验证通过

### 阶段6: 后续步骤
- [x] 运行安装脚本: `sudo bash scripts/fix_opencv_deps.sh`
- [x] 重新激活虚拟环境: `source venv/bin/activate`
- [x] 运行验证脚本: `python3 scripts/verify_deployment.py`
- [ ] 启动应用测试: `python3 run_gui.py`

## 修复文件清单
1. `scripts/fix_opencv_deps.sh` - 系统依赖安装脚本
2. `backend/__init__.py` - 延迟导入重构
3. `backend/services/__init__.py` - 服务注册表和延迟加载
4. `scripts/verify_deployment.py` - 隔离 OpenCV 检查

## 预期效果
- 核心模块不再因 OpenCV 加载失败而阻塞
- 提供清晰的降级模式和错误提示
- 支持无 GPU/无显示环境运行
- 保持原有功能完整性

