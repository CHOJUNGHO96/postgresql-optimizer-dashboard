import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/common';
import { OptimizationResult } from './OptimizationResult';
import { Sparkles, ChevronRight } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { OptimizedQueryResponse } from '@/types/optimization';

interface OptimizationHistoryProps {
  optimizations: OptimizedQueryResponse[];
  originalQuery: string;
  isLoading?: boolean;
  className?: string;
}

interface GroupedOptimizations {
  [aiModel: string]: OptimizedQueryResponse;
}

export function OptimizationHistory({
  optimizations,
  originalQuery,
  isLoading = false,
  className,
}: OptimizationHistoryProps) {
  const [selectedOptimization, setSelectedOptimization] =
    useState<OptimizedQueryResponse | null>(null);

  // AI 모델별 가장 최근 최적화만 추출
  const groupedByModel: GroupedOptimizations = optimizations.reduce((acc, opt) => {
    const modelKey = opt.ai_model;

    // 이미 있는 모델이면 created_at 비교해서 최신 것만 유지
    if (!acc[modelKey] ||
        new Date(opt.created_at) > new Date(acc[modelKey].created_at)) {
      acc[modelKey] = opt;
    }

    return acc;
  }, {} as GroupedOptimizations);

  const latestOptimizations = Object.values(groupedByModel);

  // 로딩 중일 때 Skeleton 표시
  if (isLoading) {
    return (
      <Card padding="lg" className={className}>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <CardTitle>AI 최적화 이력</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // 최적화 결과가 없으면 빈 상태 표시
  if (latestOptimizations.length === 0) {
    return (
      <Card padding="lg" className={className}>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <CardTitle>AI 최적화 이력</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Sparkles className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              아직 AI 최적화를 실행하지 않았습니다
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              상단의 "AI 최적화" 버튼을 클릭하여 쿼리를 최적화해보세요
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // AI 모델명 표시용 변환
  const getModelDisplayName = (model: string): string => {
    if (model.includes('claude')) return 'Claude';
    if (model.includes('gemini')) return 'Gemini';
    if (model.includes('glm')) return 'GLM';
    return model;
  };

  // 모델별 색상
  const getModelColor = (model: string): 'purple' | 'blue' | 'green' | 'gray' => {
    if (model.includes('claude')) return 'purple';
    if (model.includes('gemini')) return 'blue';
    if (model.includes('glm')) return 'green';
    return 'gray';
  };

  return (
    <div className={className}>
      {/* 최적화 이력 리스트 카드 */}
      <Card padding="lg">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <CardTitle>AI 최적화 이력</CardTitle>
            <Badge variant="secondary">{latestOptimizations.length}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {latestOptimizations.map((optimization) => {
              const modelName = getModelDisplayName(optimization.ai_model);
              const modelColor = getModelColor(optimization.ai_model);
              const isSelected = selectedOptimization?.id === optimization.id;

              return (
                <button
                  key={optimization.id}
                  onClick={() => setSelectedOptimization(
                    isSelected ? null : optimization
                  )}
                  className={`
                    w-full rounded-lg border p-4 text-left transition-all
                    ${modelColor === 'purple' ? 'hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20' : ''}
                    ${modelColor === 'blue' ? 'hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20' : ''}
                    ${modelColor === 'green' ? 'hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20' : ''}
                    ${modelColor === 'gray' ? 'hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-900/20' : ''}
                    ${isSelected && modelColor === 'purple'
                      ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                      : ''
                    }
                    ${isSelected && modelColor === 'blue'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : ''
                    }
                    ${isSelected && modelColor === 'green'
                      ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                      : ''
                    }
                    ${isSelected && modelColor === 'gray'
                      ? 'border-gray-500 bg-gray-50 dark:bg-gray-900/20'
                      : ''
                    }
                    ${!isSelected ? 'border-gray-200 dark:border-gray-700' : ''}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant={modelColor}>
                        {modelName}
                      </Badge>
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          최적화 완료
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(optimization.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          신뢰도
                        </p>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                          {Math.round(optimization.confidence_score * 100)}%
                        </p>
                      </div>
                      <ChevronRight
                        className={`h-5 w-5 transition-transform ${
                          isSelected ? 'rotate-90' : ''
                        }`}
                      />
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* 선택된 최적화 상세 표시 */}
      {selectedOptimization && (
        <OptimizationResult
          optimization={selectedOptimization}
          originalQuery={originalQuery}
          className="mt-4"
        />
      )}
    </div>
  );
}
