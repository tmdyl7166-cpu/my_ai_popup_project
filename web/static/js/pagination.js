/**
 * Pagination Module - 分页控制器
 * 负责分页控件的功能和逻辑
 * 单一职责：分页数据处理和UI渲染
 */

const Pagination = {
    // 状态
    state: {
        currentPage: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 0,
        container: null,
        data: [],
        sortField: null,
        sortDirection: 'asc'
    },

    /**
     * 初始化分页模块
     */
    init: function(containerId) {
        console.log('Pagination initializing...');
        this.state.container = document.getElementById(containerId || 'paginationContent');
        return this;
    },

    /**
     * 设置分页参数
     */
    setOptions: function(options) {
        if (options.pageSize !== undefined) this.state.pageSize = options.pageSize;
        if (options.currentPage !== undefined) this.state.currentPage = options.currentPage;
        if (options.sortField !== undefined) this.state.sortField = options.sortField;
        if (options.sortDirection !== undefined) this.state.sortDirection = options.sortDirection;
        return this;
    },

    /**
     * 设置数据
     */
    setData: function(data, totalItems = null) {
        if (totalItems !== null) {
            this.state.totalItems = totalItems;
        } else {
            this.state.totalItems = data.length;
        }
        
        this.state.data = data;
        this.state.totalPages = Math.ceil(this.state.totalItems / this.state.pageSize);
        
        // 确保当前页码有效
        if (this.state.currentPage > this.state.totalPages) {
            this.state.currentPage = Math.max(1, this.state.totalPages);
        }
        
        return this;
    },

    /**
     * 获取当前页数据
     */
    getCurrentPageData: function() {
        const start = (this.state.currentPage - 1) * this.state.pageSize;
        const end = start + this.state.pageSize;
        return this.state.data.slice(start, end);
    },

    /**
     * 获取分页信息
     */
    getPageInfo: function() {
        return {
            currentPage: this.state.currentPage,
            pageSize: this.state.pageSize,
            totalItems: this.state.totalItems,
            totalPages: this.state.totalPages,
            hasNext: this.state.currentPage < this.state.totalPages,
            hasPrev: this.state.currentPage > 1
        };
    },

    /**
     * 跳转到指定页
     */
    goToPage: function(page) {
        const pageNum = parseInt(page);
        if (pageNum < 1 || pageNum > this.state.totalPages) {
            console.warn(`Invalid page number: ${pageNum}`);
            return false;
        }
        
        this.state.currentPage = pageNum;
        return true;
    },

    /**
     * 下一页
     */
    nextPage: function() {
        return this.goToPage(this.state.currentPage + 1);
    },

    /**
     * 上一页
     */
    prevPage: function() {
        return this.goToPage(this.state.currentPage - 1);
    },

    /**
     * 首页
     */
    firstPage: function() {
        return this.goToPage(1);
    },

    /**
     * 末页
     */
    lastPage: function() {
        return this.goToPage(this.state.totalPages);
    },

    /**
     * 排序
     */
    sort: function(field, direction = 'asc') {
        this.state.sortField = field;
        this.state.sortDirection = direction;

        this.state.data.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];
            
            if (typeof aVal === 'string') aVal = aVal.toLowerCase();
            if (typeof bVal === 'string') bVal = bVal.toLowerCase();
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        return this;
    },

    /**
     * 渲染分页控件
     */
    render: function() {
        if (!this.state.container) {
            console.error('Pagination container not found');
            return;
        }

        const html = this.buildHtml();
        this.state.container.innerHTML = html;
        this.bindEvents();
    },

    /**
     * 构建HTML
     */
    buildHtml: function() {
        const info = this.getPageInfo();
        const startItem = (info.currentPage - 1) * info.pageSize + 1;
        const endItem = Math.min(info.currentPage * info.pageSize, info.totalItems);

        return `
            <div class="pagination-container">
                <!-- 分页信息 -->
                <div class="pagination-info mb-2">
                    <small class="text-muted">
                        显示 ${startItem} - ${endItem} 条，共 ${info.totalItems} 条
                    </small>
                </div>

                <!-- 分页控件 -->
                <nav aria-label="Page navigation">
                    <ul class="pagination pagination-sm justify-content-center mb-0">
                        <!-- 首页 -->
                        <li class="page-item ${!info.hasPrev ? 'disabled' : ''}">
                            <a class="page-link" href="#" data-page="1" onclick="pagination.handlePageClick(event, 1)">
                                <i class="fas fa-angle-double-left"></i>
                            </a>
                        </li>
                        
                        <!-- 上一页 -->
                        <li class="page-item ${!info.hasPrev ? 'disabled' : ''}">
                            <a class="page-link" href="#" data-page="${info.currentPage - 1}" onclick="pagination.handlePageClick(event, ${info.currentPage - 1})">
                                <i class="fas fa-chevron-left"></i>
                            </a>
                        </li>
                        
                        <!-- 页码 -->
                        ${this.buildPageNumbers()}
                        
                        <!-- 下一页 -->
                        <li class="page-item ${!info.hasNext ? 'disabled' : ''}">
                            <a class="page-link" href="#" data-page="${info.currentPage + 1}" onclick="pagination.handlePageClick(event, ${info.currentPage + 1})">
                                <i class="fas fa-chevron-right"></i>
                            </a>
                        </li>
                        
                        <!-- 末页 -->
                        <li class="page-item ${!info.hasNext ? 'disabled' : ''}">
                            <a class="page-link" href="#" data-page="${info.totalPages}" onclick="pagination.handlePageClick(event, ${info.totalPages})">
                                <i class="fas fa-angle-double-right"></i>
                            </a>
                        </li>
                    </ul>
                </nav>

                <!-- 每页条数选择 -->
                <div class="pagination-size mt-2">
                    <small class="text-muted">
                        每页 
                        <select class="form-select form-select-sm d-inline-block w-auto" 
                                onchange="pagination.changePageSize(this.value)">
                            <option value="5" ${this.state.pageSize === 5 ? 'selected' : ''}>5</option>
                            <option value="10" ${this.state.pageSize === 10 ? 'selected' : ''}>10</option>
                            <option value="20" ${this.state.pageSize === 20 ? 'selected' : ''}>20</option>
                            <option value="50" ${this.state.pageSize === 50 ? 'selected' : ''}>50</option>
                        </select> 条
                    </small>
                </div>
        `;
    },

    /**
     * 构建页码按钮
     */
    buildPageNumbers: function() {
        const current = this.state.currentPage;
        const total = this.state.totalPages;
        let pages = [];

        if (total <= 7) {
            // 全部显示
            for (let i = 1; i <= total; i++) {
                pages.push(i);
            }
        } else {
            // 显示部分页码
            if (current <= 4) {
                // 前面几页
                for (let i = 1; i <= 5; i++) pages.push(i);
                pages.push('...');
                pages.push(total);
            } else if (current >= total - 3) {
                // 最后几页
                pages.push(1);
                pages.push('...');
                for (let i = total - 4; i <= total; i++) pages.push(i);
            } else {
                // 中间
                pages.push(1);
                pages.push('...');
                for (let i = current - 1; i <= current + 1; i++) pages.push(i);
                pages.push('...');
                pages.push(total);
            }
        }

        return pages.map(page => {
            if (page === '...') {
                return `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            return `
                <li class="page-item ${page === current ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${page}" onclick="pagination.handlePageClick(event, ${page})">${page}</a>
                </li>
            `;
        }).join('');
    },

    /**
     * 处理页码点击
     */
    handlePageClick: function(event, page) {
        event.preventDefault();
        
        if (this.goToPage(page)) {
            // 触发自定义事件
            const pageInfo = this.getPageInfo();
            this.state.container.dispatchEvent(new CustomEvent('pagechange', {
                detail: pageInfo
            }));
            
            // 重新渲染
            this.render();
        }
    },

    /**
     * 改变每页条数
     */
    changePageSize: function(size) {
        this.state.pageSize = parseInt(size);
        this.state.totalPages = Math.ceil(this.state.totalItems / this.state.pageSize);
        this.state.currentPage = 1;
        
        // 触发自定义事件
        this.state.container.dispatchEvent(new CustomEvent('pagesizechange', {
            detail: { pageSize: this.state.pageSize }
        }));
        
        this.render();
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        // 事件已在HTML中处理
    },

    /**
     * 刷新
     */
    refresh: function() {
        this.render();
        return this.getPageInfo();
    },

    /**
     * 重置
     */
    reset: function() {
        this.state.currentPage = 1;
        this.state.pageSize = 10;
        this.state.totalItems = 0;
        this.state.totalPages = 0;
        this.state.data = [];
        this.state.sortField = null;
        this.state.sortDirection = 'asc';
        return this;
    },

    /**
     * 销毁
     */
    destroy: function() {
        console.log('Pagination destroying...');
        if (this.state.container) {
            this.state.container.innerHTML = '';
        }
        this.reset();
    }
};

// 导出到全局
window.Pagination = Pagination;
