import { OptimizationMetrics } from './OptimizationMetrics';
import { OptimizedQueryViewer } from './OptimizedQueryViewer';
import type { OptimizedQueryResponse } from '@/types/optimization';
import { cn } from '@/lib/utils';

interface OptimizationResultProps {
  optimization: OptimizedQueryResponse;
  originalQuery: string;
  className?: string;
}

export function OptimizationResult({
  optimization,
  originalQuery,
  className,
}: OptimizationResultProps) {
  return (
    <div className={cn('space-y-6', className)}>
      <OptimizationMetrics optimization={optimization} />
      <OptimizedQueryViewer
        optimization={optimization}
        originalQuery={originalQuery}
      />
    </div>
  );
}
