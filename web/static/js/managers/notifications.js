/**
 * Notifications Manager
 * Centralized notification system for the application
 */
window.NotificationsManager = (function() {
    // Configuration
    const config = {
        defaultDuration: 3000,
        maxNotifications: 5,
        position: 'top-right',
        animationDuration: 300
    };

    // Container reference
    let container = null;

    /**
     * Initialize notification system
     */
    function init(options = {}) {
        Object.assign(config, options);

        // Create container if not exists
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications-container';
            container.className = 'notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }

        console.log('NotificationsManager initialized');
    }

    /**
     * Show notification
     */
    function show(message, type = 'info', options = {}) {
        const notification = createNotification(message, type, options);
        container.appendChild(notification);

        // Trigger animation
        requestAnimationFrame(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        });

        // Auto remove
        const duration = options.duration || config.defaultDuration;
        if (duration > 0) {
            setTimeout(() => {
                remove(notification);
            }, duration);
        }

        // Limit max notifications
        const notifications = container.querySelectorAll('.notification');
        if (notifications.length > config.maxNotifications) {
            remove(notifications[0]);
        }

        return notification;
    }

    /**
     * Create notification element
     */
    function createNotification(message, type, options) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            pointer-events: auto;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 280px;
            max-width: 400px;
            opacity: 0;
            transform: translateX(100%);
            transition: all ${config.animationDuration}ms ease;
            background: ${getBackgroundColor(type)};
            color: ${getTextColor(type)};
            border-left: 4px solid ${getBorderColor(type)};
        `;

        // Icon
        const icon = document.createElement('i');
        icon.className = `fas ${getIcon(type)}`;
        icon.style.cssText = 'font-size: 1.2em; width: 24px; text-align: center;';
        notification.appendChild(icon);

        // Message
        const messageEl = document.createElement('span');
        messageEl.textContent = message;
        messageEl.style.cssText = 'flex: 1; font-size: 14px; font-weight: 500;';
        notification.appendChild(messageEl);

        // Close button
        if (options.dismissible !== false) {
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.style.cssText = `
                background: none;
                border: none;
                color: inherit;
                font-size: 20px;
                cursor: pointer;
                padding: 0 5px;
                opacity: 0.7;
                transition: opacity 0.2s;
            `;
            closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
            closeBtn.onmouseout = () => closeBtn.style.opacity = '0.7';
            closeBtn.onclick = () => remove(notification);
            notification.appendChild(closeBtn);
        }

        // Progress bar for timed notifications
        if (options.duration > 0) {
            const progressBar = document.createElement('div');
            progressBar.className = 'notification-progress';
            progressBar.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: ${getBorderColor(type)};
                width: 100%;
                animation: shrink ${options.duration}ms linear;
            `;
            notification.appendChild(progressBar);
        }

        return notification;
    }

    /**
     * Remove notification
     */
    function remove(notification) {
        if (!notification || !notification.parentNode) return;

        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, config.animationDuration);
    }

    /**
     * Get background color by type
     */
    function getBackgroundColor(type) {
        const colors = {
            success: '#d4edda',
            error: '#f8d7da',
            warning: '#fff3cd',
            info: '#d1ecf1'
        };
        return colors[type] || colors.info;
    }

    /**
     * Get text color by type
     */
    function getTextColor(type) {
        const colors = {
            success: '#155724',
            error: '#721c24',
            warning: '#856404',
            info: '#0c5460'
        };
        return colors[type] || colors.info;
    }

    /**
     * Get border color by type
     */
    function getBorderColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    /**
     * Get icon by type
     */
    function getIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Show success notification
     */
    function success(message, options = {}) {
        return show(message, 'success', options);
    }

    /**
     * Show error notification
     */
    function error(message, options = {}) {
        return show(message, 'error', options);
    }

    /**
     * Show warning notification
     */
    function warning(message, options = {}) {
        return show(message, 'warning', options);
    }

    /**
     * Show info notification
     */
    function info(message, options = {}) {
        return show(message, 'info', options);
    }

    /**
     * Clear all notifications
     */
    function clear() {
        if (container) {
            const notifications = container.querySelectorAll('.notification');
            notifications.forEach(notification => remove(notification));
        }
    }

    /**
     * Update configuration
     */
    function configure(options) {
        Object.assign(config, options);
    }

    // Public API
    return {
        init: init,
        show: show,
        success: success,
        error: error,
        warning: warning,
        info: info,
        clear: clear,
        configure: configure
    };
})();

// Add CSS animation for progress bar
const style = document.createElement('style');
style.textContent = `
    @keyframes shrink {
        from { width: 100%; }
        to { width: 0%; }
    }
`;
document.head.appendChild(style);

