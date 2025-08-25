import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface CompetitorCreateRequest {
  name: string;
  website?: string;
  category?: string;
  tracking_urls: string[];
}

export interface CrawlRequest {
  competitor_id?: string;
  urls?: string[];
  mode?: string;
}

// API functions
export const apiService = {
  // Competitors
  getCompetitors: async () => {
    const response = await api.get('/competitors');
    return response.data;
  },

  createCompetitor: async (competitor: CompetitorCreateRequest) => {
    const response = await api.post('/competitors', competitor);
    return response.data;
  },

  getCompetitor: async (id: string) => {
    const response = await api.get(`/competitors/${id}`);
    return response.data;
  },

  deleteCompetitor: async (id: string) => {
    const response = await api.delete(`/competitors/${id}`);
    return response.data;
  },

  // Tracking
  getTrackingStatus: async () => {
    const response = await api.get('/tracking/status');
    return response.data;
  },

  startTracking: async (request?: CrawlRequest) => {
    const response = await api.post('/tracking/start', request);
    return response.data;
  },

  stopTracking: async () => {
    const response = await api.post('/tracking/stop');
    return response.data;
  },

  crawlCompetitor: async (request: CrawlRequest) => {
    const response = await api.post('/crawl', request);
    return response.data;
  },

  // Analytics
  getDashboardData: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  getInsights: async () => {
    const response = await api.get('/insights/trending');
    return response.data;
  },

  // Changes
  getChanges: async (params?: {
    competitor_id?: string;
    change_type?: string;
    days?: number;
    limit?: number;
  }) => {
    const response = await api.get('/changes', { params });
    return response.data;
  },

  // Reports
  getReports: async (limit?: number) => {
    const response = await api.get('/reports', { params: { limit } });
    return response.data;
  },

  getReport: async (week: string) => {
    const response = await api.get(`/reports/${week}`);
    return response.data;
  },

  generateReport: async () => {
    const response = await api.post('/reports/generate');
    return response.data;
  },

  // Health
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default apiService;
