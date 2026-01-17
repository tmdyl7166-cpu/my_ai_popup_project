# 夜灵AR多功能合成软件 任务文档索引

> 本文档是夜灵AR多功能合成软件项目所有任务和待办事项的唯一索引
> **重要**：所有任务来源必须来自本文档或 `config/tasks/task_queue.json`
> 
> 文档版本: 1.0.0
> 最后更新: 2025-01-21

---

## 任务来源

| 来源 | 说明 | 优先级 |
|------|------|--------|
| **本文档** | 所有待完成任务清单 | 最高 |
| `config/tasks/task_queue.json` | 结构化任务队列 | 最高 |
| `config/tasks/completed_tasks.json` | 已完成任务记录 | 参考 |

---

## 待完成任务

### 核心任务

| ID | 任务 | 模块 | 状态 | 优先级 |
|----|------|------|------|--------|
| - | 无核心待完成任务 | - | - | - |

### TODO文档清单

| 文档 | 状态 | 说明 |
|------|------|------|
| `TODO.md` | ✅ 已完成 | 主任务来源 |
| `TODO_AR_CONFIG_DIALOG.md` | ✅ 已完成 | AR配置对话框任务 |
| `TODO_AR_SYNTHESIS.md` | ⏳ 待评估 | AR合成任务 |
| `TODO_CLEANUP_REDEPLOY.md` | ✅ 已完成 | 清理重新部署 |
| `TODO_CONFIG_OPTIMIZATION.md` | ✅ 已完成 | 配置优化 |
| `TODO_HEALTH_CHECK_OPTIMIZATION.md` | ⏳ 待评估 | 健康检查优化 |

### 优化任务

| ID | 任务 | 状态 | 说明 |
|----|------|------|------|
| - | 无优化任务 | - | - |

---

## 任务管理流程

```
TODO.md / task_queue.json
         │
         ▼
    读取任务
         │
         ▼
    按优先级执行
         │
         ▼
    更新 completed_tasks.json
         │
         ▼
    同步到 docs/任务文档索引.md
```

---

## 相关文档

- [任务队列](../config/tasks/task_queue.json) - 结构化任务队列
- [已完成任务](../config/tasks/completed_tasks.json) - 已完成任务记录
- [项目结构说明](项目结构说明.md) - 模块结构
- [整体项目逻辑](整体项目逻辑.md) - 数据流

---

*文档版本: 1.0.0*
*最后更新: 2025-01-21*
