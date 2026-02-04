import { useMemo } from 'react';
import { Timer, Clock, TrendingUp, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/common';
import { TooltipBadge } from './TooltipBadge';
import { cn } from '@/lib/utils';
import { calculateEstimateAccuracy } from '@/lib/planAnalysis';
import type { AnalyzeMetrics, FlattenedNode, EstimateAccuracy } from '@/types';

interface AnalyzeMetricsCardProps {
  analyzeMetrics: AnalyzeMetrics;
  flattenedNodes: FlattenedNode[];
  className?: string;
}

// 시간 포맷팅
function formatTime(ms: number): string {
  if (ms < 1) {
    return `${(ms * 1000).toFixed(1)} µs`;
  }
  if (ms < 1000) {
    return `${ms.toFixed(2)} ms`;
  }
  return `${(ms / 1000).toFixed(2)} s`;
}

// 정확도 포맷팅 (퍼센트)
function formatAccuracy(accuracy: number): string {
  const percent = accuracy * 100;
  if (percent >= 1000) {
    return `${(percent / 100).toFixed(0)}x`;
  }
  return `${percent.toFixed(0)}%`;
}

// 정확도 레벨에 따른 스타일
function getAccuracySeverityStyle(severity: EstimateAccuracy['severity']) {
  switch (severity) {
    case 'accurate':
      return {
        bg: 'bg-green-50 dark:bg-green-900/20',
        text: 'text-green-700 dark:text-green-400',
        icon: <CheckCircle2 className="h-4 w-4" />,
      };
    case 'underestimate':
      return {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        text: 'text-yellow-700 dark:text-yellow-400',
        icon: <AlertTriangle className="h-4 w-4" />,
      };
    case 'overestimate':
      return {
        bg: 'bg-orange-50 dark:bg-orange-900/20',
        text: 'text-orange-700 dark:text-orange-400',
        icon: <AlertTriangle className="h-4 w-4" />,
      };
    case 'severe':
      return {
        bg: 'bg-red-50 dark:bg-red-900/20',
        text: 'text-red-700 dark:text-red-400',
        icon: <XCircle className="h-4 w-4" />,
      };
  }
}

// 평균 정확도 계산
function calculateAverageAccuracy(accuracies: EstimateAccuracy[]): number {
  if (accuracies.length === 0) return 100;

  // 정확도 점수 계산: 1.0에 가까울수록 좋음
  const scores = accuracies.map((a) => {
    if (a.accuracy >= 0.5 && a.accuracy <= 2) {
      return 100; // 정확
    }
    if (a.accuracy > 2) {
      return Math.max(0, 100 - (a.accuracy - 1) * 10); // 과소추정
    }
    return Math.max(0, 100 - (1 / a.accuracy - 1) * 10); // 과대추정
  });

  return scores.reduce((sum, s) => sum + s, 0) / scores.length;
}

// 시간 분포 바 컴포넌트
function TimeDistributionBar({
  nodeType,
  percentage,
  actualTime,
}: {
  nodeType: string;
  percentage: number;
  actualTime: number;
}) {
  const barWidth = Math.max(percentage, 2); // 최소 2%로 표시

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1">
        <div className="mb-1 flex items-center justify-between text-xs">
          <span className="font-medium text-gray-700 dark:text-gray-300">{nodeType}</span>
          <span className="text-gray-500 dark:text-gray-400">
            {formatTime(actualTime)} ({percentage.toFixed(1)}%)
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className={cn(
              'h-full rounded-full transition-all',
              percentage >= 50
                ? 'bg-red-500'
                : percentage >= 30
                ? 'bg-orange-500'
                : percentage >= 15
                ? 'bg-yellow-500'
                : 'bg-blue-500'
            )}
            style={{ width: `${barWidth}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export function AnalyzeMetricsCard({
  analyzeMetrics,
  flattenedNodes,
  className,
}: AnalyzeMetricsCardProps) {
  const { executionTime, planningTime, nodeTimings } = analyzeMetrics;

  // 추정 정확도 분석
  const estimateAccuracies = useMemo(
    () => calculateEstimateAccuracy(flattenedNodes),
    [flattenedNodes]
  );

  // 평균 정확도
  const averageAccuracy = useMemo(
    () => calculateAverageAccuracy(estimateAccuracies),
    [estimateAccuracies]
  );

  // 상위 5개 시간 분포
  const topNodeTimings = nodeTimings.slice(0, 5);

  // 정확도 요약
  const accuracySummary = useMemo(() => {
    const summary = {
      accurate: 0,
      underestimate: 0,
      overestimate: 0,
      severe: 0,
    };
    for (const acc of estimateAccuracies) {
      summary[acc.severity]++;
    }
    return summary;
  }, [estimateAccuracies]);

  return (
    <Card padding="lg" className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-500" />
          실행 분석 (ANALYZE)
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* 요약 메트릭 카드 */}
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {/* 실행 시간 */}
          <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
              <Timer className="h-4 w-4" />
              <span className="text-sm font-medium">실행 시간</span>
            </div>
            <div className="mt-2 text-2xl font-bold text-blue-700 dark:text-blue-300">
              {formatTime(executionTime)}
            </div>
          </div>

          {/* 계획 시간 */}
          <div className="rounded-lg bg-purple-50 p-4 dark:bg-purple-900/20">
            <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400">
              <Clock className="h-4 w-4" />
              <span className="text-sm font-medium">계획 시간</span>
            </div>
            <div className="mt-2 text-2xl font-bold text-purple-700 dark:text-purple-300">
              {formatTime(planningTime)}
            </div>
          </div>

          {/* 추정 정확도 */}
          <div
            className={cn(
              'rounded-lg p-4',
              averageAccuracy >= 80
                ? 'bg-green-50 dark:bg-green-900/20'
                : averageAccuracy >= 50
                ? 'bg-yellow-50 dark:bg-yellow-900/20'
                : 'bg-red-50 dark:bg-red-900/20'
            )}
          >
            <div
              className={cn(
                'flex items-center gap-2',
                averageAccuracy >= 80
                  ? 'text-green-600 dark:text-green-400'
                  : averageAccuracy >= 50
                  ? 'text-yellow-600 dark:text-yellow-400'
                  : 'text-red-600 dark:text-red-400'
              )}
            >
              {averageAccuracy >= 80 ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <AlertTriangle className="h-4 w-4" />
              )}
              <span className="text-sm font-medium">추정 정확도</span>
            </div>
            <div
              className={cn(
                'mt-2 text-2xl font-bold',
                averageAccuracy >= 80
                  ? 'text-green-700 dark:text-green-300'
                  : averageAccuracy >= 50
                  ? 'text-yellow-700 dark:text-yellow-300'
                  : 'text-red-700 dark:text-red-300'
              )}
            >
              {averageAccuracy.toFixed(0)}%
            </div>
          </div>
        </div>

        {/* 노드별 실행 시간 분포 */}
        {topNodeTimings.length > 0 && (
          <div className="mb-6">
            <h4 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
              노드별 실행 시간 분포
            </h4>
            <div className="space-y-3">
              {topNodeTimings.map((timing) => (
                <TimeDistributionBar
                  key={timing.nodeId}
                  nodeType={timing.nodeType}
                  percentage={timing.timePercentage}
                  actualTime={timing.actualTime}
                />
              ))}
            </div>
          </div>
        )}

        {/* 추정 정확도 요약 */}
        {estimateAccuracies.length > 0 && (
          <div className="mb-6">
            <h4 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
              추정 정확도 요약
            </h4>
            <div className="flex flex-wrap gap-2">
              {accuracySummary.accurate > 0 && (
                <TooltipBadge variant="success" tooltip="예상 행 수와 실제 행 수가 유사함">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>정확 {accuracySummary.accurate}개</span>
                </TooltipBadge>
              )}
              {accuracySummary.underestimate > 0 && (
                <TooltipBadge
                  variant="warning"
                  tooltip="실제 행 수가 예상보다 많음 (과소추정)"
                >
                  <AlertTriangle className="h-3 w-3" />
                  <span>과소추정 {accuracySummary.underestimate}개</span>
                </TooltipBadge>
              )}
              {accuracySummary.overestimate > 0 && (
                <TooltipBadge
                  variant="warning"
                  tooltip="실제 행 수가 예상보다 적음 (과대추정)"
                >
                  <AlertTriangle className="h-3 w-3" />
                  <span>과대추정 {accuracySummary.overestimate}개</span>
                </TooltipBadge>
              )}
              {accuracySummary.severe > 0 && (
                <TooltipBadge variant="danger" tooltip="예상과 실제 차이가 매우 큼 (10배 이상)">
                  <XCircle className="h-3 w-3" />
                  <span>심각한 오차 {accuracySummary.severe}개</span>
                </TooltipBadge>
              )}
            </div>
          </div>
        )}

        {/* 추정 정확도 상세 테이블 */}
        {estimateAccuracies.length > 0 && (
          <div>
            <h4 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
              추정 정확도 분석
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="pb-2 text-left font-medium text-gray-500 dark:text-gray-400">
                      노드
                    </th>
                    <th className="pb-2 text-right font-medium text-gray-500 dark:text-gray-400">
                      예상 행
                    </th>
                    <th className="pb-2 text-right font-medium text-gray-500 dark:text-gray-400">
                      실제 행
                    </th>
                    <th className="pb-2 text-right font-medium text-gray-500 dark:text-gray-400">
                      정확도
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {estimateAccuracies.slice(0, 10).map((acc) => {
                    const style = getAccuracySeverityStyle(acc.severity);
                    return (
                      <tr
                        key={acc.nodeId}
                        className="border-b border-gray-100 last:border-0 dark:border-gray-800"
                      >
                        <td className="py-2 font-medium text-gray-700 dark:text-gray-300">
                          {acc.nodeType}
                        </td>
                        <td className="py-2 text-right text-gray-600 dark:text-gray-400">
                          {acc.estimatedRows.toLocaleString()}
                        </td>
                        <td className="py-2 text-right text-gray-600 dark:text-gray-400">
                          {acc.actualRows.toLocaleString()}
                        </td>
                        <td className="py-2 text-right">
                          <Badge
                            variant={
                              acc.severity === 'accurate'
                                ? 'success'
                                : acc.severity === 'severe'
                                ? 'danger'
                                : 'warning'
                            }
                            size="sm"
                          >
                            <span className="flex items-center gap-1">
                              {style.icon}
                              {formatAccuracy(acc.accuracy)}
                            </span>
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
