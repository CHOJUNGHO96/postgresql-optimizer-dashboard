import axios, { type AxiosError } from 'axios';
import type { ApiError } from '@/types';

// API Client with base configuration
export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers or transformations here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const apiError: ApiError = {
      detail: error.response?.data?.detail || error.message || '알 수 없는 오류가 발생했습니다.',
      status: error.response?.status,
    };
    return Promise.reject(apiError);
  }
);

export default apiClient;
