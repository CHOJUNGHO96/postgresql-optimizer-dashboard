import {
  TrendingUp,
  Timer,
  Rows3,
  Ruler,
} from 'lucide-react';
import { Card } from '@/components/common';
import { formatCost, formatNumber, cn } from '@/lib/utils';
import type { CostEstimate } from '@/types';

interface CostCardProps {
  costEstimate: CostEstimate;
  className?: string;
}

interface MetricItemProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  highlight?: boolean;
}

function MetricItem({ label, value, icon, description, highlight }: MetricItemProps) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 rounded-lg border p-4 transition-all',
        highlight
          ? 'border-pg-500/30 bg-pg-500/5 dark:border-pg-400/30 dark:bg-pg-400/5'
          : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800'
      )}
    >
      <div
        className={cn(
          'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg',
          highlight
            ? 'bg-pg-500/10 text-pg-500 dark:bg-pg-400/10 dark:text-pg-400'
            : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
        )}
      >
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
          {label}
        </p>
        <p className="mt-1 truncate text-xl font-bold text-gray-900 dark:text-white">
          {value}
        </p>
        {description && (
          <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
            {description}
          </p>
        )}
      </div>
    </div>
  );
}

export function CostCard({ costEstimate, className }: CostCardProps) {
  const { startup_cost, total_cost, plan_rows, plan_width } = costEstimate;

  return (
    <Card className={cn('animate-fade-in', className)} padding="lg">
      <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
        비용 추정치
      </h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricItem
          label="시작 비용"
          value={formatCost(startup_cost)}
          icon={<Timer className="h-5 w-5" />}
          description="첫 번째 행 반환까지의 비용"
        />
        <MetricItem
          label="총 비용"
          value={formatCost(total_cost)}
          icon={<TrendingUp className="h-5 w-5" />}
          description="전체 쿼리 실행 비용"
          highlight
        />
        <MetricItem
          label="예상 행 수"
          value={formatNumber(plan_rows, 0)}
          icon={<Rows3 className="h-5 w-5" />}
          description="반환될 것으로 예상되는 행 수"
        />
        <MetricItem
          label="행 너비"
          value={`${formatNumber(plan_width, 0)} bytes`}
          icon={<Ruler className="h-5 w-5" />}
          description="각 행의 평균 바이트 크기"
        />
      </div>
    </Card>
  );
}
