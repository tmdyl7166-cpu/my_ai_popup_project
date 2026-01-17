# AISP 项目框架整理与修复计划

## 📋 任务概述

**任务目标**：对 `/home/vboxuser/桌面/BX/AI规则/AISP` 项目进行全面扫描、逻辑梳理、配置修正和优化部署。

**执行顺序**：
1. 文档说明 = 配置逻辑 = 执行逻辑（优先级排序）
2. 确保层级配置正确（上层不可被下层覆盖）
3. 消除重复功能，合并相似模块
4. 验证数据流顺序

---

## 🔍 一、问题诊断报告

### 1.1 配置层级问题

| 位置 | 文件 | 问题 | 优先级 |
|------|------|------|--------|
| 根目录/ | AI_RULES.json | ✅ 正确（层级1） | 已验证 |
| 根目录/ | AI_PATH_CONTEXT.json | ✅ 正确（层级1） | 已验证 |
| 根目录/ | AI_CLEANUP_POLICY.json | ✅ 正确（层级1） | 已验证 |
| config/ | AI_RULES.json | ❌ 重复定义 | **高** |
| config/ | AI_PATH_CONTEXT.json | ❌ 重复定义 | **高** |
| config/ | AI_CLEANUP_POLICY.json | ❌ 重复定义 | **高** |
| config/ | AI3.json | ✅ 正确（层级3） | 已验证 |

### 1.2 功能重复问题

