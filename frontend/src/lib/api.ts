const API_BASE = '/api';
const TOKEN_KEY = 'skp_auth_token';
const USER_KEY = 'skp_auth_user';

async function request(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}${path}`, { headers, ...options });
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
    return data;
  } catch (e) {
    if (e instanceof TypeError && e.message === 'Failed to fetch') {
      throw new Error('Netwerkfout — server mogelijk offline');
    }
    throw e;
  }
}

export function getToken() {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getUsername() {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(USER_KEY);
}

export function setAuth(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, username);
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated() {
  return !!getToken();
}

export const api = {
  // Auth
  auth: {
    login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    verify: () => request('/auth/verify'),
    changePassword: (data) => request('/auth/password', { method: 'PUT', body: JSON.stringify(data) }),
    changeUsername: (data) => request('/auth/username', { method: 'PUT', body: JSON.stringify(data) }),
  },

  // Notes
  notes: {
    list: () => request('/notes'),
    get: (id) => request(`/notes/${id}`),
    create: (data) => request('/notes', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/notes/${id}`, { method: 'DELETE' }),
  },

  // Tasks
  tasks: {
    list: () => request('/tasks'),
    get: (id) => request(`/tasks/${id}`),
    create: (data) => request('/tasks', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
  },

  // Kanban
  kanban: {
    list: () => request('/kanban'),
    get: (id) => request(`/kanban/${id}`),
    create: (data) => request('/kanban', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/kanban/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/kanban/${id}`, { method: 'DELETE' }),
    columns: {
      list: () => request('/kanban/columns'),
      create: (data) => request('/kanban/columns', { method: 'POST', body: JSON.stringify(data) }),
      update: (id, data) => request(`/kanban/columns/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
      rename: (id, name) => request(`/kanban/columns/${id}`, { method: 'PUT', body: JSON.stringify({ name }) }),
      delete: (id) => request(`/kanban/columns/${id}`, { method: 'DELETE' }),
    },
    swimlanes: {
      list: () => request('/kanban/swimlanes'),
      create: (data) => request('/kanban/swimlanes', { method: 'POST', body: JSON.stringify(data) }),
      update: (id, data) => request(`/kanban/swimlanes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
      rename: (id, name) => request(`/kanban/swimlanes/${id}`, { method: 'PUT', body: JSON.stringify({ name }) }),
      delete: (id) => request(`/kanban/swimlanes/${id}`, { method: 'DELETE' }),
    },
  },

  // Pomodoro
  pomodoro: {
    status: () => request('/pomodoro/status'),
    start: (data) => request('/pomodoro/start', { method: 'POST', body: JSON.stringify(data) }),
    stop: () => request('/pomodoro/stop', { method: 'POST' }),
    list: () => request('/pomodoro'),
    report: (params) => request(`/pomodoro/report?days=${params.days||30}${params.item_type ? `&item_type=${params.item_type}` : ''}${params.item_id ? `&item_id=${params.item_id}` : ''}`),
  },

  // Wiki
  wiki: {
    list: (q) => request(`/wiki${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    get: (id) => request(`/wiki/${id}`),
    getBySlug: (slug) => request(`/wiki/by-slug/${slug}`),
    create: (data) => request('/wiki', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/wiki/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/wiki/${id}`, { method: 'DELETE' }),
  },

  // Snippets
  snippets: {
    list: () => request('/snippets'),
    get: (id) => request(`/snippets/${id}`),
    create: (data) => request('/snippets', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/snippets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/snippets/${id}`, { method: 'DELETE' }),
  },

  // Tags
  tags: {
    list: () => request('/tags'),
    create: (data) => request('/tags', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/tags/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/tags/${id}`, { method: 'DELETE' }),
    getForItem: (itemType, itemId) => request(`/tags/attached?item_type=${itemType}&item_id=${itemId}`),
    attach: (tagId, itemType, itemId) => request(`/tags/attach?tag_id=${tagId}&item_type=${itemType}&item_id=${itemId}`, { method: 'POST' }),
    detach: (tagId, itemType, itemId) => request(`/tags/attachment/${tagId}?item_type=${itemType}&item_id=${itemId}`, { method: 'DELETE' }),
  },

  // Backup
  backup: {
    create: () => request('/backup', { method: 'POST' }),
    list: () => request('/backup'),
    restore: (filename) => request(`/backup/restore/${encodeURIComponent(filename)}`, { method: 'POST' }),
    delete: (filename) => request(`/backup/${encodeURIComponent(filename)}`, { method: 'DELETE' }),
  },

  // Stickies
  stickies: {
    list: () => request('/stickies'),
    get: (id) => request(`/stickies/${id}`),
    create: (data) => request('/stickies', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/stickies/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/stickies/${id}`, { method: 'DELETE' }),
    bulkDelete: (ids) => request('/stickies/bulk-delete', { method: 'POST', body: JSON.stringify({ ids }) }),
  },

  // Calendar
  calendar: {
    deadlines: (days = 60) => request(`/calendar/deadlines?days=${days}`),
  },

  // Reports
  reports: {
    dashboard: (days = 90) => request(`/reports/dashboard?days=${days}`),
  },

  // Background
  background: {
    upload: (file) => {
      const form = new FormData();
      form.append('file', file);
      const token = getToken();
      return fetch('/api/background/upload', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: form,
      }).then(async r => {
        if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || 'Upload failed'); }
        return r.json();
      });
    },
    delete: () => request('/background', { method: 'DELETE' }),
    status: () => request('/background/status'),
  },

  // Projects
  projects: {
    list: () => request('/projects'),
    create: (data) => request('/projects', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
  },
};