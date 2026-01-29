import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { analyzeQuery, getQueryPlan, listQueryPlans, checkHealth } from '@/api';
import type { AnalyzeQueryRequest, ApiError } from '@/types';

// Query Keys
export const queryKeys = {
  all: ['queryPlans'] as const,
  lists: () => [...queryKeys.all, 'list'] as const,
  list: (params: { limit?: number; offset?: number }) => [...queryKeys.lists(), params] as const,
  details: () => [...queryKeys.all, 'detail'] as const,
  detail: (id: string) => [...queryKeys.details(), id] as const,
  health: ['health'] as const,
};

/**
 * Hook to analyze SQL query
 */
export function useAnalyzeQuery() {
  const queryClient = useQueryClient();

  return useMutation<Awaited<ReturnType<typeof analyzeQuery>>, ApiError, AnalyzeQueryRequest>({
    mutationFn: (request: AnalyzeQueryRequest) => analyzeQuery(request),
    onSuccess: () => {
      // Invalidate list queries to refresh the history
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() });
    },
  });
}

/**
 * Hook to get query plan by ID
 */
export function useQueryPlan(planId: string, enabled = true) {
  return useQuery<Awaited<ReturnType<typeof getQueryPlan>>, ApiError>({
    queryKey: queryKeys.detail(planId),
    queryFn: () => getQueryPlan(planId),
    enabled: enabled && !!planId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to list query plans
 */
export function useQueryPlanList(params: { limit?: number; offset?: number } = {}) {
  return useQuery<Awaited<ReturnType<typeof listQueryPlans>>, ApiError>({
    queryKey: queryKeys.list(params),
    queryFn: () => listQueryPlans(params),
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook for health check
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: checkHealth,
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
}
