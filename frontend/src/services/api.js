import axios from 'axios';
import toast from 'react-hot-toast';

const BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail;

    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      if (detail === 'TOKEN_EXPIRED') {
        toast.error('Your session has expired. Please log in again.', { duration: 4000 });
      }
      // Small delay so toast shows before redirect
      setTimeout(() => { window.location.href = '/login'; }, 1200);
    }

    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────────
export const authAPI = {
  register:            (data) => api.post('/auth/register', data),
  login:               (data) => api.post('/auth/login', data),
  logout:              ()     => api.post('/auth/logout'),
  me:                  ()     => api.get('/auth/me'),
  resendVerification:  (email) => api.post('/auth/resend-verification', { email }),
};

// ── Sessions ──────────────────────────────────────────────────────
export const sessionsAPI = {
  list:   ()     => api.get('/chat/sessions'),
  create: ()     => api.post('/chat/sessions'),
};

// ── Messages ──────────────────────────────────────────────────────
export const messagesAPI = {
  send: (sessionId, message, tts = true) =>
    api.post(`/chat/sessions/${sessionId}/message?tts=${tts}`, { message }),

  sendVoice: (sessionId, audioBlob, filename = 'recording.webm', tts = true) => {
    const form = new FormData();
    form.append('audio', audioBlob, filename);
    return api.post(`/chat/sessions/${sessionId}/voice?tts=${tts}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  history:         (sessionId, limit = 50) =>
    api.get(`/chat/sessions/${sessionId}/messages?limit=${limit}`),

  sentimentSummary: (sessionId) =>
    api.get(`/chat/sessions/${sessionId}/sentiment-summary`),
};

export default api;