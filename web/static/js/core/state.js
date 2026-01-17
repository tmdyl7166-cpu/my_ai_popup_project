/**
 * State Manager
 * Centralized state management for the application
 */
window.StateManager = (function() {
    // Private state
    const _state = {
        connection: {
            status: 'disconnected',
            lastUpdate: null
        },
        project: {
            status: 'unknown',
            components: {},
            healthScore: 0
        },
        scripts: [],
        deployment: {},
        config: {},
        logs: {}
    };

    // Subscribers
    const _subscribers = new Map();

    /**
     * Get state value by path
     */
    function get(path) {
        const keys = path.split('.');
        let value = _state;

        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return undefined;
            }
        }

        return value;
    }

    /**
     * Set state value by path
     */
    function set(path, value) {
        const keys = path.split('.');
        let current = _state;

        // Navigate to parent
        for (let i = 0; i < keys.length - 1; i++) {
            if (!(keys[i] in current)) {
                current[keys[i]] = {};
            }
            current = current[keys[i]];
        }

        // Set value
        current[keys[keys.length - 1]] = value;

        // Notify subscribers
        notifyStateChange(_state);

        return value;
    }

    /**
     * Subscribe to state changes
     */
    function subscribe(path, callback) {
        if (!_subscribers.has(path)) {
            _subscribers.set(path, []);
        }
        _subscribers.get(path).push(callback);

        // Return unsubscribe function
        return function unsubscribe() {
            const callbacks = _subscribers.get(path);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        };
    }

    /**
     * Notify all subscribers of state change
     */
    function notifyStateChange(newState) {
        _subscribers.forEach((callbacks, path) => {
            const value = get(path);
            callbacks.forEach(callback => {
                try {
                    callback(value, newState);
                } catch (error) {
                    console.error(`State subscriber error for ${path}:`, error);
                }
            });
        });
    }

    /**
     * Get entire state
     */
    function getAll() {
        return JSON.parse(JSON.stringify(_state));
    }

    /**
     * Initialize state manager
     */
    function init(initialState = {}) {
        if (Object.keys(initialState).length > 0) {
            Object.assign(_state, initialState);
        }
        console.log('StateManager initialized');
    }

    /**
     * Reset state to initial values
     */
    function reset() {
        const connection = _state.connection;
        Object.keys(_state).forEach(key => {
            _state[key] = key === 'connection' ? connection : {};
        });
        notifyStateChange(_state);
    }

    /**
     * Check if state path exists
     */
    function has(path) {
        return get(path) !== undefined;
    }

    /**
     * Remove state path
     */
    function remove(path) {
        const keys = path.split('.');
        let current = _state;

        for (let i = 0; i < keys.length - 1; i++) {
            if (current && typeof current === 'object' && keys[i] in current) {
                current = current[keys[i]];
            } else {
                return false;
            }
        }

        const lastKey = keys[keys.length - 1];
        if (current && typeof current === 'object' && lastKey in current) {
            delete current[lastKey];
            notifyStateChange(_state);
            return true;
        }

        return false;
    }

    // Public API
    return {
        get: get,
        set: set,
        subscribe: subscribe,
        getAll: getAll,
        init: init,
        reset: reset,
        has: has,
        remove: remove
    };
})();

