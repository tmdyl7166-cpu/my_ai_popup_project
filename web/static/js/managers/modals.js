/**
 * Modals Manager
 * Handles modal dialog management
 */
window.ModalsModule = (function() {
    // Active modal reference
    let activeModal = null;

    /**
     * Initialize modals module
     */
    function init() {
        console.log('ModalsModule initialized');
        this.bindGlobalEvents();
    }

    /**
     * Bind global events
     */
    function bindGlobalEvents() {
        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.hideAll();
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAll();
            }
        });
    }

    /**
     * Show script details modal
     */
    function showScriptDetails(script) {
        const modal = this.createModal({
            title: `${script.display_name} - 脚本详情`,
            size: 'lg',
            body: this.generateScriptDetailsBody(script),
            footer: this.generateScriptDetailsFooter(script)
        });

        document.body.appendChild(modal);
        activeModal = modal;

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Cleanup on hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (activeModal === modal) activeModal = null;
        });
    }

    /**
     * Generate script details body HTML
     */
    function generateScriptDetailsBody(script) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <h6>基本信息</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>名称:</strong></td>
                            <td>${escapeHtml(script.display_name)}</td>
                        </tr>
                        <tr>
                            <td><strong>标识符:</strong></td>
                            <td><code>${escapeHtml(script.name)}</code></td>
                        </tr>
                        <tr>
                            <td><strong>状态:</strong></td>
                            <td><span class="badge ${this.getStatusClass(script.status)}">${script.status}</span></td>
                        </tr>
                        <tr>
                            <td><strong>执行频率:</strong></td>
                            <td>${escapeHtml(script.frequency)}</td>
                        </tr>
                        ${script.last_run ? `
                        <tr>
                            <td><strong>上次运行:</strong></td>
                            <td>${new Date(script.last_run * 1000).toLocaleString()}</td>
                        </tr>
                        ` : ''}
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>描述</h6>
                    <p class="text-muted">${escapeHtml(script.description || '暂无描述')}</p>
                    <h6 class="mt-3">操作</h6>
                    <div class="btn-group-vertical w-100">
                        <button class="btn btn-outline-primary btn-sm" onclick="ModalsModule.runScriptFromModal('${script.name}')">
                            <i class="fas fa-play me-1"></i> 运行脚本
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="ModalsModule.viewLogsFromModal('${script.name}')">
                            <i class="fas fa-file-alt me-1"></i> 查看日志
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generate script details footer
     */
    function generateScriptDetailsFooter(script) {
        return `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times me-1"></i> 关闭
            </button>
            <button type="button" class="btn btn-primary" onclick="ModalsModule.runScriptFromModal('${script.name}')">
                <i class="fas fa-play me-1"></i> 运行脚本
            </button>
        `;
    }

    /**
     * Show confirmation dialog
     */
    function showConfirm(title, message, onConfirm, options = {}) {
        const modal = this.createModal({
            title: title,
            size: options.size || 'md',
            body: `
                <div class="text-center py-3">
                    <i class="fas fa-exclamation-triangle text-warning" style="font-size: 3em;"></i>
                    <p class="mt-3">${message}</p>
                </div>
            `,
            footer: `
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-1"></i> 取消
                </button>
                <button type="button" class="btn btn-danger" id="confirm-btn">
                    <i class="fas fa-check me-1"></i> 确认
                </button>
            `
        });

        document.body.appendChild(modal);
        activeModal = modal;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Bind confirm button
        document.getElementById('confirm-btn').onclick = () => {
            bsModal.hide();
            if (typeof onConfirm === 'function') {
                onConfirm();
            }
        };

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (activeModal === modal) activeModal = null;
        });
    }

    /**
     * Show input dialog
     */
    function showInput(title, label, placeholder, onSubmit, options = {}) {
        const modal = this.createModal({
            title: title,
            size: options.size || 'md',
            body: `
                <div class="py-3">
                    <label class="form-label">${label}</label>
                    <input type="text" class="form-control" id="modal-input" placeholder="${placeholder || ''}" value="${options.defaultValue || ''}">
                </div>
            `,
            footer: `
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-1"></i> 取消
                </button>
                <button type="button" class="btn btn-primary" id="submit-btn">
                    <i class="fas fa-check me-1"></i> 确认
                </button>
            `
        });

        document.body.appendChild(modal);
        activeModal = modal;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Focus input
        setTimeout(() => {
            const input = document.getElementById('modal-input');
            if (input) input.focus();
        }, 100);

        // Bind submit button and Enter key
        const submit = () => {
            const value = document.getElementById('modal-input').value;
            bsModal.hide();
            if (typeof onSubmit === 'function') {
                onSubmit(value);
            }
        };

        document.getElementById('submit-btn').onclick = submit;
        document.getElementById('modal-input').onkeypress = (e) => {
            if (e.key === 'Enter') submit();
        };

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (activeModal === modal) activeModal = null;
        });
    }

    /**
     * Show system info modal
     */
    function showSystemInfo(data) {
        const modal = this.createModal({
            title: '系统信息',
            size: 'lg',
            body: `
                <div class="row">
                    <div class="col-md-6">
                        <h6>CPU</h6>
                        <div class="progress mb-3" style="height: 25px;">
                            <div class="progress-bar bg-primary" style="width: ${data.cpu_percent}%">
                                ${data.cpu_percent.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>内存</h6>
                        <div class="progress mb-3" style="height: 25px;">
                            <div class="progress-bar bg-success" style="width: ${data.memory.percent}%">
                                ${data.memory.percent.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>磁盘</h6>
                        <div class="progress mb-3" style="height: 25px;">
                            <div class="progress-bar bg-warning" style="width: ${data.disk.percent}%">
                                ${data.disk.percent.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>更新时间</h6>
                        <p class="text-muted">${new Date(data.timestamp).toLocaleString()}</p>
                    </div>
                </div>
            `,
            footer: `
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-1"></i> 关闭
                </button>
            `
        });

        document.body.appendChild(modal);
        activeModal = modal;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            if (activeModal === modal) activeModal = null;
        });
    }

    /**
     * Create modal HTML
     */
    function createModal(options) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = `modal-${Date.now()}`;
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');

        const sizeClass = options.size === 'lg' ? 'modal-lg' : options.size === 'sm' ? 'modal-sm' : '';

        modal.innerHTML = `
            <div class="modal-dialog ${sizeClass}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${escapeHtml(options.title)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${options.body}
                    </div>
                    <div class="modal-footer">
                        ${options.footer}
                    </div>
                </div>
            </div>
        `;

        return modal;
    }

    /**
     * Get status CSS class
     */
    function getStatusClass(status) {
        switch (status) {
            case 'running': return 'bg-primary';
            case 'completed': return 'bg-success';
            case 'failed': return 'bg-danger';
            case 'idle': return 'bg-secondary';
            default: return 'bg-warning';
        }
    }

    /**
     * Run script from modal
     */
    function runScriptFromModal(scriptName) {
        if (activeModal) {
            bootstrap.Modal.getInstance(activeModal)?.hide();
        }
        ScriptsModule.runScript(scriptName);
    }

    /**
     * View logs from modal
     */
    function viewLogsFromModal(scriptName) {
        if (activeModal) {
            bootstrap.Modal.getInstance(activeModal)?.hide();
        }
        // Switch to logs tab
        const logsTab = document.getElementById('logs-tab');
        if (logsTab) {
            logsTab.click();
            LogsModule.loadLogsForScript(scriptName);
        }
    }

    /**
     * Hide all modals
     */
    function hideAll() {
        document.querySelectorAll('.modal.show').forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }

    /**
     * Escape HTML content
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Destroy module
     */
    function destroy() {
        this.hideAll();
        console.log('ModalsModule destroyed');
    }

    // Public API
    return {
        init: init,
        showScriptDetails: showScriptDetails,
        showConfirm: showConfirm,
        showInput: showInput,
        showSystemInfo: showSystemInfo,
        runScriptFromModal: runScriptFromModal,
        viewLogsFromModal: viewLogsFromModal,
        hideAll: hideAll,
        destroy: destroy
    };
})();

