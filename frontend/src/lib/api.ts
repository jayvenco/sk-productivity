const API_BASE = '/api';

async function request(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
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

export const api = {
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
  },

  // Pomodoro
  pomodoro: {
    status: () => request('/pomodoro/status'),
    start: (data) => request('/pomodoro/start', { method: 'POST', body: JSON.stringify(data) }),
    stop: () => request('/pomodoro/stop', { method: 'POST' }),
    list: () => request('/pomodoro'),
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
};