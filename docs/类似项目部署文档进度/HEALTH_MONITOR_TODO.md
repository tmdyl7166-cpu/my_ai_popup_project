# AISP 自动化健康监控系统 - 任务清单

## 任务目标
对Scripts中的自动化运行脚本进行识别优化，确保所有的功能脚本运行逻辑正确，并且检查是否有自动化健康检测脚本，对自动化健康检测脚本进行优化。

## 需求分析

### 核心功能需求
1. **自动启动监控** - 项目在VSC中启动后自动开启健康监控
2. **内容位置修正** - 自动检测并移动未放置在正确位置的内容
3. **文档实时检查** - 实时检查所有文档位置
4. **重复内容合并** - 对重复的代码、配置进行择优合并
5. **关联脚本更新** - 修正新添加/修改内容的关联脚本指向
6. **JSON配置同步** - 更新子项目JSON配置的认定规则
7. **上下文识别** - 确保修改后的内容指向性正确

## 实施计划

### Phase 1: 基础架构 (第1-2天)
- [ ] 1.1 创建 `scripts/project_health_monitor.py` - 统一监控系统主程序
- [ ] 1.2 创建 `scripts/auto/project_maintainer.py` - 项目维护器
- [ ] 1.3 创建 `scripts/auto/content_organizer.py` - 内容整理器
- [ ] 1.4 创建 `scripts/auto/duplicate_detector.py` - 重复内容检测器
- [ ] 1.5 创建 `scripts/auto/config_sync.py` - 配置同步器

### Phase 2: 核心功能 (第3-5天)
- [ ] 2.1 实现项目结构检查和自动修复
- [ ] 2.2 实现文档位置检查和自动整理
- [ ] 2.3 实现重复代码检测和合并
- [ ] 2.4 实现配置规则同步
- [ ] 2.5 实现关联脚本指向更新

### Phase 3: 上下文识别 (第6-7天)
- [ ] 3.1 实现函数和定义上下文识别
- [ ] 3.2 实现规则和配置上下文修正
- [ ] 3.3 实现内容指向性验证
- [ ] 3.4 实现自动修复机制

### Phase 4: 集成和测试 (第8-10天)
- [ ] 4.1 集成到现有启动脚本
- [ ] 4.2 集成到健康检测Web界面
- [ ] 4.3 添加轮询模式支持
- [ ] 4.4 添加守护进程模式支持
- [ ] 4.5 编写测试用例
- [ ] 4.6 更新文档

## 详细设计

### 文件结构
```
scripts/
├── project_health_monitor.py    # 统一监控系统主程序
├── health_check.py              # 健康检测（保留原有功能）
├── start_health_monitor.py      # 启动器（保留原有功能）
├── auto/
│   ├── __init__.py
│   ├── project_maintainer.py    # 项目维护器
│   ├── content_organizer.py     # 内容整理器
│   ├── duplicate_detector.py    # 重复内容检测器
│   ├── config_sync.py           # 配置同步器
│   └── context_analyzer.py      # 上下文分析器
└── config/
    └── health_monitor_config.json  # 监控配置
```

### 核心类设计

#### ProjectHealthMonitor
```python
class ProjectHealthMonitor:
    """项目健康监控主类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.components = {
            'health_checker': HealthChecker(),
            'project_maintainer': ProjectMaintainer(),
            'content_organizer': ContentOrganizer(),
            'duplicate_detector': DuplicateDetector(),
            'config_sync': ConfigSync(),
            'context_analyzer': ContextAnalyzer(),
        }
    
    def run_full_check(self) -> dict:
        """执行完整健康检查"""
        # ...
```

## 进度跟踪

### 每日更新
- [ ] 更新任务状态
- [ ] 记录遇到的问题
- [ ] 总结已完成的工作

## 验收标准

1. 所有自动化脚本运行逻辑正确
2. 健康检测脚本能自动启动
3. 能自动检测并修正内容位置
4. 能检测并合并重复内容
5. 能同步配置规则
6. 文档完整且更新

## 风险管理

| 风险 | 影响 | 应对措施 |
|-----|------|---------|
| 脚本冲突 | 中 | 统一入口，避免重复 |
| 性能影响 | 低 | 使用后台线程，限制频率 |
| 数据丢失 | 高 | 备份机制，dry-run模式 |

## 依赖项

- Python 3.10+
- psutil (系统监控)
- watchdog (文件监控)
- JSON (配置文件)

## 参考文档

- docs/健康检测说明.md
- docs/脚本启动说明.md
- scripts/README.md
- directory_structure.json

