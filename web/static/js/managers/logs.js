/**
 * Logs Manager
 * Handles log viewing and management
 */
window.LogsModule = (function() {
    // Current state
    let currentScript = null;
    let logsCache = new Map();
    let autoRefresh = false;
    let refreshInterval = null;

    /**
     * Initialize logs module
     */
    function init() {
        console.log('LogsModule initialized');
        this.bindEvents();
    }

    /**
     * Bind event handlers
     */
    function bindEvents() {
        const logsTab = document.getElementById('logs-tab');
        if (logsTab) {
            logsTab.addEventListener('shown.bs.tab', () => {
                this.onTabActivated();
            });
        }

        const logRefreshBtn = document.getElementById('log-refresh-btn');
        if (logRefreshBtn) {
            logRefreshBtn.addEventListener('click', () => {
                this.refreshLogs();
            });
        }

        const clearLogsBtn = document.getElementById('clear-logs-btn');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => {
                this.clearLogs();
            });
        }

        const autoRefreshToggle = document.getElementById('auto-refresh-logs');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                autoRefresh = e.target.checked;
                if (autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    /**
     * Handle tab activation
     */
    async function onTabActivated() {
        if (!currentScript) {
            this.showEmptyState();
        } else {
            await this.loadLogs(currentScript);
        }
    }

    /**
     * Show empty state when no script selected
     */
    function showEmptyState() {
        const container = document.getElementById('logs-content');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    请选择一个脚本查看其日志
                </div>
            `;
        }
    }

    /**
     * Load logs for specific script
     */
    async function loadLogs(scriptName, lines = 100) {
        currentScript = scriptName;

        try {
            const response = await fetch(`/api/logs/${scriptName}?lines=${lines}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.renderLogs(data.logs, scriptName);
                // Cache logs
                logsCache.set(scriptName, data.logs);
            } else {
                this.showError(data.message || '加载日志失败');
            }
        } catch (error) {
            console.error('Failed to load logs:', error);
            this.showError('加载日志失败: ' + error.message);
        }
    }

    /**
     * Load logs for script from other module
     */
    function loadLogsForScript(scriptName) {
        currentScript = scriptName;
        this.loadLogs(scriptName);
    }

    /**
     * Render logs to container
     */
    function renderLogs(logs, scriptName) {
        const container = document.getElementById('logs-content');
        if (!container) return;

        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    暂无日志记录
                </div>
            `;
            return;
        }

        // Build HTML
        const logsHtml = logs.map(line => {
            // Parse log line for styling
            const escapedLine = escapeHtml(line);
            const styledLine = applyLogStyles(escapedLine);
            return `<div class="log-line">${styledLine}</div>`;
        }).join('');

        container.innerHTML = logsHtml;

        // Auto scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    /**
     * Apply syntax highlighting to log lines
     */
    function applyLogStyles(line) {
        // Error lines (red)
        if (line.includes('[ERROR]') || line.includes('Error:') || line.includes('Traceback')) {
            return `<span class="log-error">${line}</span>`;
        }
        // Warning lines (yellow)
        if (line.includes('[WARN]') || line.includes('Warning:')) {
            return `<span class="log-warning">${line}</span>`;
        }
        // Success lines (green)
        if (line.includes('[SUCCESS]') || line.includes('Success:')) {
            return `<span class="log-success">${line}</span>`;
        }
        // Info lines (blue timestamp)
        if (/^\d{4}-\d{2}-\d{2}/.test(line)) {
            return `<span class="log-timestamp">${line}</span>`;
        }
        return line;
    }

    /**
     * Refresh current logs
     */
    async function refreshLogs() {
        if (currentScript) {
            // Invalidate cache
            logsCache.delete(currentScript);
            await this.loadLogs(currentScript);
            NotificationsManager.success('日志已刷新');
        } else {
            this.showEmptyState();
        }
    }

    /**
     * Clear logs display
     */
    function clearLogs() {
        const container = document.getElementById('logs-content');
        if (container) {
            container.innerHTML = '';
        }
        currentScript = null;
        logsCache.clear();
        NotificationsManager.info('日志已清除');
    }

    /**
     * Show error message
     */
    function showError(message) {
        const container = document.getElementById('logs-content');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${escapeHtml(message)}
                </div>
            `;
        }
    }

    /**
     * Update script select dropdown
     */
    function updateScriptSelect(scripts) {
        const select = document.getElementById('log-script-select');
        if (!select) return;

        const currentValue = select.value;
        select.innerHTML = '<option value="">选择脚本</option>';

        scripts.forEach(script => {
            const option = document.createElement('option');
            option.value = script.name;
            option.textContent = script.display_name;
            select.appendChild(option);
        });

        // Restore selection
        if (currentValue) {
            select.value = currentValue;
        }

        // Add change event
        select.onchange = () => {
            const scriptName = select.value;
            if (scriptName) {
                this.loadLogs(scriptName);
            } else {
                this.showEmptyState();
            }
        };
    }

    /**
     * Start auto refresh
     */
    function startAutoRefresh() {
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(() => {
            if (currentScript) {
                this.loadLogs(currentScript);
            }
        }, 5000);
        console.log('Logs auto-refresh started');
    }

    /**
     * Stop auto refresh
     */
    function stopAutoRefresh() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        console.log('Logs auto-refresh stopped');
    }

    /**
     * Escape HTML content
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Export logs to file
     */
    function exportLogs(format = 'txt') {
        if (!currentScript || !logsCache.has(currentScript)) {
            NotificationsManager.warning('没有可导出的日志');
            return;
        }

        const logs = logsCache.get(currentScript);
        let content = '';
        let mimeType = 'text/plain';
        let filename = `${currentScript}.${format}`;

        if (format === 'json') {
            content = JSON.stringify(logs, null, 2);
            mimeType = 'application/json';
        } else {
            content = logs.join('\n');
        }

        // Download file
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        NotificationsManager.success(`日志已导出为 ${filename}`);
    }

    /**
     * Destroy module
     */
    function destroy() {
        this.stopAutoRefresh();
        logsCache.clear();
        currentScript = null;
        console.log('LogsModule destroyed');
    }

    // Public API
    return {
        init: init,
        loadLogs: loadLogs,
        loadLogsForScript: loadLogsForScript,
        refreshLogs: refreshLogs,
        clearLogs: clearLogs,
        updateScriptSelect: updateScriptSelect,
        showError: showError,
        exportLogs: exportLogs,
        startAutoRefresh: startAutoRefresh,
        stopAutoRefresh: stopAutoRefresh,
        destroy: destroy
    };
})();

