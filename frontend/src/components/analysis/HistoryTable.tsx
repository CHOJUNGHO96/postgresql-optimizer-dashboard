import { useNavigate } from 'react-router-dom';
import { Eye, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, Button, Badge, EmptyState, LoadingOverlay, ErrorMessage } from '@/components/common';
import { NodeTypeBadge } from './NodeTypeBadge';
import {
  formatCost,
  formatExecutionTime,
  formatRelativeTime,
  truncate,
  getCostSeverity,
} from '@/lib/utils';
import type { QueryPlanResponse } from '@/types';

interface HistoryTableProps {
  data: QueryPlanResponse[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export function HistoryTable({
  data,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  error,
  onRetry,
}: HistoryTableProps) {
  const navigate = useNavigate();
  const totalPages = Math.ceil(total / pageSize);
  const hasNext = page < totalPages;
  const hasPrev = page > 1;

  if (isLoading) {
    return (
      <Card>
        <LoadingOverlay message="히스토리를 불러오는 중..." />
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <ErrorMessage message={error} onRetry={onRetry} />
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card>
        <EmptyState
          title="분석 기록이 없습니다"
          description="쿼리를 분석하면 여기에 기록이 표시됩니다."
          icon={<Eye className="h-12 w-12" />}
          action={
            <Button variant="primary" onClick={() => navigate('/')}>
              쿼리 분석하기
            </Button>
          }
        />
      </Card>
    );
  }

  return (
    <Card padding="none" className="animate-fade-in overflow-hidden">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                쿼리
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                노드 타입
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                총 비용
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                실행 시간
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                분석 일시
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((item) => {
              const severity = getCostSeverity(item.cost_estimate.total_cost);
              return (
                <tr
                  key={item.id}
                  className="bg-white transition-colors hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-750"
                >
                  <td className="px-4 py-4">
                    <code className="block max-w-xs truncate font-mono text-sm text-gray-700 dark:text-gray-300">
                      {truncate(item.query, 50)}
                    </code>
                  </td>
                  <td className="px-4 py-4">
                    <NodeTypeBadge nodeType={item.node_type} size="sm" />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-gray-900 dark:text-white">
                        {formatCost(item.cost_estimate.total_cost)}
                      </span>
                      <Badge
                        variant={
                          severity === 'low'
                            ? 'success'
                            : severity === 'medium'
                            ? 'warning'
                            : 'danger'
                        }
                        size="sm"
                      >
                        {severity === 'low' && '낮음'}
                        {severity === 'medium' && '보통'}
                        {severity === 'high' && '높음'}
                        {severity === 'critical' && '심각'}
                      </Badge>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {formatExecutionTime(item.execution_time_ms)}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {formatRelativeTime(item.created_at)}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/analysis/${item.id}`)}
                      leftIcon={<Eye className="h-4 w-4" />}
                    >
                      상세
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3 dark:border-gray-700">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          총 <span className="font-medium text-gray-900 dark:text-white">{total}</span>개 중{' '}
          <span className="font-medium text-gray-900 dark:text-white">
            {(page - 1) * pageSize + 1}
          </span>
          -
          <span className="font-medium text-gray-900 dark:text-white">
            {Math.min(page * pageSize, total)}
          </span>
          개 표시
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page - 1)}
            disabled={!hasPrev}
            leftIcon={<ChevronLeft className="h-4 w-4" />}
          >
            이전
          </Button>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {page} / {totalPages || 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={!hasNext}
            rightIcon={<ChevronRight className="h-4 w-4" />}
          >
            다음
          </Button>
        </div>
      </div>
    </Card>
  );
}
