import { useState } from 'react';
import { Sparkles, Loader2, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Button } from '@/components/common';
import { useOptimizeQuery } from '@/hooks/useQueryOptimization';
import { ModelSelector } from './ModelSelector';
import type { AIModel, OptimizedQueryResponse } from '@/types/optimization';

interface OptimizeButtonProps {
  planId: string;
  onOptimizationComplete?: (optimization: OptimizedQueryResponse) => void;
}

export function OptimizeButton({ planId, onOptimizationComplete }: OptimizeButtonProps) {
  const [open, setOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState<AIModel>('claude-3-5-sonnet-20241022');
  const [validateOptimization, setValidateOptimization] = useState(false);
  const [includeSchemaContext, setIncludeSchemaContext] = useState(false);

  const { mutate: optimize, isPending } = useOptimizeQuery(planId);

  const handleOptimize = () => {
    optimize(
      {
        ai_model: selectedModel,
        validate_optimization: validateOptimization,
        include_schema_context: includeSchemaContext,
      },
      {
        onSuccess: (data) => {
          toast.success(
            `쿼리가 성공적으로 최적화되었습니다\nAI 신뢰도: ${(data.confidence_score * 100).toFixed(0)}%`
          );
          setOpen(false);
          onOptimizationComplete?.(data);
        },
        onError: (error: Error) => {
          toast.error(`최적화 실패: ${error.message}`);
        },
      }
    );
  };

  return (
    <>
      <Button variant="primary" onClick={() => setOpen(true)}>
        <Sparkles className="h-4 w-4 mr-2" />
        AI 최적화
      </Button>

      {open && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  AI 쿼리 최적화
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  AI를 활용하여 SQL 쿼리를 분석하고 최적화합니다
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <ModelSelector
                value={selectedModel}
                onChange={setSelectedModel}
                disabled={isPending}
              />

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="validate"
                    checked={validateOptimization}
                    onChange={(e) => setValidateOptimization(e.target.checked)}
                    disabled={isPending}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <label
                    htmlFor="validate"
                    className="text-sm font-normal cursor-pointer text-gray-700 dark:text-gray-300"
                  >
                    최적화 검증 (EXPLAIN ANALYZE 실행)
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="schema"
                    checked={includeSchemaContext}
                    onChange={(e) => setIncludeSchemaContext(e.target.checked)}
                    disabled={isPending}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <label
                    htmlFor="schema"
                    className="text-sm font-normal cursor-pointer text-gray-700 dark:text-gray-300"
                  >
                    스키마 정보 포함
                  </label>
                </div>
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  variant="secondary"
                  onClick={() => setOpen(false)}
                  disabled={isPending}
                  className="flex-1"
                >
                  취소
                </Button>
                <Button
                  variant="primary"
                  onClick={handleOptimize}
                  disabled={isPending}
                  className="flex-1"
                >
                  {isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      최적화 중...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      쿼리 최적화
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