| 模块 | 位置 | 功能 | 解决方案 |
|------|------|------|----------|
| 性能监控 | scripts/monitor.py | 资源监控 | **保留**（CLI工具） |
| 性能监控 | backend/services/performance_monitor.py | 资源监控 | **保留**（服务） |
| 性能监控 | backend/control_core/monitor.py | 资源监控 | **合并到 services/** |
| 任务调度 | backend/services/task_executor.py | 任务执行 | **合并到 task_scheduler.py** |
| 任务调度 | backend/services/task_scheduler.py | 任务调度 | **保留**（主调度器） |
| 数据存储 | backend/ai_control/memory_db.py | SQLite存储 | **保留**（持久化） |
| 数据存储 | backend/ai_control/memory_store.py | JSON存储 | **合并到 memory_db.py** |
| API入口 | backend/api.py | FastAPI入口 | **废弃，重定向到 unified_api.py** |
| API入口 | backend/unified_api.py | 统一API | **保留** |

### 1.3 配置关联缺失

| 文件 | 缺少字段 | 修复方式 |
|------|----------|----------|
| config/daemon_guard_config.json | config_association | 添加 |
| config/resource_alert_config.json | config_association | 添加 |
| config/run_config.example.json | meta, config_priority | 添加 |
| config/DOCS_SYNC_CONFIG.json | config_priority | 添加 |

### 1.4 数据流违规风险

| 违规类型 | 位置 | 检测结果 |
|----------|------|----------|
| GUI直接调用后端服务 | gui/main_window.py → backend/services/* | ❌ 需要检查 |
| 后端逆向调用control_core | backend/services/* → control_core/* | ⚠️ 需要验证 |

---

## 📐 二、项目框架结构

### 2.1 最终配置层级

```
┌─────────────────────────────────────────────────────────────────┐
│  层级 1 (最高优先级) - AI 行为规则配置                            │
│  位置: /workspaces/AISP/                                        │
│  文件:                                                           │
│    ├── AI_RULES.json            # AI行为约束与编程规则           │
│    ├── AI_PATH_CONTEXT.json     # 路径上下文与模块边界           │
│    └── AI_CLEANUP_POLICY.json   # 清理、合并、去重规则           │
│  规则: 不可被覆盖，定义所有下层配置的基础                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  层级 2 - 项目主配置                                             │
│  位置: /workspaces/AISP/config/                                 │
│  文件:                                                           │
│    ├── project_config.json      # 项目结构、模块、路径           │
│    ├── ai_config.json           # AI控制模块配置                 │
│    ├── engines_config.json      # 第三方引擎配置                 │
│    └── output_config.json       # 输出模块配置                   │
│  规则: 不可被覆盖，遵循层级1规则                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  层级 3 - 运行配置                                               │
│  位置: /workspaces/AISP/config/                                 │
│  文件:                                                           │
│    ├── run_config.json          # API服务器、Ollama运行配置      │
│    ├── health_check_config.json # 健康检测配置                  │
│    └── AI3.json                 # 前端交互与UI优化规则           │
│  规则: 可被环境变量覆盖                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  层级 4 - 功能子配置                                             │
│  位置: /workspaces/AISP/config/                                 │
│  目录:                                                           │
│    ├── ai/model_config.json     # 具体模型配置参数               │
│    ├── ai/capability_map.json   # AI能力边界与限制               │
│    └── tasks/                    # 任务管理                      │
│        ├── task_queue.json      # 待处理任务队列                 │
│        ├── task_schema.json     # 任务结构规范                  │
│        └── completed_tasks.json # 已完成任务记录                 │
│  规则: 继承上层配置，可根据具体功能调整                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块目录结构

```
AISP/
├── 🎨 gui/                          # GUI层 (L1)
│   ├── main_window.py              # 主窗口
│   ├── hot_window_manager.py       # 热窗口管理
│   ├── api_config.py               # API配置
│   ├── dialogs/                    # 对话框
│   ├── services/api_service.py     # API服务封装
│   └── widgets/                    # UI组件
│
├── 🔌 backend/                      # 后端层 (L2)
│   ├── api.py                      # ⚠️ 废弃（重定向）
│   ├── unified_api.py              # ✅ 统一API入口
│   ├── models.py                   # 数据模型
│   ├── path_utils.py               # 路径工具
│   ├── ai_control/                 # AI控制层
│   │   ├── auto_strategy.py        # 自动策略
│   │   ├── ollama_client.py        # Ollama客户端
│   │   └── memory_db.py            # 内存数据库 ⭐
│   ├── ar_engine/                  # AR引擎层
│   │   ├── frame_pipeline.py       # 帧处理管道
│   │   ├── adapters/               # 适配器
│   │   └── iRoopDeepFaceCam/       # 第三方引擎
│   ├── control_core/               # 控制核心
│   │   ├── server.py               # 服务端
│   │   ├── state_manager.py        # 状态管理
│   │   ├── auth.py                 # 认证授权
│   │   ├── pipeline_manager.py     # 管道管理
│   │   ├── resource_guard.py       # 资源保护
│   │   ├── instruction_parser.py   # 指令解析
│   │   ├── module_router.py        # 模块路由
│   │   ├── user_session.py         # 用户会话
│   │   └── validator.py            # 验证器
│   ├── services/                   # 业务服务层 ⭐
│   │   ├── video_pipeline.py       # 视频管道
│   │   ├── face_detection.py       # 人脸检测
│   │   ├── face_recognition.py     # 人脸识别
│   │   ├── face_swap.py            # 人脸替换
│   │   ├── camera_service.py       # 摄像头服务
│   │   ├── video_compositor.py     # 视频合成
│   │   ├── task_scheduler.py       # 任务调度 ⭐
│   │   ├── performance_monitor.py  # 性能监控 ⭐
│   │   └── local_ai_interface.py   # 本地AI接口
│   ├── database/                   # 数据库
│   │   └── db.py
│   └── utils/                      # 工具类
│       └── image_utils.py
│
├── ⚙️ engines/                      # 引擎抽象层 (L3)
│   └── engine_base.py              # 引擎基类
│
├── 📹 virtual_cam/                  # 输出层 (L3)
│   └── virtual_camera.py
│
├── 📺 obs_integration/              # 输出层 (L3)
│   └── obs_controller.py
│
├── 🌐 web/                          # Web监控层
│   ├── web_api.py                  # Web API
│   └── templates/                   # 模板
│
├── ⚙️ config/                       # 配置层 (L0-L4)
│   ├── *.json                      # 层级2配置
│   ├── ai/                         # 层级4配置
│   ├── tasks/                      # 层级4配置
│   └── data/                       # 同步状态
│
├── 📜 scripts/                      # 脚本目录
│   ├── *.sh                        # Shell脚本
│   └── *.py                        # Python脚本
│
├── 📁 data/                         # 数据目录
│   └── last_check_state.json
│
├── 📁 logs/                         # 日志目录
│
├── 📚 docs/                         # 文档目录
│   ├── README.md
│   ├── 项目结构说明.md
│   ├── 整体项目逻辑.md
│   ├── 模块依赖关系.md
│   └── ...
│
└── 🔧 根目录配置文件
    ├── .blackboxrules              # AI规则
    ├── .gitignore
    ├── AI_RULES.json               # 层级1
    ├── AI_PATH_CONTEXT.json        # 层级1
    ├── AI_CLEANUP_POLICY.json      # 层级1
    └── requirements.txt
```

### 2.3 数据流顺序（必须严格遵守）

```
1. GUI_INPUT      (gui/)
   ↓
2. BACKEND_API    (backend/unified_api.py)
   ↓
3. SERVICE_PROCESSING (backend/services/)
   ├─→ AI_CONTROL        (backend/ai_control/)
   │     ↓
   └─→ LOCAL_AI_INTERFACE (backend/services/local_ai_interface.py)
         ↓
4. ENGINE_EXECUTION   (backend/ar_engine/ → engines/)
   ↓
5. VIRTUAL_CAM_OUTPUT (virtual_cam/ → obs_integration/)
```

---

## 🔧 三、修复任务清单

### Phase 1: 配置清理与统一

#### 任务 1.1: 删除重复的配置文件

**操作**：
- 删除 `config/AI_RULES.json`
- 删除 `config/AI_PATH_CONTEXT.json`
- 删除 `config/AI_CLEANUP_POLICY.json`

**验证**：
- 确保根目录下的三个文件存在且正确
- 更新 `config/README.md` 说明

#### 任务 1.2: 补充缺失的配置字段

**操作**：为以下文件添加 `config_association` 和 `config_priority` 字段

| 文件 | 添加字段 |
|------|----------|
| config/daemon_guard_config.json | config_priority, config_association |
| config/resource_alert_config.json | config_priority, config_association |
| config/DOCS_SYNC_CONFIG.json | config_priority |
| config/run_config.example.json | meta, config_priority |

### Phase 2: 模块合并与优化

#### 任务 2.1: 合并性能监控模块

**操作**：
1. 将 `backend/control_core/monitor.py` 的功能合并到 `backend/services/performance_monitor.py`
2. 删除 `backend/control_core/monitor.py`
3. 更新 `backend/control_core/` 模块的导入

**合并逻辑**：
```python
# 在 performance_monitor.py 中添加
def get_control_core_status():
    """获取control_core状态（从原monitor.py迁移）"""
    return {
        "server_status": get_server_status(),
        "resource_usage": get_resource_usage()
    }
```

#### 任务 2.2: 合并任务执行模块

**操作**：
1. 将 `backend/services/task_executor.py` 的功能合并到 `backend/services/task_scheduler.py`
2. 删除 `backend/services/task_executor.py`
3. 更新相关导入

**合并逻辑**：
```python
# 在 task_scheduler.py 中添加 execute_task 方法
async def execute_task(self, task_id: str):
    """执行单个任务（原task_executor.py功能）"""
    # 实现从 task_queue.json 读取并执行
```

#### 任务 2.3: 合并数据存储模块

**操作**：
1. 将 `backend/ai_control/memory_store.py` 的功能合并到 `backend/ai_control/memory_db.py`
2. 删除 `backend/ai_control/memory_store.py`
3. 更新相关导入

**合并逻辑**：
```python
# 在 memory_db.py 中添加 JSON 存储方法
def store_json(self, key: str, data: dict):
    """存储JSON数据（原memory_store.py功能）"""
    # 使用 SQLite 的 JSON 支持或独立存储
```

#### 任务 2.4: 清理废弃的API入口

**操作**：
1. 确保 `backend/api.py` 正确重定向到 `backend/unified_api.py`
2. 更新启动脚本使用 `backend.unified_api:app`
3. 添加 DEPRECATED 警告

### Phase 3: 配置关联验证

#### 任务 3.1: 验证配置引用链

**验证**：
```bash
# 1. 检查所有配置文件都有 meta 字段
# 2. 检查 config_association.root_rules 指向正确的根规则
# 3. 检查 config_priority.level 正确
```

#### 任务 3.2: 更新文档同步状态

**操作**：
1. 运行配置验证脚本
2. 更新 `config/data/docs_sync_state.json`

### Phase 4: 数据流验证

#### 任务 4.1: 检查模块边界

**验证项**：
| 检查项 | 预期结果 |
|--------|----------|
| gui/ 是否直接调用 backend/services/* | ❌ 不允许 |
| backend/services/ 是否直接调用 gui/* | ❌ 不允许 |
| backend/ar_engine/ 是否直接调用 backend/control_core/* | ❌ 不允许 |

#### 任务 4.2: 验证导入依赖

**脚本**：创建验证脚本检查所有 Python 导入

---

## 📊 四、执行顺序与依赖

```
Phase 1: 配置清理
├── 1.1 删除重复配置文件 (无依赖)
├── 1.2 补充配置字段 (无依赖)
└── 1.3 更新 README (依赖1.1, 1.2)

Phase 2: 模块合并
├── 2.1 合并性能监控 (依赖1.1)
├── 2.2 合并任务执行 (依赖1.1)
├── 2.3 合并数据存储 (依赖1.1)
└── 2.4 清理废弃API (依赖1.1)

Phase 3: 配置验证
├── 3.1 验证配置引用 (依赖1.1, 1.2)
└── 3.2 更新同步状态 (依赖3.1)

Phase 4: 数据流验证
├── 4.1 检查模块边界 (依赖2.1, 2.2, 2.3)
└── 4.2 验证导入依赖 (依赖4.1)
```

---

## ✅ 五、验证清单

### 5.1 配置验证

- [ ] 所有配置文件都有 `meta` 字段
- [ ] 所有配置文件都有 `config_priority` 字段
- [ ] 所有配置文件都有 `config_association` 字段
- [ ] 层级1文件在根目录存在
- [ ] config/ 目录无层级1文件重复

### 5.2 模块验证

- [ ] 无重复功能模块
- [ ] 所有导入路径正确
- [ ] 无循环依赖
- [ ] 模块边界清晰

### 5.3 数据流验证

- [ ] 数据流顺序符合定义
- [ ] 无逆向调用
- [ ] API路由正确

### 5.4 功能验证

- [ ] 启动脚本能正常运行
- [ ] API端点可访问
- [ ] 配置文件能被正确加载

---

## 📝 六、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 删除文件导致错误 | 高 | 先备份，确认无依赖后再删除 |
| 模块合并引入bug | 中 | 充分测试，保留备份 |
| 配置字段遗漏 | 低 | 自动化检查工具验证 |

---

*创建时间: 2026-01-10*
*版本: 1.0.0*

