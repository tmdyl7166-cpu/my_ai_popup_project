/**
 * Modal Manager Module - 模态框管理模块
 * 负责创建和管理各种模态框
 * 单一职责：模态框管理
 */

const ModalManager = {
    // 状态
    state: {
        container: null,
        activeModals: new Map(),
        modalCounter: 0
    },

    // 配置
    config: {
        backdrop: true,
        keyboard: true,
        focus: true,
        animationDuration: 300
    },

    /**
     * 初始化模态框管理器
     */
    init: function() {
        console.log('Modal Manager initializing...');
        this.createContainer();
    },

    /**
     * 创建模态框容器
     */
    createContainer: function() {
        let container = document.getElementById('modalContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'modalContainer';
            document.body.appendChild(container);
        }
        this.state.container = container;
    },

    /**
     * 创建模态框
     */
    create: function(options = {}) {
        const modalId = `modal-${++this.state.modalCounter}`;

        const defaultOptions = {
            id: modalId,
            title: '模态框',
            content: '',
            size: 'md', // sm, md, lg, xl
            buttons: [],
            closable: true,
            backdrop: this.config.backdrop,
            keyboard: this.config.keyboard,
            focus: this.config.focus,
            onShow: null,
            onHide: null,
            onConfirm: null
        };

        const config = { ...defaultOptions, ...options };

        // 创建模态框HTML
        const modalHtml = this.buildModalHtml(config);

        // 添加到容器
        this.state.container.insertAdjacentHTML('beforeend', modalHtml);

        const modalElement = document.getElementById(config.id);
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: config.backdrop,
            keyboard: config.keyboard,
            focus: config.focus
        });

        // 存储模态框信息
        const modalData = {
            id: config.id,
            element: modalElement,
            modal: modal,
            config: config
        };
        this.state.activeModals.set(config.id, modalData);

        // 绑定事件
        this.bindModalEvents(modalData);

        return config.id;
    },

    /**
     * 构建模态框HTML
     */
    buildModalHtml: function(config) {
        const sizeClass = config.size ? `modal-${config.size}` : '';
        const closable = config.closable ? '' : 'data-bs-backdrop="static"';

        let buttonsHtml = '';
        if (config.buttons && config.buttons.length > 0) {
            buttonsHtml = config.buttons.map(button => `
                <button type="button"
                        class="btn btn-${button.type || 'secondary'}"
                        data-action="${button.action || ''}"
                        ${button.dismiss ? 'data-bs-dismiss="modal"' : ''}>
                    ${button.text}
                </button>
            `).join('');
        }

        return `
            <div class="modal fade" id="${config.id}" tabindex="-1" ${closable}>
                <div class="modal-dialog ${sizeClass}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${config.title}</h5>
                            ${config.closable ? '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>' : ''}
                        </div>
                        <div class="modal-body">
                            ${config.content}
                        </div>
                        ${buttonsHtml ? `<div class="modal-footer">${buttonsHtml}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * 绑定模态框事件
     */
    bindModalEvents: function(modalData) {
        const { modal, config } = modalData;

        // 显示事件
        modal._element.addEventListener('show.bs.modal', () => {
            if (config.onShow) config.onShow(modalData);
        });

        // 隐藏事件
        modal._element.addEventListener('hide.bs.modal', () => {
            if (config.onHide) config.onHide(modalData);
        });

        // 隐藏后事件
        modal._element.addEventListener('hidden.bs.modal', () => {
            this.destroy(config.id);
        });

        // 按钮点击事件
        const buttons = modal._element.querySelectorAll('[data-action]');
        buttons.forEach(button => {
            button.addEventListener('click', (event) => {
                const action = event.target.getAttribute('data-action');
                if (action === 'confirm' && config.onConfirm) {
                    config.onConfirm(modalData);
                }
                // 其他动作可以在这里扩展
            });
        });
    },

    /**
     * 显示模态框
     */
    show: function(id) {
        const modalData = this.state.activeModals.get(id);
        if (modalData) {
            modalData.modal.show();
        }
    },

    /**
     * 隐藏模态框
     */
    hide: function(id) {
        const modalData = this.state.activeModals.get(id);
        if (modalData) {
            modalData.modal.hide();
        }
    },

    /**
     * 更新模态框内容
     */
    update: function(id, options) {
        const modalData = this.state.activeModals.get(id);
        if (!modalData) return;

        const { element, config } = modalData;

        // 更新标题
        if (options.title !== undefined) {
            const titleElement = element.querySelector('.modal-title');
            if (titleElement) titleElement.textContent = options.title;
            config.title = options.title;
        }

        // 更新内容
        if (options.content !== undefined) {
            const bodyElement = element.querySelector('.modal-body');
            if (bodyElement) bodyElement.innerHTML = options.content;
            config.content = options.content;
        }

        // 更新配置
        Object.assign(config, options);
    },

    /**
     * 销毁模态框
     */
    destroy: function(id) {
        const modalData = this.state.activeModals.get(id);
        if (!modalData) return;

        // 从DOM中移除
        if (modalData.element.parentNode) {
            modalData.element.parentNode.removeChild(modalData.element);
        }

        // 从活跃列表中移除
        this.state.activeModals.delete(id);
    },

    /**
     * 销毁所有模态框
     */
    destroyAll: function() {
        const ids = Array.from(this.state.activeModals.keys());
        ids.forEach(id => this.destroy(id));
    },

    /**
     * 获取模态框数据
     */
    get: function(id) {
        return this.state.activeModals.get(id);
    },

    /**
     * 获取所有活跃模态框
     */
    getAll: function() {
        return Array.from(this.state.activeModals.values());
    },

    /**
     * 创建确认对话框
     */
    confirm: function(options = {}) {
        const defaultOptions = {
            title: '确认',
            content: '您确定要执行此操作吗？',
            buttons: [
                { text: '取消', type: 'secondary', dismiss: true },
                { text: '确定', type: 'primary', action: 'confirm' }
            ],
            size: 'sm',
            ...options
        };

        return this.create(defaultOptions);
    },

    /**
     * 创建信息对话框
     */
    alert: function(options = {}) {
        const defaultOptions = {
            title: '提示',
            content: '操作已完成',
            buttons: [
                { text: '确定', type: 'primary', dismiss: true }
            ],
            size: 'sm',
            ...options
        };

        return this.create(defaultOptions);
    },

    /**
     * 创建加载对话框
     */
    loading: function(options = {}) {
        const defaultOptions = {
            title: '加载中',
            content: '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">加载中...</span></div></div>',
            closable: false,
            backdrop: 'static',
            keyboard: false,
            size: 'sm',
            ...options
        };

        return this.create(defaultOptions);
    },

    /**
     * 销毁模态框管理器
     */
    destroy: function() {
        console.log('Modal Manager destroying...');
        this.destroyAll();
        if (this.state.container) {
            // 不移除容器，因为可能还有其他模态框
            this.state.container = null;
        }
        this.state.activeModals.clear();
    }
};

// 导出到全局
window.ModalManager = ModalManager;
