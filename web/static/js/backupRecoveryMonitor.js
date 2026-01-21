/**
 * Backup Recovery Monitor Module - 备份恢复监控模块
 * 管理数据备份、系统恢复和灾难恢复功能
 * 单一职责：备份管理和灾难恢复监控
 */

const BackupRecoveryMonitor = {
    // 状态
    state: {
        backups: [],
        recoveryPoints: [],
        schedules: [],
        isProcessing: false
    },

    // 配置
    config: {
        apiEndpoint: '/api/backup',
        restoreEndpoint: '/api/backup/restore',
        schedulesEndpoint: '/api/backup/schedules',
        logsEndpoint: '/api/backup/logs',
        refreshInterval: 30000,
        alertThresholds: {
            storageUsage: 80,  // 存储使用率告警
            backupAge: 168,    // 备份超过7天告警(小时)
            failedBackups: 3   // 连续失败次数告警
        }
    },

    // 备份类型
    backupTypes: [
        { id: 'full', name: '全量备份', icon: 'fa-database', color: 'primary' },
        { id: 'incremental', name: '增量备份', icon: 'fa-increment', color: 'success' },
        { id: 'differential', name: '差异备份', icon: 'fa-diff', color: 'info' }
    ],

    // 恢复状态
    restoreStatuses: [
        { id: 'idle', name: '就绪', icon: 'fa-check-circle', color: 'success' },
        { id: 'preparing', name: '准备中', icon: 'fa-spinner fa-spin', color: 'info' },
        { id: 'restoring', name: '恢复中', icon: 'fa-sync fa-spin', color: 'warning' },
        { id: 'completed', name: '已完成', icon: 'fa-check', color: 'success' },
        { id: 'failed', name: '失败', icon: 'fa-times', color: 'danger' }
    ],

    /**
     * 初始化备份恢复监控
     */
    init: function(containerId) {
        console.log('Backup Recovery Monitor initializing...');
        this.state.container = document.getElementById(containerId || 'backupRecoveryContent');

        if (!this.state.container) {
            console.error('Backup Recovery Monitor container not found');
            return;
        }

        this.render();
        this.loadData();
        this.startMonitoring();
    },

    /**
     * 渲染界面
     */
    render: function() {
        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        return `
            <div class="backup-recovery-monitor">
                <div class="card">
                    <div class="card-header bg-gradient-danger text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-life-ring me-2"></i>备份与灾难恢复
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="BackupRecoveryMonitor.loadData()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-light" onclick="BackupRecoveryMonitor.createBackup()">
                                <i class="fas fa-save me-1"></i>立即备份
                            </button>
                            <button class="btn btn-outline-light" onclick="BackupRecoveryMonitor.showRestoreWizard()">
                                <i class="fas fa-undo me-1"></i>恢复数据
                            </button>
                            <button class="btn btn-outline-light" onclick="BackupRecoveryMonitor.showScheduleManager()">
                                <i class="fas fa-clock me-1"></i>计划任务
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 统计概览 -->
                        <div class="row mb-3">
                            <div class="col-md-3">
                                <div class="card bg-primary text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="backupCount">0</h4>
                                        <small>备份总数</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-success text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="storageUsed">0 GB</h4>
                                        <small>已用存储</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-info text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="scheduleCount">0</h4>
                                        <small>计划任务</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-warning text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="lastBackupTime">--</h4>
                                        <small>最近备份</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 标签页 -->
                        <ul class="nav nav-tabs mb-3" role="tablist">
                            <li class="nav-item">
                                <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#backupList">
                                    <i class="fas fa-save me-1"></i>备份列表
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#recoveryPoints">
                                    <i class="fas fa-history me-1"></i>恢复点
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#backupSchedules">
                                    <i class="fas fa-clock me-1"></i>计划任务
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#backupLogs">
                                    <i class="fas fa-list-alt me-1"></i>备份日志
                                </button>
                            </li>
                        </ul>

                        <!-- 标签页内容 -->
                        <div class="tab-content">
                            <!-- 备份列表 -->
                            <div class="tab-pane fade show active" id="backupList">
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover" id="backupTable">
                                        <thead class="table-light">
                                            <tr>
                                                <th>类型</th>
                                                <th>名称</th>
                                                <th>大小</th>
                                                <th>创建时间</th>
                                                <th>状态</th>
                                                <th>操作</th>
                                            </tr>
                                        </thead>
                                        <tbody id="backupTableBody">
                                            ${this.buildBackupRows()}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- 恢复点 -->
                            <div class="tab-pane fade" id="recoveryPoints">
                                <div class="row" id="recoveryPointsContainer">
                                    ${this.buildRecoveryPointCards()}
                                </div>
                            </div>

                            <!-- 计划任务 -->
                            <div class="tab-pane fade" id="backupSchedules">
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover" id="scheduleTable">
                                        <thead class="table-light">
                                            <tr>
                                                <th>任务名称</th>
                                                <th>备份类型</th>
                                                <th>执行时间</th>
                                                <th>保留份数</th>
                                                <th>状态</th>
                                                <th>操作</th>
                                            </tr>
                                        </thead>
                                        <tbody id="scheduleTableBody">
                                            ${this.buildScheduleRows()}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- 备份日志 -->
                            <div class="tab-pane fade" id="backupLogs">
                                <div class="log-entries" id="backupLogsContainer" style="max-height: 300px; overflow-y: auto;">
                                    ${this.buildLogEntries()}
                                </div>
                            </div>
                        </div>

                        <!-- 灾难恢复面板 -->
                        <div class="disaster-recovery-section mt-3">
                            <div class="card border-danger">
                                <div class="card-header bg-danger text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-exclamation-triangle me-2"></i>灾难恢复
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="card">
                                                <div class="card-body text-center">
                                                    <i class="fas fa-undo fa-3x text-warning mb-2"></i>
                                                    <h6>系统回滚</h6>
                                                    <small class="text-muted">恢复到上一个稳定版本</small>
                                                    <button class="btn btn-warning btn-sm mt-2" onclick="BackupRecoveryMonitor.showRollbackWizard()">
                                <i class="fas fa-undo me-1"></i>执行回滚
                            </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card">
                                                <div class="card-body text-center">
                                                    <i class="fas fa-download fa-3x text-success mb-2"></i>
                                                    <h6>数据恢复</h6>
                                                    <small class="text-muted">从备份恢复数据</small>
                                                    <button class="btn btn-success btn-sm mt-2" onclick="BackupRecoveryMonitor.showDataRestoreWizard()">
                                <i class="fas fa-download me-1"></i>恢复数据
                            </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card">
                                                <div class="card-body text-center">
                                                    <i class="fas fa-copy fa-3x text-info mb-2"></i>
                                                    <h6>紧急克隆</h6>
                                                    <small class="text-muted">创建系统紧急克隆</small>
                                                    <button class="btn btn-info btn-sm mt-2" onclick="BackupRecoveryMonitor.createEmergencyClone()">
                                <i class="fas fa-copy me-1"></i>创建克隆
                            </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建备份表格行
     */
    buildBackupRows: function() {
        const backups = this.state.backups.length > 0 ? this.state.backups : this.getMockBackups();

        return backups.map(backup => {
            const typeInfo = this.backupTypes.find(t => t.id === backup.type) || { icon: 'fa-database', color: 'secondary' };
            return `
                <tr>
                    <td>
                        <span class="badge bg-${typeInfo.color}">
                            <i class="fas ${typeInfo.icon} me-1"></i>${backup.type_name}
                        </span>
                    </td>
                    <td>${backup.name}</td>
                    <td>${this.formatSize(backup.size)}</td>
                    <td>${this.formatTime(backup.created_at)}</td>
                    <td>
                        <span class="badge bg-${backup.status === 'completed' ? 'success' : backup.status === 'failed' ? 'danger' : 'warning'}">
                            ${backup.status === 'completed' ? '完成' : backup.status === 'failed' ? '失败' : '进行中'}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="BackupRecoveryMonitor.downloadBackup('${backup.id}')" title="下载">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-outline-success" onclick="BackupRecoveryMonitor.restoreFromBackup('${backup.id}')" title="恢复">
                                <i class="fas fa-undo"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="BackupRecoveryMonitor.deleteBackup('${backup.id}')" title="删除">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('') || `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i class="fas fa-save fa-2x mb-2"></i>
                    <p class="mb-0">暂无备份数据</p>
                    <small>点击"立即备份"创建第一个备份</small>
                </td>
            </tr>
        `;
    },

    /**
     * 构建恢复点卡片
     */
    buildRecoveryPointCards: function() {
        const points = this.state.recoveryPoints.length > 0 ? this.state.recoveryPoints : this.getMockRecoveryPoints();

        return points.map(point => `
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <strong>${point.name}</strong>
                        <span class="badge bg-${point.type === 'system' ? 'primary' : point.type === 'data' ? 'info' : 'success'}">
                            ${point.type === 'system' ? '系统' : point.type === 'data' ? '数据' : '配置'}
                        </span>
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <small class="text-muted">${point.description}</small>
                        </p>
                        <div class="d-flex justify-content-between mb-2">
                            <small>创建时间</small>
                            <small>${this.formatTime(point.created_at)}</small>
                        </div>
                        <div class="d-flex justify-content-between">
                            <small>版本</small>
                            <small>${point.version}</small>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-outline-primary btn-sm w-100" onclick="BackupRecoveryMonitor.restoreToPoint('${point.id}')">
                            <i class="fas fa-undo me-1"></i>恢复到该点
                        </button>
                    </div>
                </div>
            </div>
        `).join('') || `
            <div class="col-12 text-center text-muted py-4">
                <i class="fas fa-history fa-2x mb-2"></i>
                <p>暂无恢复点</p>
            </div>
        `;
    },

    /**
     * 构建计划任务行
     */
    buildScheduleRows: function() {
        const schedules = this.state.schedules.length > 0 ? this.state.schedules : this.getMockSchedules();

        return schedules.map(schedule => `
            <tr>
                <td>${schedule.name}</td>
                <td>
                    <span class="badge bg-${this.backupTypes.find(t => t.id === schedule.type)?.color || 'secondary'}">
                        ${schedule.type_name}
                    </span>
                </td>
                <td>${schedule.cron_expression}</td>
                <td>${schedule.retention}</td>
                <td>
                    <span class="badge bg-${schedule.enabled ? 'success' : 'secondary'}">
                        ${schedule.enabled ? '启用' : '禁用'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-${schedule.enabled ? 'warning' : 'success'}" 
                            onclick="BackupRecoveryMonitor.toggleSchedule('${schedule.id}')" title="${schedule.enabled ? '禁用' : '启用'}">
                            <i class="fas fa-${schedule.enabled ? 'pause' : 'play'}"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="BackupRecoveryMonitor.editSchedule('${schedule.id}')" title="编辑">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('') || `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i class="fas fa-clock fa-2x mb-2"></i>
                    <p class="mb-0">暂无计划任务</p>
                    <small>点击"计划任务"创建新任务</small>
                </td>
            </tr>
        `;
    },

    /**
     * 构建日志条目
     */
    buildLogEntries: function() {
        const logs = this.getMockLogs();
        return logs.map(log => `
            <div class="log-entry log-${log.level.toUpperCase()}">
                <span class="log-time">${this.formatTime(log.timestamp)}</span>
                <span class="log-level">${log.level.toUpperCase()}</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('') || '<div class="text-center text-muted py-3">暂无日志</div>';
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 事件已在HTML中处理
    },

    /**
     * 加载数据
     */
    loadData: async function() {
        try {
            // 加载备份数据
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            if (data.status === 'success') {
                this.state.backups = data.backups || [];
            }
        } catch (error) {
            console.warn('加载备份数据失败，使用模拟数据:', error);
            this.state.backups = this.getMockBackups();
        }

        this.updateDisplay();
    },

    /**
     * 更新显示
     */
    updateDisplay: function() {
        // 更新统计
        document.getElementById('backupCount').textContent = this.state.backups.length;
        
        const totalSize = this.state.backups.reduce((sum, b) => sum + (b.size || 0), 0);
        document.getElementById('storageUsed').textContent = this.formatSize(totalSize);
        
        document.getElementById('scheduleCount').textContent = this.state.schedules.length;
        
        const lastBackup = this.state.backups[0];
        document.getElementById('lastBackupTime').textContent = lastBackup 
            ? this.formatTime(lastBackup.created_at) 
            : '--';

        // 更新表格
        const backupBody = document.getElementById('backupTableBody');
        if (backupBody) {
            backupBody.innerHTML = this.buildBackupRows();
        }

        // 更新恢复点
        const recoveryContainer = document.getElementById('recoveryPointsContainer');
        if (recoveryContainer) {
            recoveryContainer.innerHTML = this.buildRecoveryPointCards();
        }

        // 更新计划任务
        const scheduleBody = document.getElementById('scheduleTableBody');
        if (scheduleBody) {
            scheduleBody.innerHTML = this.buildScheduleRows();
        }
    },

    /**
     * 创建备份
     */
    createBackup: async function() {
        if (this.state.isProcessing) {
            bubbleMonitor.show('info', '处理中', '请等待当前操作完成');
            return;
        }

        this.state.isProcessing = true;
        bubbleMonitor.show('info', '开始备份', '正在创建系统备份...');

        // 模拟备份过程
        await new Promise(resolve => setTimeout(resolve, 2000));

        const newBackup = {
            id: 'backup-' + Date.now(),
            name: '手动备份 ' + new Date().toLocaleString(),
            type: 'full',
            type_name: '全量备份',
            size: Math.floor(Math.random() * 10000) + 1000,
            status: 'completed',
            created_at: new Date().toISOString()
        };

        this.state.backups.unshift(newBackup);
        this.updateDisplay();

        this.state.isProcessing = false;
        bubbleMonitor.show('success', '备份完成', `备份 "${newBackup.name}" 已创建`);
    },

    /**
     * 显示恢复向导
     */
    showRestoreWizard: function() {
        const content = `
            <div class="restore-wizard">
                <div class="alert alert-info mb-3">
                    <i class="fas fa-info-circle me-2"></i>
                    选择要恢复的备份版本，系统将恢复到该时间点的状态。
                </div>
                <div class="mb-3">
                    <label class="form-label">选择备份</label>
                    <select class="form-select" id="restoreBackupSelect">
                        ${this.state.backups.map(backup => `
                            <option value="${backup.id}">${backup.name} (${this.formatTime(backup.created_at)})</option>
                        `).join('') || '<option value="">暂无备份</option>'}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">恢复选项</label>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="restoreData" checked>
                        <label class="form-check-label" for="restoreData">恢复数据</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="restoreConfig" checked>
                        <label class="form-check-label" for="restoreConfig">恢复配置</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="createRestorePoint" checked>
                        <label class="form-check-label" for="createRestorePoint">创建恢复点</label>
                    </div>
                </div>
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    警告：恢复操作将覆盖当前数据，请确认后执行。
                </div>
            </div>
        `;

        ModalManager.show({
            title: '数据恢复向导',
            content: content,
            size: 'lg',
            onConfirm: () => {
                const backupId = document.getElementById('restoreBackupSelect').value;
                this.executeRestore(backupId);
            }
        });
    },

    /**
     * 执行恢复
     */
    executeRestore: async function(backupId) {
        bubbleMonitor.show('info', '开始恢复', '正在恢复系统数据...');

        // 模拟恢复过程
        await new Promise(resolve => setTimeout(resolve, 3000));

        bubbleMonitor.show('success', '恢复完成', '系统数据已恢复到选定备份点');
    },

    /**
     * 显示计划任务管理器
     */
    showScheduleManager: function() {
        const content = `
            <div class="schedule-manager">
                <div class="mb-3">
                    <label class="form-label">任务名称</label>
                    <input type="text" class="form-control" id="scheduleName" placeholder="每日数据库备份">
                </div>
                <div class="mb-3">
                    <label class="form-label">备份类型</label>
                    <select class="form-select" id="scheduleType">
                        ${this.backupTypes.map(type => `
                            <option value="${type.id}">${type.name}</option>
                        `).join('')}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">执行时间 (Cron表达式)</label>
                    <input type="text" class="form-control" id="scheduleCron" value="0 2 * * *" placeholder="0 2 * * *">
                    <small class="text-muted">格式: 分 时 日 月 周 (默认每天凌晨2点)</small>
                </div>
                <div class="mb-3">
                    <label class="form-label">保留份数</label>
                    <input type="number" class="form-control" id="scheduleRetention" value="7" min="1" max="30">
                </div>
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="scheduleEnabled" checked>
                    <label class="form-check-label" for="scheduleEnabled">启用任务</label>
                </div>
            </div>
        `;

        ModalManager.show({
            title: '创建计划任务',
            content: content,
            size: 'md',
            onConfirm: () => {
                const name = document.getElementById('scheduleName').value;
                const type = document.getElementById('scheduleType').value;
                const cron = document.getElementById('scheduleCron').value;
                const retention = parseInt(document.getElementById('scheduleRetention').value);
                const enabled = document.getElementById('scheduleEnabled').checked;

                const newSchedule = {
                    id: 'schedule-' + Date.now(),
                    name: name,
                    type: type,
                    type_name: this.backupTypes.find(t => t.id === type)?.name || type,
                    cron_expression: cron,
                    retention: retention,
                    enabled: enabled,
                    next_run: new Date(Date.now() + 86400000).toISOString()
                };

                this.state.schedules.push(newSchedule);
                this.updateDisplay();

                bubbleMonitor.show('success', '任务创建成功', `计划任务 "${name}" 已创建`);
            }
        });
    },

    /**
     * 显示回滚向导
     */
    showRollbackWizard: function() {
        const content = `
            <div class="rollback-wizard">
                <div class="alert alert-danger mb-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>警告：</strong>系统回滚将恢复到上一个稳定版本，当前未保存的更改将丢失。
                </div>
                <div class="mb-3">
                    <label class="form-label">选择回滚版本</label>
                    <select class="form-select">
                        <option value="last-stable">上一个稳定版本 (推荐)</option>
                        <option value="last-backup">上一个备份版本</option>
                        <option value="custom">自定义版本...</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">回滚原因</label>
                    <select class="form-select">
                        <option value="bug">系统bug</option>
                        <option value="performance">性能问题</option>
                        <option value="compatibility">兼容性问题</option>
                        <option value="other">其他</option>
                    </select>
                </div>
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="confirmRollback" required>
                    <label class="form-check-label" for="confirmRollback">
                        我确认理解回滚的影响，并愿意执行此操作
                    </label>
                </div>
            </div>
        `;

        ModalManager.show({
            title: '系统回滚向导',
            content: content,
            size: 'md',
            onConfirm: () => {
                const confirmed = document.getElementById('confirmRollback')?.checked;
                if (!confirmed) {
                    bubbleMonitor.show('warning', '需确认', '请勾选确认框以继续');
                    return false;
                }
                this.executeRollback();
            }
        });
    },

    /**
     * 执行回滚
     */
    executeRollback: async function() {
        bubbleMonitor.show('info', '开始回滚', '正在执行系统回滚...');

        // 模拟回滚过程
        await new Promise(resolve => setTimeout(resolve, 3000));

        bubbleMonitor.show('success', '回滚完成', '系统已回滚到上一个稳定版本');
    },

    /**
     * 显示数据恢复向导
     */
    showDataRestoreWizard: function() {
        this.showRestoreWizard();
    },

    /**
     * 创建紧急克隆
     */
    createEmergencyClone: async function() {
        bubbleMonitor.show('info', '创建克隆', '正在创建系统紧急克隆...');

        await new Promise(resolve => setTimeout(resolve, 2000));

        bubbleMonitor.show('success', '克隆创建成功', '紧急克隆已创建，保留30天');
    },

    /**
     * 下载备份
     */
    downloadBackup: function(backupId) {
        bubbleMonitor.show('info', '下载中', '正在准备备份文件下载...');
        // 实际实现中应该触发下载
    },

    /**
     * 从备份恢复
     */
    restoreFromBackup: function(backupId) {
        this.showRestoreWizard();
    },

    /**
     * 删除备份
     */
    deleteBackup: function(backupId) {
        const backup = this.state.backups.find(b => b.id === backupId);
        if (!backup) return;

        ModalManager.confirm({
            title: '确认删除',
            content: `确定要删除备份 "${backup.name}" 吗？此操作不可恢复。`,
            onConfirm: () => {
                this.state.backups = this.state.backups.filter(b => b.id !== backupId);
                this.updateDisplay();
                bubbleMonitor.show('success', '删除成功', '备份已删除');
            }
        });
    },

    /**
     * 恢复到恢复点
     */
    restoreToPoint: function(pointId) {
        const point = this.state.recoveryPoints.find(p => p.id === pointId);
        if (!point) return;

        ModalManager.confirm({
            title: '确认恢复',
            content: `确定要恢复到恢复点 "${point.name}" 吗？当前数据将被覆盖。`,
            onConfirm: () => {
                bubbleMonitor.show('info', '恢复中', `正在恢复到 ${point.name}...`);
                setTimeout(() => {
                    bubbleMonitor.show('success', '恢复完成', `已恢复到 ${point.name}`);
                }, 2000);
            }
        });
    },

    /**
     * 切换计划任务状态
     */
    toggleSchedule: function(scheduleId) {
        const schedule = this.state.schedules.find(s => s.id === scheduleId);
        if (!schedule) return;

        schedule.enabled = !schedule.enabled;
        this.updateDisplay();

        bubbleMonitor.show(
            schedule.enabled ? 'success' : 'warning',
            schedule.enabled ? '任务已启用' : '任务已禁用',
            schedule.name
        );
    },

    /**
     * 编辑计划任务
     */
    editSchedule: function(scheduleId) {
        const schedule = this.state.schedules.find(s => s.id === scheduleId);
        if (!schedule) return;

        this.showScheduleManager();
    },

    /**
     * 获取模拟备份数据
     */
    getMockBackups: function() {
        return [
            {
                id: 'backup-001',
                name: '自动每日备份',
                type: 'full',
                type_name: '全量备份',
                size: 5242880,
                status: 'completed',
                created_at: new Date(Date.now() - 86400000).toISOString()
            },
            {
                id: 'backup-002',
                name: '手动配置备份',
                type: 'incremental',
                type_name: '增量备份',
                size: 1048576,
                status: 'completed',
                created_at: new Date(Date.now() - 172800000).toISOString()
            }
        ];
    },

    /**
     * 获取模拟恢复点数据
     */
    getMockRecoveryPoints: function() {
        return [
            {
                id: 'point-001',
                name: '系统安装完成',
                type: 'system',
                description: '初始系统配置完成',
                version: 'v1.0.0',
                created_at: new Date(Date.now() - 604800000).toISOString()
            },
            {
                id: 'point-002',
                name: '安全配置更新',
                type: 'config',
                description: '安全策略配置更新',
                version: 'v1.1.0',
                created_at: new Date(Date.now() - 259200000).toISOString()
            }
        ];
    },

    /**
     * 获取模拟计划任务数据
     */
    getMockSchedules: function() {
        return [
            {
                id: 'schedule-001',
                name: '每日数据库备份',
                type: 'incremental',
                type_name: '增量备份',
                cron_expression: '0 2 * * *',
                retention: 7,
                enabled: true
            },
            {
                id: 'schedule-002',
                name: '每周全量备份',
                type: 'full',
                type_name: '全量备份',
                cron_expression: '0 3 * * 0',
                retention: 4,
                enabled: true
            }
        ];
    },

    /**
     * 获取模拟日志数据
     */
    getMockLogs: function() {
        return [
            { timestamp: new Date().toISOString(), level: 'info', message: '备份任务执行完成' },
            { timestamp: new Date(Date.now() - 3600000).toISOString(), level: 'success', message: '增量备份成功, 耗时 45秒' },
            { timestamp: new Date(Date.now() - 7200000).toISOString(), level: 'warning', message: '存储空间使用率 75%' },
            { timestamp: new Date(Date.now() - 86400000).toISOString(), level: 'info', message: '计划备份任务已执行' }
        ];
    },

    /**
     * 格式化大小
     */
    formatSize: function(bytes) {
        if (!bytes) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let unitIndex = 0;
        let size = bytes;
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        return size.toFixed(1) + ' ' + units[unitIndex];
    },

    /**
     * 格式化时间
     */
    formatTime: function(isoString) {
        if (!isoString) return '--';
        const date = new Date(isoString);
        return date.toLocaleString('zh-CN');
    },

    /**
     * 开始监控
     */
    startMonitoring: function() {
        this.state.interval = setInterval(() => {
            this.loadData();
        }, this.config.refreshInterval);
    },

    /**
     * 停止监控
     */
    stopMonitoring: function() {
        if (this.state.interval) {
            clearInterval(this.state.interval);
            this.state.interval = null;
        }
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        return {
            backupCount: this.state.backups.length,
            scheduleCount: this.state.schedules.length,
            storageUsed: this.state.backups.reduce((sum, b) => sum + (b.size || 0), 0)
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Backup Recovery Monitor destroying...');
        this.stopMonitoring();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.BackupRecoveryMonitor = BackupRecoveryMonitor;

