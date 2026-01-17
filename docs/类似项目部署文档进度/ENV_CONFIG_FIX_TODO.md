# 环境配置修复任务清单

## 任务概览
- **开始时间**: 2025-01-21
- **任务目标**: 修复所有环境配置问题

## 修复计划

### Phase 1: 清理重复配置文件
- [x] 1.1 分析`配置/`目录下的重复配置
- [ ] 1.2 删除`配置/config/AI_CLEANUP_POLICY.json` (与data/rules重复)
- [ ] 1.3 删除`配置/config/AI_RULES.json` (与data/rules/root_rules.json重复)
- [ ] 1.4 删除`配置/config/AI_PATH_CONTEXT.json` (与directory_structure.json冲突)
- [ ] 1.5 删除`配置/config/AI3.json`
- [ ] 1.6 删除`配置/config/auto_rule_checker.py`
- [ ] 1.7 删除`配置/config/docs_sync_engine.py`
- [ ] 1.8 删除`配置/config/config_loader.py`
- [ ] 1.9 删除`配置/backup/`目录下的重复备份文件
- [ ] 1.10 删除`配置/tasks/`目录下的任务文件

### Phase 2: 修复路径引用
- [ ] 2.1 更新`.blackboxrules`中的路径为`/workspaces/AISP`
- [ ] 2.2 更新`ai_task_config.json`中的项目路径
- [ ] 2.3 更新`logic_layers_deployment.json`中的项目路径
- [ ] 2.4 验证`directory_structure.json`中的路径引用

### Phase 3: 统一版本信息
- [ ] 3.1 统一`ai_task_config.json`版本为2.0.0
- [ ] 3.2 统一`data/rules/`目录下所有配置文件的版本为2.0.0
- [ ] 3.3 更新`.blackboxrules`版本为2.0.0

### Phase 4: 保留VSCode编辑器配置
- [ ] 4.1 保留`配置/extensions.json`
- [ ] 4.2 保留`配置/launch.json`
- [ ] 4.3 保留`配置/settings.json`
- [ ] 4.4 保留`配置/tasks.json`

### Phase 5: 验证修复
- [ ] 5.1 验证配置文件的JSON语法正确性
- [ ] 5.2 验证配置引用路径的一致性
- [ ] 5.3 生成配置修复报告

## 清理规则
- 以`data/rules/`目录为唯一权威配置源
- `配置/`目录仅保留VSCode相关的编辑器配置
- 所有规则类配置必须集中在`data/rules/`目录
- 项目路径统一为`/workspaces/AISP`

## 后续步骤
1. 执行配置清理
2. 同步更新相关文档
3. 验证配置一致性
4. 提交更改

