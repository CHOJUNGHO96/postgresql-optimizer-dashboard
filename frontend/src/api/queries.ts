import apiClient from './client';
import type {
  QueryPlanResponse,
  QueryPlanListResponse,
  AnalyzeQueryRequest,
  HealthResponse,
} from '@/types';

/**
 * API Endpoints
 */
const ENDPOINTS = {
  ANALYZE: '/query-analysis/analyze',
  GET_PLAN: (id: string) => `/query-analysis/${id}`,
  LIST_PLANS: '/query-analysis/',
  HEALTH: '/health',
} as const;

/**
 * Analyze SQL query
 */
export async function analyzeQuery(request: AnalyzeQueryRequest): Promise<QueryPlanResponse> {
  const response = await apiClient.post<QueryPlanResponse>(ENDPOINTS.ANALYZE, request);
  return response.data;
}

/**
 * Get query plan by ID
 */
export async function getQueryPlan(planId: string): Promise<QueryPlanResponse> {
  const response = await apiClient.get<QueryPlanResponse>(ENDPOINTS.GET_PLAN(planId));
  return response.data;
}

/**
 * List query plans with pagination and optional title search
 */
export async function listQueryPlans(
  params: { limit?: number; offset?: number; title_search?: string } = {}
): Promise<QueryPlanListResponse> {
  const { limit = 100, offset = 0, title_search } = params;
  const response = await apiClient.get<QueryPlanListResponse>(ENDPOINTS.LIST_PLANS, {
    params: { limit, offset, ...(title_search && { title_search }) },
  });
  return response.data;
}

/**
 * Health check
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>(ENDPOINTS.HEALTH);
  return response.data;
}
