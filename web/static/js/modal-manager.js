class ModalManager {
    constructor() { this.activeModal = null; }
    show(modalId) {
        const el = document.getElementById(modalId);
        if (el) el.classList.remove('hidden');
        this.activeModal = modalId;
    }
    hide(modalId) {
        const el = document.getElementById(modalId);
        if (el) el.classList.add('hidden');
        this.activeModal = null;
    }
    showError(message) { alert('错误: ' + message); }
    showSuccess(message) { alert('成功: ' + message); }
    init() { console.log('ModalManager initialized'); }
}
const ModalManager = new ModalManager();
