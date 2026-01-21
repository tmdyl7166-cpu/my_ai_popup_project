class WSManager {
    constructor() { this.ws = null; this.handlers = {}; this.connected = false; }
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/ws/monitoring';
        try {
            this.ws = new WebSocket(wsUrl);
            this.ws.onopen = () => { this.connected = true; this.emit('connected'); };
            this.ws.onclose = () => { this.connected = false; this.scheduleReconnect(); };
            this.ws.onerror = () => { this.emit('error'); };
            this.ws.onmessage = (event) => {
                try { const data = JSON.parse(event.data); this.emit(data.type, data); } catch (e) {}
            };
        } catch (e) { this.scheduleReconnect(); }
    }
    scheduleReconnect() { setTimeout(() => this.connect(), 3000); }
    on(event, handler) { if (!this.handlers[event]) this.handlers[event] = []; this.handlers[event].push(handler); }
    emit(event, data) { if (this.handlers[event]) this.handlers[event].forEach(h => h(data)); }
}
const wsManager = new WSManager();
