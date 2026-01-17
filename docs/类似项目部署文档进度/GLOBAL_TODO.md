# AISP 全局任务待办清单

> **创建时间**: 2025-01-21  
> **最后更新**: 2025-01-21  
> **状态**: 执行中

---

## 📋 任务总览

| 优先级 | 类别 | 任务数 | 完成数 | 进行中 |
|--------|------|--------|--------|--------|
| 🔴 高 | 配置与验证 | 4 | 2 | 1 |
| 🟡 中 | Web监控优化 | 4 | 6 | 1 |
| 🟢 中 | 脚本与配置修复 | 5 | 3 | 0 |
| 🔵 低 | 文档与UI优化 | 2 | 0 | 0 |

---

## 🔴 高优先级 - 配置与验证

### T001: 修复 health_check_config.json ✅ 已完成
- [x] 创建 config/health_check_config.json
- [x] 添加 config_priority 字段
- [x] 添加 config_association 字段
- [x] 验证 JSON 语法

### T002: 更新验证器逻辑 ⏳ 进行中
- [ ] 分析 scripts/validate_configs.py 字段检查逻辑
- [ ] 修改验证器支持 depends_on 字段
- [ ] 测试验证器
- **状态**: ⏳ 待开始

### T003: 验证所有配置
- [ ] 运行配置验证器
- [ ] 检查层级验证结果
- [ ] 修复发现的问题
- **状态**: ⏳ 待开始

### T004: 运行规则检查器
- [ ] 执行 `scripts/validate_root_rules.py`
- [ ] 修复严重违规
- [ ] 验证通过
- **状态**: ⏳ 待开始

---

## 🟡 中优先级 - Web监控优化

### T005: 集成 dashboard/health API ✅ 已完成
- [x] 创建 `backend/services/monitor_storage.py`
- [x] 创建 `backend/services/health_scoring.py`
- [x] 创建 `backend/services/monitor_ws.py`
- [x] 更新 `backend/unified_api.py` 添加 dashboard 端点
- [x] 添加 `/web/api/health` 端点
- [x] 集成监控存储服务
- [x] 集成健康评分服务

### T006: 更新前端页面UI
- [ ] 更新 `web/templates/index.html` 添加健康评分组件
- [ ] 添加报警通知面板
- [ ] 优化整体布局
- [ ] 优化移动端响应式布局
- **状态**: ⏳ 待开始

### T007: 集成WebSocket客户端 ⏳ 进行中
- [x] 创建 `web/static/js/websocket.js`
- [ ] 更新 `web/static/js/app.js` 集成WebSocket客户端
- [ ] 更新 `web/static/js/charts.js` 添加实时图表
- [ ] 测试实时数据推送
- **状态**: ⏳ 待开始

### T008: 功能测试与验证
- [ ] 测试所有API端点
- [ ] 测试WebSocket连接
- [ ] 验证健康评分计算
- [ ] 性能测试
- **状态**: ⏳ 待开始

---

## 🟢 中优先级 - 脚本与配置修复

### T009: 修复Shell脚本硬编码路径 ✅ 已完成
检查后发现以下脚本**已有动态路径检测，无需修复**：
- [x] `scripts/start_aisp_with_ollama.sh` - 已有 get_project_root()
- [x] `scripts/cleanup_env.sh` - 已有 get_project_root()
- [x] `scripts/api_opt_.sh` - 已有 get_project_root()
- **状态**: ✅ 已完成 (无需修复)

### T010: 统一环境变量命名
- [ ] 更新 `scripts/setup_env.sh` 添加英文环境变量
- [ ] 更新 `scripts/backup.sh`
- [ ] 更新 `scripts/log_rotate.sh`
- [ ] 更新 Python 脚本环境变量名
- **状态**: ⏳ 待开始

### T011: 清理废弃API文件
- [ ] 分析 `backend/api.py` 废弃情况
- [ ] 创建迁移指南
- [ ] 清理或标记废弃
- **状态**: ⏳ 待开始

### T012: 统一任务队列位置
- [ ] 分析当前任务队列实现
- [ ] 统一到 `task_scheduler.py`
- [ ] 更新依赖引用
- **状态**: ⏳ 待开始

### T013: 验证和测试
- [ ] 语法检查所有Python脚本
- [ ] 导入测试
- [ ] 路径配置测试
- **状态**: ⏳ 待开始

---

## 🔵 低优先级 - 文档与UI优化

### T014: README.md 优化
- [ ] 更新项目概述与五层逻辑架构说明
- [ ] 完善新框架结构说明
- [ ] 更新功能特性
- [ ] 更新安装部署说明
- [ ] 更新项目结构树
- [ ] 更新配置说明
- [ ] 更新引擎集成说明
- **状态**: ⏳ 待开始

### T015: GUI验证测试
- [ ] 验证 ar_config_dialog.py 语法
- [ ] 验证导入成功
- [ ] 验证窗口创建
- **状态**: ⏳ 待开始

---

## 📝 执行记录

### 2025-01-21
- 14:00 - 创建全局任务待办清单
- 14:10 - 开始执行任务
- 14:15 - 分析所有待办文档
- 14:20 - 确认脚本已有动态路径检测，无需修复
- 14:25 - 开始 Web 监控优化 (T005, T007)
- 14:30 - 创建 health_check_config.json
- 14:35 - 更新 unified_api.py 添加 dashboard 和 health 端点
- 14:40 - 运行配置验证器
- 14:45 - 更新 health_check_config.json 添加 config_association

### 已完成任务详情
1. ✅ T005: Web监控后端服务创建
   - monitor_storage.py - 监控数据持久化
   - health_scoring.py - 健康评分系统
   - monitor_ws.py - WebSocket处理器

2. ✅ T005: unified_api.py API端点更新
   - /web/api/dashboard - 综合仪表盘
   - /web/api/health - 健康评分

3. ✅ T001: health_check_config.json 创建
   - 完整的健康检查配置
   - config_priority 层级信息
   - config_association 依赖关系

---

## 验证命令

```bash
# 验证配置
python3 scripts/validate_configs.py --all

# 验证JSON语法
python3 -c "import json; json.load(open('config/health_check_config.json'))"

# 运行规则检查
python3 scripts/validate_root_rules.py

# 语法检查
python3 -m py_compile scripts/*.py
python3 -m py_compile backend/**/*.py
```

---

*创建时间: 2025-01-21*
*最后更新: 2025-01-21*

