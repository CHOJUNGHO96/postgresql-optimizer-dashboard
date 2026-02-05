import apiClient from './client';
import type {
  QueryPlanResponse,
  QueryPlanListResponse,
  AnalyzeQueryRequest,
  AnalyzePlanRequest,
  HealthResponse,
} from '@/types';
import type {
  OptimizeQueryRequest,
  OptimizedQueryResponse,
  CreateTaskRequest,
  TaskResponse,
} from '@/types/optimization';

/**
 * API Endpoints
 */
const ENDPOINTS = {
  ANALYZE: '/query-analysis/analyze',
  ANALYZE_PLAN: '/query-analysis/analyze-plan',
  GET_PLAN: (id: string) => `/query-analysis/${id}`,
  LIST_PLANS: '/query-analysis/',
  OPTIMIZE_QUERY: (planId: string) => `/query-analysis/${planId}/optimize`,
  OPTIMIZE_QUERY_ASYNC: (planId: string) => `/query-analysis/${planId}/optimize/async`,
  GET_TASK_STATUS: (taskId: string) => `/query-analysis/tasks/${taskId}`,
  GET_OPTIMIZATIONS: (planId: string) => `/query-analysis/${planId}/optimize`,
  GET_OPTIMIZATION: (planId: string, optimizationId: string) =>
    `/query-analysis/${planId}/optimize/${optimizationId}`,
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
 * Analyze EXPLAIN JSON directly
 */
export async function analyzePlan(request: AnalyzePlanRequest): Promise<QueryPlanResponse> {
  const response = await apiClient.post<QueryPlanResponse>(ENDPOINTS.ANALYZE_PLAN, request);
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

/**
 * Optimize query using AI
 */
export async function optimizeQuery(
  planId: string,
  request: OptimizeQueryRequest
): Promise<OptimizedQueryResponse> {
  const response = await apiClient.post<OptimizedQueryResponse>(
    ENDPOINTS.OPTIMIZE_QUERY(planId),
    request
  );
  return response.data;
}

/**
 * List optimization history for a query plan
 */
export async function listOptimizations(
  planId: string
): Promise<OptimizedQueryResponse[]> {
  const response = await apiClient.get<OptimizedQueryResponse[]>(
    ENDPOINTS.GET_OPTIMIZATIONS(planId)
  );
  return response.data;
}

/**
 * Get a specific optimization by ID
 */
export async function getOptimization(
  planId: string,
  optimizationId: string
): Promise<OptimizedQueryResponse> {
  const response = await apiClient.get<OptimizedQueryResponse>(
    ENDPOINTS.GET_OPTIMIZATION(planId, optimizationId)
  );
  return response.data;
}

/**
 * Create async optimization task (non-blocking)
 */
export async function optimizeQueryAsync(
  planId: string,
  request: CreateTaskRequest
): Promise<TaskResponse> {
  const response = await apiClient.post<TaskResponse>(
    ENDPOINTS.OPTIMIZE_QUERY_ASYNC(planId),
    request
  );
  return response.data;
}

/**
 * Get task status
 */
export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const response = await apiClient.get<TaskResponse>(
    ENDPOINTS.GET_TASK_STATUS(taskId)
  );
  return response.data;
}
