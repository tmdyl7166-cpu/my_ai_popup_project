/**
 * Navigation Manager
 * Handles navigation and tab management
 */
window.NavigationModule = (function() {
    // Current active tab
    let activeTab = 'dashboard';
    let previousTab = null;

    /**
     * Initialize navigation module
     */
    function init() {
        console.log('NavigationModule initialized');
        this.bindEvents();
        this.updateActiveState();
    }

    /**
     * Bind event handlers
     */
    function bindEvents() {
        // Navigation links
        document.querySelectorAll('[data-nav]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.dataset.nav;
                this.navigateTo(target);
            });
        });

        // Tab change events
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.dataset.bsTarget;
                this.onTabChanged(target);
            });
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + number for quick navigation
            if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '9') {
                e.preventDefault();
                this.navigateToByIndex(parseInt(e.key));
            }
        });
    }

    /**
     * Navigate to specific section
     */
    function navigateTo(target) {
        if (!target) return;

        previousTab = activeTab;
        activeTab = target;

        // Find corresponding tab button
        const tabButton = document.querySelector(`[data-bs-target="#${target}"]`) ||
                         document.querySelector(`[href="#${target}"]`) ||
                         document.querySelector(`[data-nav="${target}"]`);

        if (tabButton) {
            // Use Bootstrap tab if available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {
                new bootstrap.Tab(tabButton).show();
            } else {
                // Fallback: direct show
                tabButton.click();
            }
        }

        // Update URL hash
        if (target !== 'dashboard') {
            history.pushState(null, null, `#${target}`);
        } else {
            history.pushState(null, null, window.location.pathname);
        }

        // Notify state change
        StateManager.set('navigation.activeTab', target);
    }

    /**
     * Navigate by index (1-9)
     */
    function navigateToByIndex(index) {
        const tabs = ['dashboard', 'scripts', 'deployment', 'config', 'logs'];
        if (index >= 1 && index <= tabs.length) {
            this.navigateTo(tabs[index - 1]);
        }
    }

    /**
     * Handle tab change
     */
    function onTabChanged(target) {
        // Extract tab name from # prefix
        const tabName = target.replace('#', '');

        // Update active state
        activeTab = tabName;

        // Load data for specific tabs
        this.loadTabData(tabName);

        // Notify
        console.log(`Navigated to: ${tabName}`);
    }

    /**
     * Load data when tab is activated
     */
    function loadTabData(tabName) {
        switch (tabName) {
            case 'dashboard':
                if (typeof DashboardModule !== 'undefined') {
                    DashboardModule.refreshData();
                }
                break;
            case 'scripts':
                if (typeof ScriptsModule !== 'undefined') {
                    ScriptsModule.refresh();
                }
                break;
            case 'deployment':
                if (typeof DeploymentModule !== 'undefined') {
                    DeploymentModule.loadDeploymentProgress();
                }
                break;
            case 'config':
                if (typeof ConfigModule !== 'undefined') {
                    ConfigModule.refresh();
                }
                break;
            case 'logs':
                // Already handled by LogsModule
                break;
        }
    }

    /**
     * Update active state in UI
     */
    function updateActiveState() {
        // Update nav links
        document.querySelectorAll('[data-nav]').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.nav === activeTab) {
                link.classList.add('active');
            }
        });

        // Update tab links
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.classList.remove('active');
            const target = tab.dataset.bsTarget;
            if (target && target.replace('#', '') === activeTab) {
                tab.classList.add('active');
            }
        });
    }

    /**
     * Go back to previous tab
     */
    function goBack() {
        if (previousTab) {
            this.navigateTo(previousTab);
        }
    }

    /**
     * Get current active tab
     */
    function getActiveTab() {
        return activeTab;
    }

    /**
     * Check if tab is active
     */
    function isActive(tabName) {
        return activeTab === tabName;
    }

    /**
     * Add navigation item dynamically
     */
    function addNavItem(options) {
        const { id, label, icon, target, position = 'end' } = options;

        const item = document.createElement('a');
        item.className = 'nav-link';
        item.dataset.nav = target || id;
        item.href = `#${target || id}`;
        item.innerHTML = icon ? `<i class="${icon} me-2"></i>${label}` : label;

        const container = document.getElementById('nav-container') ||
                         document.querySelector('.nav.flex-column') ||
                         document.querySelector('.nav');

        if (container) {
            if (position === 'start') {
                container.insertBefore(item, container.firstChild);
            } else {
                container.appendChild(item);
            }

            // Bind click event
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateTo(target || id);
            });
        }

        return item;
    }

    /**
     * Remove navigation item
     */
    function removeNavItem(id) {
        const item = document.querySelector(`[data-nav="${id}"]`);
        if (item) {
            item.remove();
        }
    }

    /**
     * Handle browser back/forward
     */
    function handleHashChange() {
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.navigateTo(hash);
        } else {
            this.navigateTo('dashboard');
        }
    }

    /**
     * Start hash change listener
     */
    function startHashListener() {
        window.addEventListener('hashchange', () => this.handleHashChange());
    }

    /**
     * Destroy module
     */
    function destroy() {
        document.querySelectorAll('[data-nav]').forEach(link => {
            link.replaceWith(link.cloneNode(true));
        });
        console.log('NavigationModule destroyed');
    }

    // Public API
    return {
        init: init,
        navigateTo: navigateTo,
        navigateToByIndex: navigateToByIndex,
        onTabChanged: onTabChanged,
        loadTabData: loadTabData,
        updateActiveState: updateActiveState,
        goBack: goBack,
        getActiveTab: getActiveTab,
        isActive: isActive,
        addNavItem: addNavItem,
        removeNavItem: removeNavItem,
        handleHashChange: handleHashChange,
        startHashListener: startHashListener,
        destroy: destroy
    };
})();

