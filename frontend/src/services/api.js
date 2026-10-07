const API_BASE = '/api/v1';

/**
 * Fetch wrapper with token authorization and JSON handling
 */
async function request(endpoint, options = {}) {
  const token = localStorage.getItem('dept_access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({
    success: false,
    message: 'Invalid server response.',
  }));

  if (!response.ok) {
    const errorMsg = data.message || `Request failed with status ${response.status}`;
    const error = new Error(errorMsg);
    error.status = response.status;
    error.details = data.error?.details;
    throw error;
  }

  return data;
}

export const api = {
  // Public Portal Endpoints (Zero authentication required)
  getDepartmentInfo: async () => {
    const res = await request('/public/department-info');
    return res.data?.department;
  },

  getFaculty: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/faculty${query ? `?${query}` : ''}`);
    return res.data?.faculty || [];
  },

  getFacultyDetail: async (id) => {
    const res = await request(`/public/faculty/${id}`);
    return res.data?.faculty;
  },

  getEvents: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/events${query ? `?${query}` : ''}`);
    return res.data?.events || [];
  },

  getAchievements: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/achievements${query ? `?${query}` : ''}`);
    return res.data?.achievements || [];
  },

  getAnnouncements: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/announcements${query ? `?${query}` : ''}`);
    return res.data?.announcements || [];
  },

  getPrograms: async () => {
    const res = await request('/public/programs');
    return res.data?.programs || [];
  },

  getGallery: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/gallery${query ? `?${query}` : ''}`);
    return res.data?.gallery || [];
  },

  getNews: async () => {
    const res = await request('/public/news');
    return res.data?.news || [];
  },

  getPublicStats: async () => {
    const res = await request('/public/stats');
    return res.data?.stats || {};
  },

  // Authentication Endpoints
  login: async (email, password) => {
    const res = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await request('/auth/me');
    return res.data?.user;
  },
};
