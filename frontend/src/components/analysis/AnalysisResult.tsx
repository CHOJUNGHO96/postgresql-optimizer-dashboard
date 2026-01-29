import { Clock, Calendar, FileCode2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, JsonTreeView, Badge } from '@/components/common';
import { CostCard } from './CostCard';
import { NodeTypeCard } from './NodeTypeBadge';
import { SqlEditor } from '@/components/query';
import {
  formatExecutionTime,
  formatDate,
  getCostSeverity,
  getCostSeverityStyles,
  cn,
} from '@/lib/utils';
import type { QueryPlanResponse } from '@/types';

interface AnalysisResultProps {
  result: QueryPlanResponse;
  showQuery?: boolean;
  className?: string;
}

export function AnalysisResult({
  result,
  showQuery = true,
  className,
}: AnalysisResultProps) {
  const severity = getCostSeverity(result.cost_estimate.total_cost);
  const severityStyles = getCostSeverityStyles(severity);

  return (
    <div className={cn('space-y-6 animate-fade-in', className)}>
      {/* Summary Header */}
      <Card padding="lg">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div
              className={cn(
                'flex h-12 w-12 items-center justify-center rounded-xl',
                severityStyles.bg,
                severityStyles.border,
                'border'
              )}
            >
              <FileCode2 className={cn('h-6 w-6', severityStyles.color)} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                쿼리 분석 결과
              </h2>
              <div className="mt-1 flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  {formatDate(result.created_at)}
                </span>
                {result.execution_time_ms !== null && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {formatExecutionTime(result.execution_time_ms)}
                  </span>
                )}
              </div>
            </div>
          </div>
          <Badge
            variant={
              severity === 'low'
                ? 'success'
                : severity === 'medium'
                ? 'warning'
                : 'danger'
            }
            size="lg"
          >
            비용 수준: {severityStyles.label}
          </Badge>
        </div>
      </Card>

      {/* Node Type */}
      <NodeTypeCard nodeType={result.node_type} />

      {/* Cost Estimates */}
      <CostCard costEstimate={result.cost_estimate} />

      {/* Query (if enabled) */}
      {showQuery && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle>실행된 쿼리</CardTitle>
          </CardHeader>
          <CardContent>
            <SqlEditor
              value={result.query}
              onChange={() => {}}
              readOnly
              minHeight="100px"
              maxHeight="200px"
            />
          </CardContent>
        </Card>
      )}

      {/* Raw Plan */}
      <Card padding="lg">
        <CardHeader>
          <CardTitle>실행 계획 상세 (JSON)</CardTitle>
        </CardHeader>
        <CardContent>
          <JsonTreeView
            data={result.plan_raw}
            defaultExpanded
            maxDepth={4}
          />
        </CardContent>
      </Card>
    </div>
  );
}
