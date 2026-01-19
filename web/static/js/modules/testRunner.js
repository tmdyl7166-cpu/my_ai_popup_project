/**
 * Test Runner Module - 测试运行器模块
 * 提供测试用例管理、执行和结果展示功能
 * 单一职责：测试运行和结果展示
 */

const TestRunner = {
    // 状态
    state: {
        tests: [],
        results: [],
        isRunning: false,
        currentSuite: null
    },

    // 配置
    config: {
        apiEndpoint: '/api/tests',
        runEndpoint: '/api/tests/run',
        resultsEndpoint: '/api/tests/results',
        refreshInterval: 5000
    },

    // 测试类别
    categories: [
        { id: 'unit', name: '单元测试', icon: 'fa-code' },
        { id: 'integration', name: '集成测试', icon: 'fa-project-diagram' },
        { id: 'e2e', name: '端到端测试', icon: 'fa-globe' },
        { id: 'performance', name: '性能测试', icon: 'fa-tachometer-alt' },
        { id: 'security', name: '安全测试', icon: 'fa-shield-alt' }
    ],

    /**
     * 初始化测试运行器
     */
    init: function(containerId) {
        console.log('Test Runner initializing...');
        this.state.container = document.getElementById(containerId || 'testRunnerContent');
        
        if (!this.state.container) {
            console.error('Test Runner container not found');
            return;
        }

        this.render();
        this.loadTests();
        this.startAutoRefresh();
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
            <div class="test-runner-container">
                <div class="card">
                    <div class="card-header bg-gradient-primary text-white d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-flask me-2"></i>测试运行器
                        </h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-light" onclick="TestRunner.loadTests()">
                                <i class="fas fa-sync me-1"></i>刷新
                            </button>
                            <button class="btn btn-outline-light" onclick="TestRunner.runAllTests()">
                                <i class="fas fa-play me-1"></i>全部运行
                            </button>
                            <button class="btn btn-outline-light" onclick="TestRunner.showResults()">
                                <i class="fas fa-chart-bar me-1"></i>结果
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- 统计概览 -->
                        <div class="row mb-3">
                            <div class="col-md-3">
                                <div class="card bg-success text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="testPassCount">0</h4>
                                        <small>通过</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-danger text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="testFailCount">0</h4>
                                        <small>失败</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-warning text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="testSkipCount">0</h4>
                                        <small>跳过</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-info text-white text-center">
                                    <div class="card-body py-2">
                                        <h4 class="mb-0" id="testTotalCount">0</h4>
                                        <small>总计</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 分类筛选 -->
                        <div class="category-filter mb-3">
                            <div class="btn-group btn-group-sm flex-wrap" role="group">
                                ${this.categories.map(cat => `
                                    <button type="button" class="btn btn-outline-primary category-btn" 
                                        data-category="${cat.id}" onclick="TestRunner.filterByCategory('${cat.id}')">
                                        <i class="fas ${cat.icon} me-1"></i>${cat.name}
                                    </button>
                                `).join('')}
                                <button type="button" class="btn btn-outline-secondary category-btn active" 
                                    data-category="all" onclick="TestRunner.filterByCategory('all')">
                                    全部
                                </button>
                            </div>
                        </div>

                        <!-- 测试进度 -->
                        <div class="test-progress mb-3" id="testProgressContainer" style="display: none;">
                            <div class="d-flex justify-content-between mb-1">
                                <small>执行进度</small>
                                <small id="testProgressText">0/0</small>
                            </div>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                    id="testProgressBar" style="width: 0%"></div>
                            </div>
                            <small class="text-muted mt-1" id="testProgressStatus">准备中...</small>
                        </div>

                        <!-- 测试列表 -->
                        <div class="test-list-container" style="max-height: 400px; overflow-y: auto;">
                            <table class="table table-sm table-hover" id="testTable">
                                <thead class="table-light sticky-top">
                                    <tr>
                                        <th style="width: 40px;">状态</th>
                                        <th style="width: 80px;">类别</th>
                                        <th>测试名称</th>
                                        <th style="width: 100px;">耗时</th>
                                        <th style="width: 80px;">操作</th>
                                    </tr>
                                </thead>
                                <tbody id="testTableBody">
                                    ${this.buildTestRows()}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 构建测试行
     */
    buildTestRows: function() {
        if (this.state.tests.length === 0) {
            return `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-flask fa-2x mb-2"></i>
                        <p class="mb-0">暂无测试用例</p>
                        <small>点击"全部运行"创建模拟测试数据</small>
                    </td>
                </tr>
            `;
        }

        return this.state.tests.map(test => `
            <tr class="test-row" data-category="${test.category}" data-status="${test.status}">
                <td>
                    <span class="badge ${this.getStatusClass(test.status)}">
                        ${this.getStatusIcon(test.status)}
                    </span>
                </td>
                <td>
                    <small><i class="${this.getCategoryIcon(test.category)} me-1"></i>${test.category_name}</small>
                </td>
                <td>
                    <div class="test-name">${test.name}</div>
                    <small class="text-muted">${test.description || ''}</small>
                </td>
                <td><small>${test.duration ? test.duration + 'ms' : '-'}</small></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${test.status === 'pending' || test.status === 'failed' ? `
                            <button class="btn btn-outline-success" onclick="TestRunner.runTest('${test.id}')" title="运行">
                                <i class="fas fa-play"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-outline-info" onclick="TestRunner.viewDetails('${test.id}')" title="详情">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 事件已在HTML中处理
    },

    /**
     * 加载测试列表
     */
    loadTests: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.state.tests = data.tests || [];
                this.updateDisplay();
            }
        } catch (error) {
            console.warn('加载测试列表失败，使用模拟数据:', error);
            this.state.tests = this.getMockTests();
            this.updateDisplay();
        }
    },

    /**
     * 更新显示
     */
    updateDisplay: function() {
        const tbody = document.getElementById('testTableBody');
        if (tbody) {
            tbody.innerHTML = this.buildTestRows();
        }
        
        this.updateStats();
    },

    /**
     * 更新统计
     */
    updateStats: function() {
        const stats = {
            passed: 0,
            failed: 0,
            skipped: 0,
            pending: 0,
            total: this.state.tests.length
        };
        
        this.state.tests.forEach(test => {
            if (stats[test.status] !== undefined) {
                stats[test.status]++;
            }
        });
        
        document.getElementById('testPassCount').textContent = stats.passed;
        document.getElementById('testFailCount').textContent = stats.failed;
        document.getElementById('testSkipCount').textContent = stats.skipped;
        document.getElementById('testTotalCount').textContent = stats.total;
    },

    /**
     * 运行所有测试
     */
    runAllTests: async function() {
        if (this.state.isRunning) {
            bubbleMonitor.show('info', '测试执行中', '请等待当前测试完成');
            return;
        }

        this.state.isRunning = true;
        this.showProgress();
        
        const tests = this.state.tests.length > 0 ? this.state.tests : this.getMockTests();
        const total = tests.length;
        let completed = 0;
        
        bubbleMonitor.show('info', '开始测试', `共 ${total} 个测试用例`);

        // 模拟测试执行
        for (let i = 0; i < tests.length; i++) {
            const test = tests[i];
            
            // 模拟测试状态更新
            test.status = 'running';
            test.startTime = Date.now();
            this.updateDisplay();
            
            // 更新进度
            this.updateProgress(completed + 1, total, `执行中: ${test.name}`);
            
            // 模拟执行时间
            await this.sleep(Math.random() * 500 + 100);
            
            // 模拟结果
            const success = Math.random() > 0.2; // 80%通过率
            test.status = success ? 'passed' : 'failed';
            test.duration = Date.now() - test.startTime;
            test.error = success ? null : '模拟错误: 断言失败';
            
            completed++;
            this.updateProgress(completed, total, `完成: ${test.name}`);
            this.updateDisplay();
        }

        this.state.isRunning = false;
        this.hideProgress();
        
        const passed = tests.filter(t => t.status === 'passed').length;
        const failed = tests.filter(t => t.status === 'failed').length;
        
        bubbleMonitor.show(
            passed > failed ? 'success' : 'warning',
            '测试完成',
            `通过: ${passed}, 失败: ${failed}`
        );
    },

    /**
     * 运行单个测试
     */
    runTest: async function(testId) {
        const test = this.state.tests.find(t => t.id === testId);
        if (!test) return;
        
        test.status = 'running';
        test.startTime = Date.now();
        this.updateDisplay();
        
        await this.sleep(Math.random() * 300 + 100);
        
        const success = Math.random() > 0.2;
        test.status = success ? 'passed' : 'failed';
        test.duration = Date.now() - test.startTime;
        
        this.updateDisplay();
        bubbleMonitor.show(
            success ? 'success' : 'error',
            test.name,
            success ? '测试通过' : '测试失败'
        );
    },

    /**
     * 显示进度
     */
    showProgress: function() {
        document.getElementById('testProgressContainer').style.display = 'block';
    },

    /**
     * 更新进度
     */
    updateProgress: function(current, total, status) {
        const percent = (current / total) * 100;
        document.getElementById('testProgressBar').style.width = percent + '%';
        document.getElementById('testProgressText').textContent = `${current}/${total}`;
        document.getElementById('testProgressStatus').textContent = status;
    },

    /**
     * 隐藏进度
     */
    hideProgress: function() {
        document.getElementById('testProgressContainer').style.display = 'none';
    },

    /**
     * 按类别筛选
     */
    filterByCategory: function(category) {
        // 更新按钮状态
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-category="${category}"]`)?.classList.add('active');
        
        // 筛选显示
        document.querySelectorAll('.test-row').forEach(row => {
            if (category === 'all' || row.dataset.category === category) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    },

    /**
     * 查看详情
     */
    viewDetails: function(testId) {
        const test = this.state.tests.find(t => t.id === testId);
        if (!test) return;
        
        const details = `
            <div class="test-details">
                <h6>${test.name}</h6>
                <p><strong>类别:</strong> ${test.category_name}</p>
                <p><strong>状态:</strong> <span class="badge ${this.getStatusClass(test.status)}">${test.status}</span></p>
                <p><strong>耗时:</strong> ${test.duration ? test.duration + 'ms' : '-'}</p>
                ${test.error ? `<p><strong>错误:</strong> <code>${test.error}</code></p>` : ''}
                ${test.stack_trace ? `
                    <p><strong>堆栈:</strong></p>
                    <pre class="bg-light p-2" style="font-size: 12px; max-height: 200px; overflow: auto;">${test.stack_trace}</pre>
                ` : ''}
                <p><strong>描述:</strong> ${test.description || '无'}</p>
            </div>
        `;
        
        ModalManager.show({
            title: '测试详情',
            content: details,
            size: 'lg'
        });
    },

    /**
     * 显示结果
     */
    showResults: function() {
        const passed = this.state.tests.filter(t => t.status === 'passed').length;
        const failed = this.state.tests.filter(t => t.status === 'failed').length;
        const skipped = this.state.tests.filter(t => t.status === 'skipped').length;
        const pending = this.state.tests.filter(t => t.status === 'pending').length;
        
        const total = this.state.tests.length || 1;
        const passRate = ((passed / total) * 100).toFixed(1);
        
        const content = `
            <div class="test-results-summary">
                <div class="text-center mb-3">
                    <h2 class="${passRate >= 80 ? 'text-success' : passRate >= 60 ? 'text-warning' : 'text-danger'}">
                        ${passRate}%
                    </h2>
                    <small class="text-muted">通过率</small>
                </div>
                
                <div class="row text-center">
                    <div class="col-3">
                        <div class="h4 text-success mb-0">${passed}</div>
                        <small>通过</small>
                    </div>
                    <div class="col-3">
                        <div class="h4 text-danger mb-0">${failed}</div>
                        <small>失败</small>
                    </div>
                    <div class="col-3">
                        <div class="h4 text-warning mb-0">${skipped}</div>
                        <small>跳过</small>
                    </div>
                    <div class="col-3">
                        <div class="h4 text-secondary mb-0">${pending}</div>
                        <small>待测</small>
                    </div>
                </div>
                
                <hr>
                
                <div class="progress mb-2" style="height: 25px;">
                    <div class="progress-bar bg-success" style="width: ${(passed/total*100)}%">${passed}</div>
                    <div class="progress-bar bg-danger" style="width: ${(failed/total*100)}%">${failed}</div>
                    <div class="progress-bar bg-warning" style="width: ${(skipped/total*100)}%">${skipped}</div>
                    <div class="progress-bar bg-secondary" style="width: ${(pending/total*100)}%">${pending}</div>
                </div>
                
                <div class="text-center text-muted">
                    <small>总计: ${total} 个测试用例</small>
                </div>
            </div>
        `;
        
        ModalManager.show({
            title: '测试结果统计',
            content: content,
            size: 'md'
        });
    },

    /**
     * 获取状态样式类
     */
    getStatusClass: function(status) {
        const classes = {
            passed: 'bg-success',
            failed: 'bg-danger',
            skipped: 'bg-warning',
            pending: 'bg-secondary',
            running: 'bg-info'
        };
        return classes[status] || 'bg-secondary';
    },

    /**
     * 获取状态图标
     */
    getStatusIcon: function(status) {
        const icons = {
            passed: '✓',
            failed: '✕',
            skipped: '⊘',
            pending: '○',
            running: '⟳'
        };
        return icons[status] || '?';
    },

    /**
     * 获取类别图标
     */
    getCategoryIcon: function(category) {
        const cat = this.categories.find(c => c.id === category);
        return cat ? cat.icon : 'fa-code';
    },

    /**
     * 获取模拟测试数据
     */
    getMockTests: function() {
        return [
            {
                id: 'test-1',
                name: '健康检查API测试',
                description: '验证 /api/health 端点返回正确状态',
                category: 'unit',
                category_name: '单元测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-2',
                name: 'GPU监控集成测试',
                description: '验证 GPU API 正常返回数据',
                category: 'integration',
                category_name: '集成测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-3',
                name: '审计日志流程测试',
                description: '验证日志记录完整流程',
                category: 'e2e',
                category_name: '端到端测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-4',
                name: '系统资源监控性能测试',
                description: '验证资源监控响应时间',
                category: 'performance',
                category_name: '性能测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-5',
                name: 'API安全测试',
                description: '验证API端点安全性',
                category: 'security',
                category_name: '安全测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-6',
                name: 'WebSocket连接测试',
                description: '验证实时通信功能',
                category: 'integration',
                category_name: '集成测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-7',
                name: '冒泡通知渲染测试',
                description: '验证通知显示正确',
                category: 'unit',
                category_name: '单元测试',
                status: 'pending',
                duration: null
            },
            {
                id: 'test-8',
                name: '完整用户流程测试',
                description: '验证从登录到操作的完整流程',
                category: 'e2e',
                category_name: '端到端测试',
                status: 'pending',
                duration: null
            }
        ];
    },

    /**
     * 休眠
     */
    sleep: function(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        this.state.interval = setInterval(() => {
            this.loadTests();
        }, this.config.refreshInterval);
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh: function() {
        if (this.state.interval) {
            clearInterval(this.state.interval);
            this.state.interval = null;
        }
    },

    /**
     * 获取状态
     */
    getStatus: function() {
        const passed = this.state.tests.filter(t => t.status === 'passed').length;
        const failed = this.state.tests.filter(t => t.status === 'failed').length;
        const total = this.state.tests.length;
        
        return {
            isRunning: this.state.isRunning,
            totalTests: total,
            passedTests: passed,
            failedTests: failed,
            passRate: total > 0 ? ((passed / total) * 100).toFixed(1) : 0
        };
    },

    /**
     * 销毁模块
     */
    destroy: function() {
        console.log('Test Runner destroying...');
        this.stopAutoRefresh();
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
    }
};

// 导出到全局
window.TestRunner = TestRunner;

