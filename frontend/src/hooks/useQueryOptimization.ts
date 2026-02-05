import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  optimizeQuery,
  optimizeQueryAsync,
  getTaskStatus,
  listOptimizations,
  getOptimization,
} from '@/api/queries';
import type { OptimizeQueryRequest, CreateTaskRequest } from '@/types/optimization';

/**
 * Hook for optimizing a query using AI
 */
export function useOptimizeQuery(planId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: OptimizeQueryRequest) => optimizeQuery(planId, request),
    onSuccess: () => {
      // Invalidate optimization list to refetch
      queryClient.invalidateQueries({ queryKey: ['optimizations', planId] });
      // 즉시 refetch 실행하여 UI 업데이트
      queryClient.refetchQueries({ queryKey: ['optimizations', planId] });
    },
  });
}

/**
 * Hook for fetching optimization history
 */
export function useOptimizations(planId: string) {
  return useQuery({
    queryKey: ['optimizations', planId],
    queryFn: () => listOptimizations(planId),
    enabled: !!planId,
  });
}

/**
 * Hook for fetching a specific optimization
 */
export function useOptimization(planId: string, optimizationId: string) {
  return useQuery({
    queryKey: ['optimization', planId, optimizationId],
    queryFn: () => getOptimization(planId, optimizationId),
    enabled: !!planId && !!optimizationId,
  });
}

/**
 * Hook for async query optimization with background task
 */
export function useOptimizeQueryAsync(planId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateTaskRequest) => optimizeQueryAsync(planId, request),
    onSuccess: () => {
      // Task invalidation happens after task completes
    },
  });
}

/**
 * Hook for polling task status
 */
export function useTaskStatus(taskId: string | null, enabled: boolean = true) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ['task-status', taskId],
    queryFn: () => getTaskStatus(taskId!),
    enabled: enabled && !!taskId,
    refetchInterval: (data) => {
      // Poll every 2 seconds while task is pending/processing
      if (data?.status === 'pending' || data?.status === 'processing') {
        return 2000;
      }
      // Stop polling when completed/failed
      return false;
    },
    refetchIntervalInBackground: true,
    retry: 3,
    retryDelay: 1000,
  });
}
