import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { optimizeQuery, listOptimizations, getOptimization } from '@/api/queries';
import type { OptimizeQueryRequest } from '@/types/optimization';

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
