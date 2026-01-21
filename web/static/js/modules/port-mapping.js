const PortMapping = {
    API_BASE: '/api',
    WS_BASE: '/ws',
    getApiUrl: function() { return window.location.origin + this.API_BASE; },
    getWsUrl: function() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return protocol + '//' + window.location.host + this.WS_BASE + '/monitoring';
    }
};
