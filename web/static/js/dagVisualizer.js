/**
 * DAG Visualizer Module - DAG可视化模块
 * 负责机械风主题企业大屏幕图形监控，DAG可视化流水线
 * 单一职责：DAG图的可视化和交互操作
 */

const DAGVisualizer = {
    // 状态
    state: {
        container: null,
        canvas: null,
        svg: null,
        dagData: null,
        nodes: new Map(),
        edges: new Map(),
        selectedNode: null,
        zoom: 1,
        panOffset: { x: 0, y: 0 },
        isDragging: false,
        dragStart: null,
        updateInterval: null,
        autoRefresh: true
    },

    // 配置
    config: {
        refreshInterval: 10000, // 10秒
        apiEndpoint: '/api/tasks/dag',
        nodeSize: { width: 120, height: 60 },
        nodeSpacing: { horizontal: 200, vertical: 100 },
        themes: {
            mechanical: {
                primary: '#1a1a2e',
                secondary: '#16213e',
                accent: '#0f3460',
                highlight: '#e94560',
                text: '#eaeaea',
                border: '2px solid #0f3460',
                shadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
            }
        },
        nodeTypes: {
            'start': { icon: 'play-circle', color: '#00b894' },
            'task': { icon: 'cogs', color: '#0984e3' },
            'decision': { icon: 'code-branch', color: '#fdcb6e' },
            'end': { icon: 'stop-circle', color: '#d63031' },
            'parallel': { icon: 'arrows-alt', color: '#6c5ce7' }
        },
        statusColors: {
            'pending': '#636e72',
            'running': '#0984e3',
            'completed': '#00b894',
            'failed': '#d63031',
            'skipped': '#fdcb6e'
        }
    },

    /**
     * 初始化DAG可视化器
     */
    init: function(containerId = 'dagCanvas') {
        console.log('DAG Visualizer initializing...');

        this.state.container = document.getElementById(containerId);
        if (!this.state.container) {
            console.error('DAG Visualizer container not found');
            return;
        }

        this.createCanvas();
        this.bindEvents();
        this.loadDAGData();
        this.startAutoRefresh();
    },

    /**
     * 创建画布
     */
    createCanvas: function() {
        // 创建SVG画布
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '600');
        svg.setAttribute('class', 'dag-canvas mechanical-theme');
        svg.style.background = 'linear-gradient(135deg, var(--mech-primary), var(--mech-secondary))';

        // 创建定义
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');

        // 创建箭头标记
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '7');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3.5');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
        polygon.setAttribute('fill', '#666');

        marker.appendChild(polygon);
        defs.appendChild(marker);
        svg.appendChild(defs);

        // 创建节点组
        const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        nodesGroup.setAttribute('class', 'nodes-group');
        svg.appendChild(nodesGroup);

        // 创建边组
        const edgesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        edgesGroup.setAttribute('class', 'edges-group');
        svg.appendChild(edgesGroup);

        this.state.container.appendChild(svg);
        this.state.svg = svg;
        this.state.nodesGroup = nodesGroup;
        this.state.edgesGroup = edgesGroup;
    },

    /**
     * 绑定事件
     */
    bindEvents: function() {
        const svg = this.state.svg;
        if (!svg) return;

        // 鼠标滚轮缩放
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.handleZoom(e);
        });

        // 鼠标拖拽平移
        svg.addEventListener('mousedown', (e) => {
            if (e.target === svg) {
                this.startPan(e);
            }
        });

        svg.addEventListener('mousemove', (e) => {
            if (this.state.isDragging) {
                this.updatePan(e);
            }
        });

        svg.addEventListener('mouseup', () => {
            this.endPan();
        });

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
    },

    /**
     * 加载DAG数据
     */
    loadDAGData: async function(taskId = null) {
        try {
            let url = this.config.apiEndpoint;
            if (taskId) {
                url += `/${taskId}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch DAG data');

            const data = await response.json();
            this.state.dagData = data.dag || this.getMockDAGData();
            this.renderDAG();

            // 触发冒泡通知
            bubbleMonitor.show('success', 'DAG数据加载', 'DAG图表已更新', 'dag-visualizer');

        } catch (error) {
            console.error('Failed to load DAG data:', error);
            this.state.dagData = this.getMockDAGData();
            this.renderDAG();

            // 触发错误通知
            bubbleMonitor.show('error', 'DAG数据加载失败', error.message, 'dag-visualizer');
        }
    },

    /**
     * 获取模拟DAG数据
     */
    getMockDAGData: function() {
        return {
            nodes: [
                { id: 'start', type: 'start', label: '开始', x: 100, y: 100, status: 'completed' },
                { id: 'task1', type: 'task', label: '数据预处理', x: 350, y: 100, status: 'completed' },
                { id: 'task2', type: 'task', label: '模型训练', x: 600, y: 100, status: 'running' },
                { id: 'decision1', type: 'decision', label: '准确率检查', x: 350, y: 250, status: 'pending' },
                { id: 'task3', type: 'task', label: '参数调优', x: 100, y: 400, status: 'pending' },
                { id: 'task4', type: 'task', label: '重新训练', x: 600, y: 400, status: 'pending' },
                { id: 'end', type: 'end', label: '完成', x: 350, y: 550, status: 'pending' }
            ],
            edges: [
                { from: 'start', to: 'task1' },
                { from: 'task1', to: 'task2' },
                { from: 'task2', to: 'decision1' },
                { from: 'decision1', to: 'task3', condition: 'accuracy < 0.8' },
                { from: 'decision1', to: 'task4', condition: 'accuracy >= 0.8' },
                { from: 'task3', to: 'task4' },
                { from: 'task4', to: 'end' }
            ]
        };
    },

    /**
     * 渲染DAG图
     */
    renderDAG: function() {
        this.clearCanvas();
        this.renderEdges();
        this.renderNodes();
        this.updateLayout();
    },

    /**
     * 清空画布
     */
    clearCanvas: function() {
        if (this.state.nodesGroup) {
            this.state.nodesGroup.innerHTML = '';
        }
        if (this.state.edgesGroup) {
            this.state.edgesGroup.innerHTML = '';
        }
        this.state.nodes.clear();
        this.state.edges.clear();
    },

    /**
     * 渲染节点
     */
    renderNodes: function() {
        const nodes = this.state.dagData.nodes || [];
        const nodesGroup = this.state.nodesGroup;

        nodes.forEach(nodeData => {
            const node = this.createNodeElement(nodeData);
            nodesGroup.appendChild(node);
            this.state.nodes.set(nodeData.id, { element: node, data: nodeData });
        });
    },

    /**
     * 创建节点元素
     */
    createNodeElement: function(nodeData) {
        const nodeType = this.config.nodeTypes[nodeData.type] || this.config.nodeTypes.task;
        const statusColor = this.config.statusColors[nodeData.status] || '#636e72';

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'dag-node');
        g.setAttribute('data-node-id', nodeData.id);
        g.setAttribute('transform', `translate(${nodeData.x || 0}, ${nodeData.y || 0})`);

        // 节点背景
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', this.config.nodeSize.width);
        rect.setAttribute('height', this.config.nodeSize.height);
        rect.setAttribute('rx', '8');
        rect.setAttribute('fill', nodeType.color);
        rect.setAttribute('stroke', statusColor);
        rect.setAttribute('stroke-width', '3');
        rect.setAttribute('class', 'node-bg');

        // 节点图标
        const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        icon.setAttribute('x', '20');
        icon.setAttribute('y', '25');
        icon.setAttribute('class', 'node-icon fas');
        icon.setAttribute('fill', 'white');
        icon.setAttribute('font-size', '16');
        icon.textContent = `\\uf${this.getIconCode(nodeType.icon)}`;

        // 节点标签
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', '40');
        label.setAttribute('y', '25');
        label.setAttribute('class', 'node-label');
        label.setAttribute('fill', 'white');
        label.setAttribute('font-size', '12');
        label.textContent = nodeData.label || nodeData.id;

        // 状态指示器
        const statusIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        statusIndicator.setAttribute('cx', '100');
        statusIndicator.setAttribute('cy', '45');
        statusIndicator.setAttribute('r', '6');
        statusIndicator.setAttribute('fill', statusColor);
        statusIndicator.setAttribute('class', 'status-indicator');

        g.appendChild(rect);
        g.appendChild(icon);
        g.appendChild(label);
        g.appendChild(statusIndicator);

        // 绑定事件
        g.addEventListener('click', () => this.selectNode(nodeData.id));
        g.addEventListener('dblclick', () => this.showNodeDetails(nodeData));

        return g;
    },

    /**
     * 渲染边
     */
    renderEdges: function() {
        const edges = this.state.dagData.edges || [];
        const edgesGroup = this.state.edgesGroup;

        edges.forEach(edgeData => {
            const edge = this.createEdgeElement(edgeData);
            if (edge) {
                edgesGroup.appendChild(edge);
                this.state.edges.set(`${edgeData.from}-${edgeData.to}`, { element: edge, data: edgeData });
            }
        });
    },

    /**
     * 创建边元素
     */
    createEdgeElement: function(edgeData) {
        const fromNode = this.state.dagData.nodes.find(n => n.id === edgeData.from);
        const toNode = this.state.dagData.nodes.find(n => n.id === edgeData.to);

        if (!fromNode || !toNode) return null;

        const fromX = (fromNode.x || 0) + this.config.nodeSize.width;
        const fromY = (fromNode.y || 0) + this.config.nodeSize.height / 2;
        const toX = (toNode.x || 0);
        const toY = (toNode.y || 0) + this.config.nodeSize.height / 2;

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = `M ${fromX} ${fromY} L ${toX} ${toY}`;
        path.setAttribute('d', d);
        path.setAttribute('stroke', '#666');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#arrowhead)');
        path.setAttribute('class', 'dag-edge');

        return path;
    },

    /**
     * 更新布局
     */
    updateLayout: function() {
        const svg = this.state.svg;
        if (!svg) return;

        // 计算边界
        const nodes = Array.from(this.state.nodes.values());
        if (nodes.length === 0) return;

        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

        nodes.forEach(({ data }) => {
            minX = Math.min(minX, data.x || 0);
            minY = Math.min(minY, data.y || 0);
            maxX = Math.max(maxX, (data.x || 0) + this.config.nodeSize.width);
            maxY = Math.max(maxY, (data.y || 0) + this.config.nodeSize.height);
        });

        // 设置视图框
        const padding = 50;
        const viewBox = `${minX - padding} ${minY - padding} ${maxX - minX + 2 * padding} ${maxY - minY + 2 * padding}`;
        svg.setAttribute('viewBox', viewBox);
    },

    /**
     * 选择节点
     */
    selectNode: function(nodeId) {
        // 清除之前的选择
        if (this.state.selectedNode) {
            const prevNode = this.state.nodes.get(this.state.selectedNode);
            if (prevNode) {
                prevNode.element.classList.remove('selected');
            }
        }

        // 设置新的选择
        this.state.selectedNode = nodeId;
        const node = this.state.nodes.get(nodeId);
        if (node) {
            node.element.classList.add('selected');
        }

        // 触发事件
        this.onNodeSelected(nodeId);
    },

    /**
     * 显示节点详情
     */
    showNodeDetails: function(nodeData) {
        ModalManager.alert({
            title: `${nodeData.label || nodeData.id} 详情`,
            content: `
                <div class="node-details">
                    <div class="detail-row">
                        <strong>ID:</strong> ${nodeData.id}
                    </div>
                    <div class="detail-row">
                        <strong>类型:</strong> ${nodeData.type}
                    </div>
                    <div class="detail-row">
                        <strong>状态:</strong>
                        <span class="badge" style="background-color: ${this.config.statusColors[nodeData.status]}">
                            ${this.getStatusText(nodeData.status)}
                        </span>
                    </div>
                    <div class="detail-row">
                        <strong>开始时间:</strong> ${nodeData.start_time || '未开始'}
                    </div>
                    <div class="detail-row">
                        <strong>结束时间:</strong> ${nodeData.end_time || '未结束'}
                    </div>
                    <div class="detail-row">
                        <strong>执行时长:</strong> ${nodeData.duration || '0秒'}
                    </div>
                    ${nodeData.error ? `
                        <div class="detail-row">
                            <strong>错误信息:</strong>
                            <div class="error-message">${nodeData.error}</div>
                        </div>
                    ` : ''}
                </div>
            `,
            size: 'lg'
        });
    },

    /**
     * 处理缩放
     */
    handleZoom: function(event) {
        const delta = event.deltaY > 0 ? 0.9 : 1.1;
        this.state.zoom *= delta;
        this.state.zoom = Math.max(0.1, Math.min(3, this.state.zoom));

        this.applyTransform();
    },

    /**
     * 开始平移
     */
    startPan: function(event) {
        this.state.isDragging = true;
        this.state.dragStart = {
            x: event.clientX - this.state.panOffset.x,
            y: event.clientY - this.state.panOffset.y
        };
    },

    /**
     * 更新平移
     */
    updatePan: function(event) {
        if (!this.state.isDragging || !this.state.dragStart) return;

        this.state.panOffset.x = event.clientX - this.state.dragStart.x;
        this.state.panOffset.y = event.clientY - this.state.dragStart.y;

        this.applyTransform();
    },

    /**
     * 结束平移
     */
    endPan: function() {
        this.state.isDragging = false;
        this.state.dragStart = null;
    },

    /**
     * 应用变换
     */
    applyTransform: function() {
        const svg = this.state.svg;
        if (!svg) return;

        const transform = `translate(${this.state.panOffset.x}, ${this.state.panOffset.y}) scale(${this.state.zoom})`;
        svg.style.transform = transform;
    },

    /**
     * 处理键盘事件
     */
    handleKeyDown: function(event) {
        switch (event.key) {
            case 'Delete':
            case 'Backspace':
                if (this.state.selectedNode) {
                    this.removeNode(this.state.selectedNode);
                }
                break;
            case 'Escape':
                this.deselectNode();
                break;
            case '+':
            case '=':
                this.zoomIn();
                break;
            case '-':
                this.zoomOut();
                break;
            case '0':
                this.resetView();
                break;
        }
    },

    /**
     * 放大
     */
    zoomIn: function() {
        this.state.zoom *= 1.2;
        this.state.zoom = Math.min(3, this.state.zoom);
        this.applyTransform();
    },

    /**
     * 缩小
     */
    zoomOut: function() {
        this.state.zoom *= 0.8;
        this.state.zoom = Math.max(0.1, this.state.zoom);
        this.applyTransform();
    },

    /**
     * 重置视图
     */
    resetView: function() {
        this.state.zoom = 1;
        this.state.panOffset = { x: 0, y: 0 };
        this.applyTransform();
    },

    /**
     * 取消选择节点
     */
    deselectNode: function() {
        if (this.state.selectedNode) {
            const node = this.state.nodes.get(this.state.selectedNode);
            if (node) {
                node.element.classList.remove('selected');
            }
            this.state.selectedNode = null;
        }
    },

    /**
     * 添加节点
     */
    addNode: function(nodeData) {
        if (!this.state.dagData.nodes) {
            this.state.dagData.nodes = [];
        }

        this.state.dagData.nodes.push(nodeData);
        this.renderDAG();

        bubbleMonitor.show('success', '节点添加', `节点 ${nodeData.label} 已添加`, 'dag-visualizer');
    },

    /**
     * 删除节点
     */
    removeNode: function(nodeId) {
        if (!this.state.dagData.nodes) return;

        this.state.dagData.nodes = this.state.dagData.nodes.filter(n => n.id !== nodeId);

        // 删除相关边
        if (this.state.dagData.edges) {
            this.state.dagData.edges = this.state.dagData.edges.filter(
                e => e.from !== nodeId && e.to !== nodeId
            );
        }

        this.renderDAG();
        this.deselectNode();

        bubbleMonitor.show('warning', '节点删除', `节点 ${nodeId} 已删除`, 'dag-visualizer');
    },

    /**
     * 更新节点状态
     */
    updateNodeStatus: function(nodeId, status) {
        const node = this.state.dagData.nodes.find(n => n.id === nodeId);
        if (node) {
            node.status = status;
            this.renderDAG();

            // 触发状态变化通知
            const statusText = this.getStatusText(status);
            bubbleMonitor.show(
                status === 'completed' ? 'success' :
                status === 'failed' ? 'error' :
                status === 'running' ? 'info' : 'warning',
                '节点状态更新',
                `节点 ${node.label} 状态变为: ${statusText}`,
                'dag-visualizer'
            );
        }
    },

    /**
     * 连接节点
     */
    connectNodes: function(fromId, toId, condition = null) {
        if (!this.state.dagData.edges) {
            this.state.dagData.edges = [];
        }

        // 检查是否已存在连接
        const existing = this.state.dagData.edges.find(e => e.from === fromId && e.to === toId);
        if (existing) return;

        const edge = { from: fromId, to: toId };
        if (condition) {
            edge.condition = condition;
        }

        this.state.dagData.edges.push(edge);
        this.renderDAG();

        bubbleMonitor.show('info', '节点连接', `已连接 ${fromId} -> ${toId}`, 'dag-visualizer');
    },

    /**
     * 断开节点连接
     */
    disconnectNodes: function(fromId, toId) {
        if (!this.state.dagData.edges) return;

        this.state.dagData.edges = this.state.dagData.edges.filter(
            e => !(e.from === fromId && e.to === toId)
        );

        this.renderDAG();

        bubbleMonitor.show('warning', '断开连接', `已断开 ${fromId} -> ${toId}`, 'dag-visualizer');
    },

    /**
     * 高亮执行路径
     */
    highlightExecutionPath: function(path) {
        // 清除之前的路径高亮
        document.querySelectorAll('.dag-edge.highlight').forEach(edge => {
            edge.classList.remove('highlight');
        });

        // 高亮指定路径
        path.forEach(edgeKey => {
            const edge = this.state.edges.get(edgeKey);
            if (edge) {
                edge.element.classList.add('highlight');
            }
        });
    },

    /**
     * 获取DAG配置
     */
    getDAGConfig: function() {
        return this.state.dagData;
    },

    /**
     * 保存DAG配置
     */
    saveDAGConfig: async function() {
        try {
            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.state.dagData)
            });

            if (!response.ok) throw new Error('Failed to save DAG config');

            const result = await response.json();
            bubbleMonitor.show('success', '配置保存', 'DAG配置已保存', 'dag-visualizer');

            return result;
        } catch (error) {
            console.error('Failed to save DAG config:', error);
            bubbleMonitor.show('error', '保存失败', error.message, 'dag-visualizer');
            throw error;
        }
    },

    /**
     * 获取图标代码
     */
    getIconCode: function(iconName) {
        const iconCodes = {
            'play-circle': '144',
            'cogs': '085',
            'code-branch': '126',
            'stop-circle': '28d',
            'arrows-alt': '0b2'
        };
        return iconCodes[iconName] || '085';
    },

    /**
     * 获取状态文本
     */
    getStatusText: function(status) {
        const texts = {
            'pending': '等待中',
            'running': '运行中',
            'completed': '已完成',
            'failed': '失败',
            'skipped': '已跳过'
        };
        return texts[status] || status;
    },

    /**
     * 节点选择事件
     */
    onNodeSelected: function(nodeId) {
        // 可以在这里添加节点选择后的逻辑
        console.log('Node selected:', nodeId);
    },

    /**
     * 开始自动刷新
     */
    startAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
        }

        this.state.updateInterval = setInterval(() => {
            if (this.state.autoRefresh) {
                this.loadDAGData();
            }
        }, this.config.refreshInterval);
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh: function() {
        if (this.state.updateInterval) {
            clearInterval(this.state.updateInterval);
            this.state.updateInterval = null;
        }
    },

    /**
     * 刷新数据
     */
    refresh: function() {
        return this.loadDAGData();
    },

    /**
     * 更新数据
     */
    update: function(newData) {
        this.state.dagData = newData;
        this.renderDAG();
    },

    /**
     * 导出DAG图
     */
    exportDAG: function(format = 'svg') {
        const svg = this.state.svg;
        if (!svg) return;

        if (format === 'svg') {
            const serializer = new XMLSerializer();
            const svgString = serializer.serializeToString(svg);

            const blob = new Blob([svgString], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dag-${Date.now()}.svg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            bubbleMonitor.show('success', '导出成功', 'DAG图已导出为SVG', 'dag-visualizer');
        }
    },

    /**
     * 销毁DAG可视化器
     */
    destroy: function() {
        console.log('DAG Visualizer destroying...');
        this.stopAutoRefresh();

        if (this.state.container) {
            this.state.container.innerHTML = '';
        }

        this.state.nodes.clear();
        this.state.edges.clear();
    }
};

// 导出到全局
window.dagVisualizer = DAGVisualizer;
