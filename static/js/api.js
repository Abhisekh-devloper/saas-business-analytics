// SaaS Business Analytics - API Client Layer

const API = (() => {
  const TOKEN_KEY = 'saas_auth_token';
  const USER_KEY = 'saas_user';

  const getToken = () => localStorage.getItem(TOKEN_KEY);
  const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
  const removeToken = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const getStoredUser = () => {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  };
  const setStoredUser = (user) => localStorage.setItem(USER_KEY, JSON.stringify(user));

  const getCsrfToken = () => {
    const name = 'csrftoken';
    const matches = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)'));
    return matches ? decodeURIComponent(matches[1]) : '';
  };

  const request = async (url, options = {}) => {
    const headers = options.headers || {};
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    // Don't set Content-Type for FormData (browser sets boundary automatically)
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      removeToken();
      window.dispatchEvent(new CustomEvent('auth:expired'));
      throw new Error('Session expired or unauthorized. Please log in.');
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await response.json();
      if (!response.ok) {
        const errorMsg = data.error || data.detail || (typeof data === 'object' ? JSON.stringify(data) : 'Request failed');
        throw new Error(errorMsg);
      }
      return data;
    }

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    return response;
  };

  return {
    auth: {
      getToken,
      isAuthenticated: () => !!getToken(),
      getUser: getStoredUser,
      async register(username, email, password) {
        const res = await request('/api/auth/register/', {
          method: 'POST',
          body: JSON.stringify({ username, email, password })
        });
        setToken(res.token);
        setStoredUser(res.user);
        return res;
      },
      async login(username, password) {
        const res = await request('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify({ username, password })
        });
        setToken(res.token);
        setStoredUser(res.user);
        return res;
      },
      async demoLogin() {
        const res = await request('/api/auth/demo-login/', {
          method: 'POST'
        });
        setToken(res.token);
        setStoredUser(res.user);
        return res;
      },
      async fetchProfile() {
        const user = await request('/api/auth/user/');
        setStoredUser(user);
        return user;
      },
      async logout() {
        try {
          await request('/api/auth/logout/', { method: 'POST' });
        } catch (e) {
          console.warn('Logout API error:', e);
        } finally {
          removeToken();
        }
      }
    },

    datasets: {
      list: () => request('/api/analytics/datasets/'),
      get: (id) => request(`/api/analytics/datasets/${id}/`),
      setActive: (id) => request(`/api/analytics/datasets/${id}/set-active/`, { method: 'POST' }),
      delete: (id) => request(`/api/analytics/datasets/${id}/`, { method: 'DELETE' }),
      loadSample: () => request('/api/analytics/datasets/load-sample/', { method: 'POST' }),
      upload: (formData) => request('/api/analytics/datasets/upload/', {
        method: 'POST',
        body: formData
      })
    },

    analytics: {
      getDashboard: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return request(`/api/analytics/dashboard/?${query}`);
      },
      getInsights: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return request(`/api/analytics/insights/?${query}`);
      },
      getDataTable: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return request(`/api/analytics/data-table/?${query}`);
      },
      getExportUrl: (type, params = {}) => {
        const query = new URLSearchParams(params).toString();
        return `/api/analytics/export/${type}/?${query}`;
      }
    }
  };
})();

