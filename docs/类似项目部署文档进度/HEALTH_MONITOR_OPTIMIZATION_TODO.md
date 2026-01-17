# AISP 自动化健康监控优化计划

## 任务目标
对 Scripts 中的自动化运行脚本进行识别优化，确保所有功能脚本运行逻辑正确，并优化自动化健康检测脚本。

## 优化任务列表

### 阶段1: 创建统一入口和VSC集成
- [ ] 1.1 创建 `scripts/health_monitor_main.py` - 统一健康监控入口
- [ ] 1.2 创建 `scripts/auto/vsc_integrator.py` - VSC启动集成模块

### 阶段2: 增强内容整理器
- [ ] 2.1 创建 `scripts/auto/enhanced_organizer.py` - 增强内容整理器

### 阶段3: 增强重复检测合并
- [ ] 3.1 创建 `scripts/auto/enhanced_duplicate_detector.py` - 增强重复检测器

### 阶段4: 增强配置同步器
- [ ] 4.1 创建 `scripts/auto/enhanced_config_syncer.py` - 增强配置同步器

### 阶段5: 创建统一配置文件
- [ ] 5.1 创建 `config/health_monitor_enhanced.json` - 增强配置

### 阶段6: 更新启动脚本
- [ ] 6.1 更新 `scripts/start_health_monitor.py` - 支持VSC模式
- [ ] 6.2 更新 `scripts/config/health_monitor_config.json` - 添加新配置

### 阶段7: 创建集成脚本
- [ ] 7.1 创建 `scripts/start_all_monitors.sh` - 一键启动所有监控
- [ ] 7.2 更新 `scripts/README.md` - 文档更新

## 详细规范

### VSC集成规范
- 检测环境变量 `VSCODE_INJECTION` 或 `CODESPACES`
- 监听文件 `.vscode/extensions.txt` 变化
- 自动启动健康监控服务

### 增强功能规范
- 所有dry_run默认为True
- 支持 `--repair` 参数执行实际修改
- 支持 `--vsc` 参数启用VSC集成模式
- 所有修改自动备份到 `.backup/` 目录

## 执行顺序
1. 创建统一入口脚本
2. 创建VSC集成模块
3. 创建增强整理器
4. 创建增强重复检测器
5. 创建增强配置同步器
6. 创建统一配置文件
7. 更新启动脚本
8. 测试验证

