# API Routes 修复任务清单

## 修复目标
修复 `api_routes.py` 中的所有代码问题，包括：
- 未使用的导入 (F401)
- 模块级导入不在文件顶部 (E402)
- 未定义的名称 (Pylance)
- 代码风格问题 (E501)
- 异常处理问题 (E722)

## 任务清单

### 阶段1: 清理导入
- [ ] 1.1 移除未使用的导入: os, asyncio, hashlib, logging
- [ ] 1.2 移除未使用的 fastapi/ pydantic 导入
- [ ] 1.3 添加缺少的导入: HTTPBearer, HTTPAuthorizationCredentials
- [ ] 1.4 将 sys.path 导入移到顶部
- [ ] 1.5 将 get_logger 导入移到顶部
- [ ] 1.6 处理 get_security_manager 问题

### 阶段2: 修复认证依赖
- [ ] 2.1 实现简单的安全管理器替代方案
- [ ] 2.2 修复 get_current_user 依赖
- [ ] 2.3 修复 get_admin_user 依赖

### 阶段3: 代码风格优化
- [ ] 3.1 修复超过79字符的长行
- [ ] 3.2 修复裸 except 为 except Exception:
- [ ] 3.3 应用 Sourcery 优化建议

### 阶段4: 测试验证
- [ ] 4.1 运行 flake8 检查
- [ ] 4.2 运行 pylint/pylance 检查
- [ ] 4.3 验证代码功能正常

## 开始时间
- 开始: 2024年

## 状态更新
- [x] 分析代码问题
- [x] 制定修复计划
- [ ] 执行修复
- [ ] 验证修复结果

