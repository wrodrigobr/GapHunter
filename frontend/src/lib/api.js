import axios from 'axios';

// Configuração base da API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Criar instância do axios
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar respostas e erros
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Se token expirou, redirecionar para login
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    
    // Log de erros em produção
    if (import.meta.env.VITE_ENVIRONMENT === 'production') {
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.response?.data?.detail || error.message
      });
    }
    
    return Promise.reject(error);
  }
);

// Serviços da API
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: () => api.post('/auth/refresh'),
};

export const userService = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  getStats: () => api.get('/users/stats'),
};

export const handsService = {
  upload: (formData) => api.post('/hands/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getHistory: (page = 1, limit = 10) => api.get(`/hands/history?page=${page}&limit=${limit}`),
  getHand: (id) => api.get(`/hands/${id}`),
  analyze: (id) => api.post(`/hands/${id}/analyze`),
};

export const gapsService = {
  getGaps: (userId) => api.get(`/gaps/user/${userId}`),
  getGapDetails: (gapId) => api.get(`/gaps/${gapId}`),
  updateGapStatus: (gapId, status) => api.put(`/gaps/${gapId}/status`, { status }),
};

export const performanceService = {
  getStats: (period = 30) => api.get(`/performance/stats?period=${period}`),
  addTournament: (data) => api.post('/performance/tournaments', data),
  getTournaments: (page = 1, limit = 10) => api.get(`/performance/tournaments?page=${page}&limit=${limit}`),
  getROIChart: (period = 30) => api.get(`/performance/roi-chart?period=${period}`),
};

export const coachingService = {
  getCoachProfile: () => api.get('/coaching/coach/profile'),
  createCoachProfile: (data) => api.post('/coaching/coach/profile', data),
  getStudents: () => api.get('/coaching/coach/students'),
  getStudentProgress: (studentId) => api.get(`/coaching/coach/students/${studentId}/progress`),
  addNote: (data) => api.post('/coaching/coach/notes', data),
  getAvailableCoaches: () => api.get('/coaching/coaches'),
};

export const visionService = {
  getSettings: () => api.get('/coaching/vision/settings'),
  updateSettings: (data) => api.put('/coaching/vision/settings', data),
  getPublicPlayers: () => api.get('/coaching/vision/players'),
  createAnalysis: (data) => api.post('/coaching/vision/analyze', data),
  getAnalyses: () => api.get('/coaching/vision/analyses'),
};

export const subscriptionService = {
  getPlans: () => api.get('/subscription/plans'),
  getMySubscription: () => api.get('/subscription/my-subscription'),
  subscribe: (data) => api.post('/subscription/subscribe', data),
  checkFeatureAccess: (feature) => api.get(`/subscription/feature-access/${feature}`),
  
  // Afiliados
  joinAffiliate: (data) => api.post('/subscription/affiliate/join', data),
  getAffiliateStats: () => api.get('/subscription/affiliate/stats'),
  getAffiliateDashboard: () => api.get('/subscription/affiliate/dashboard'),
  
  // Clube
  joinClub: () => api.post('/subscription/club/join'),
  getClubStats: () => api.get('/subscription/club/stats'),
  addClubPoints: (points, reason) => api.post(`/subscription/club/add-points?points=${points}&reason=${reason}`),
  getLeaderboard: (limit = 10) => api.get(`/subscription/club/leaderboard?limit=${limit}`),
};

export default api;

