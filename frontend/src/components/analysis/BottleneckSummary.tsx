import { AlertTriangle, CheckCircle, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/common';
import { cn, formatCost } from '@/lib/utils';
import type { BottleneckNode } from '@/types';

interface BottleneckSummaryProps {
  bottlenecks: BottleneckNode[];
  totalCost: number;
  className?: string;
  onNodeClick?: (nodeId: string) => void;
}

const severityConfig = {
  critical: {
    badge: 'danger' as const,
    label: '심각',
    barColor: 'bg-red-500',
  },
  high: {
    badge: 'warning' as const,
    label: '높음',
    barColor: 'bg-orange-500',
  },
  medium: {
    badge: 'info' as const,
    label: '보통',
    barColor: 'bg-yellow-500',
  },
  low: {
    badge: 'default' as const,
    label: '낮음',
    barColor: 'bg-blue-500',
  },
};

export function BottleneckSummary({
  bottlenecks,
  totalCost,
  className,
  onNodeClick,
}: BottleneckSummaryProps) {
  const hasBottlenecks = bottlenecks.length > 0;

  return (
    <Card padding="lg" className={className}>
      <CardHeader>
        <div className="flex items-center gap-2">
          {hasBottlenecks ? (
            <AlertTriangle className="h-5 w-5 text-orange-500" />
          ) : (
            <CheckCircle className="h-5 w-5 text-green-500" />
          )}
          <CardTitle>병목 지점 요약</CardTitle>
        </div>
        <Badge variant={hasBottlenecks ? 'warning' : 'success'}>
          {hasBottlenecks ? `${bottlenecks.length}개 발견` : '성능 병목 없음'}
        </Badge>
      </CardHeader>

      <CardContent>
        {hasBottlenecks ? (
          <div className="space-y-4">
            {/* 병목 노드 목록 */}
            <div className="space-y-3">
              {bottlenecks.map((bottleneck, index) => (
                <BottleneckItem
                  key={bottleneck.node.id}
                  bottleneck={bottleneck}
                  rank={index + 1}
                  onClick={() => onNodeClick?.(bottleneck.node.id)}
                />
              ))}
            </div>

            {/* 비용 분포 차트 */}
            <div className="mt-6">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">비용 분포</span>
                <span className="text-gray-500 dark:text-gray-500">
                  총 비용: {formatCost(totalCost)}
                </span>
              </div>
              <CostDistributionBar bottlenecks={bottlenecks} />
              <CostDistributionLegend bottlenecks={bottlenecks} />
            </div>
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            <CheckCircle className="mx-auto mb-2 h-8 w-8 text-green-500" />
            <p>쿼리 실행 계획에서 주요 병목 지점이 발견되지 않았습니다.</p>
            <p className="mt-1 text-sm">쿼리가 효율적으로 실행될 것으로 예상됩니다.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface BottleneckItemProps {
  bottleneck: BottleneckNode;
  rank: number;
  onClick?: () => void;
}

function BottleneckItem({ bottleneck, rank, onClick }: BottleneckItemProps) {
  const { node, contribution, severity, reason } = bottleneck;
  const config = severityConfig[severity];

  return (
    <div
      className={cn(
        'group rounded-lg border p-3 transition-all',
        'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50',
        onClick && 'cursor-pointer hover:border-gray-300 hover:bg-gray-100 dark:hover:border-gray-600 dark:hover:bg-gray-800'
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
            {rank}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <Badge variant={config.badge} size="sm">
                {node.nodeType}
              </Badge>
              {node.relationName && (
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {node.relationName}
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {reason}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            {contribution.percentage.toFixed(1)}%
          </span>
          {onClick && (
            <ChevronRight className="h-4 w-4 text-gray-400 transition-transform group-hover:translate-x-0.5" />
          )}
        </div>
      </div>
    </div>
  );
}

interface CostDistributionBarProps {
  bottlenecks: BottleneckNode[];
}

function CostDistributionBar({ bottlenecks }: CostDistributionBarProps) {
  const totalPercentage = bottlenecks.reduce(
    (sum, b) => sum + b.contribution.percentage,
    0
  );
  const otherPercentage = Math.max(0, 100 - totalPercentage);

  return (
    <div className="flex h-4 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
      {bottlenecks.map((bottleneck) => {
        const config = severityConfig[bottleneck.severity];
        return (
          <div
            key={bottleneck.node.id}
            className={cn(config.barColor, 'transition-all')}
            style={{ width: `${Math.min(bottleneck.contribution.percentage, 100)}%` }}
            title={`${bottleneck.node.nodeType}: ${bottleneck.contribution.percentage.toFixed(1)}%`}
          />
        );
      })}
      {otherPercentage > 0 && (
        <div
          className="bg-gray-400 dark:bg-gray-500"
          style={{ width: `${otherPercentage}%` }}
          title={`기타: ${otherPercentage.toFixed(1)}%`}
        />
      )}
    </div>
  );
}

interface CostDistributionLegendProps {
  bottlenecks: BottleneckNode[];
}

function CostDistributionLegend({ bottlenecks }: CostDistributionLegendProps) {
  const totalPercentage = bottlenecks.reduce(
    (sum, b) => sum + b.contribution.percentage,
    0
  );
  const otherPercentage = Math.max(0, 100 - totalPercentage);

  return (
    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
      {bottlenecks.map((bottleneck) => {
        const config = severityConfig[bottleneck.severity];
        return (
          <div key={bottleneck.node.id} className="flex items-center gap-1">
            <div className={cn('h-2 w-2 rounded-full', config.barColor)} />
            <span>
              {bottleneck.node.nodeType}
              {bottleneck.node.relationName && ` (${bottleneck.node.relationName})`}
            </span>
          </div>
        );
      })}
      {otherPercentage > 0 && (
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-gray-400 dark:bg-gray-500" />
          <span>기타 ({otherPercentage.toFixed(1)}%)</span>
        </div>
      )}
    </div>
  );
}
