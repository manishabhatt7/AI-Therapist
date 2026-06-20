import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Inject JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// ── Sessions ──────────────────────────────────────────────────────
export const sessionsAPI = {
  list: () => api.get('/chat/sessions'),
  create: () => api.post('/chat/sessions'),
};

// ── Messages ──────────────────────────────────────────────────────
export const messagesAPI = {
  send: (sessionId, message) =>
    api.post(`/chat/sessions/${sessionId}/message`, { message }),

  sendVoice: (sessionId, audioBlob, filename = 'recording.webm') => {
    const form = new FormData();
    form.append('audio', audioBlob, filename);
    return api.post(`/chat/sessions/${sessionId}/voice`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  history: (sessionId, limit = 50) =>
    api.get(`/chat/sessions/${sessionId}/messages?limit=${limit}`),

  sentimentSummary: (sessionId) =>
    api.get(`/chat/sessions/${sessionId}/sentiment-summary`),
};

export default api;
