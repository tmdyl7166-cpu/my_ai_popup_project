class NotificationManager {
    constructor() { this.container = document.getElementById('toastContainer'); }
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.innerHTML = '<span>' + message + '</span>';
        this.container.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, duration);
    }
    success(message) { this.show(message, 'success'); }
    error(message) { this.show(message, 'error'); }
}
const GlobalNotificationManager = new NotificationManager();
