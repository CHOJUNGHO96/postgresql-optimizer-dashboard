import { useState, useCallback } from 'react';
import { Play, Trash2, Info, FileText, Code, Database } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/common';
import { SqlEditor } from './SqlEditor';
import { useAnalyzeQuery, useAnalyzePlan } from '@/hooks';
import type { QueryPlanResponse } from '@/types';

interface QueryAnalyzerProps {
  onAnalysisComplete?: (result: QueryPlanResponse) => void;
}

type TabType = 'query' | 'plan';

export function QueryAnalyzer({ onAnalysisComplete }: QueryAnalyzerProps) {
  const [activeTab, setActiveTab] = useState<TabType>('query');

  // Query tab state
  const [query, setQuery] = useState('');
  const [title, setTitle] = useState('');

  // Plan tab state
  const [planJson, setPlanJson] = useState('');
  const [planTitle, setPlanTitle] = useState('');
  const [originalQuery, setOriginalQuery] = useState('');

  const { mutate: analyzeQuery, isPending: isQueryPending } = useAnalyzeQuery();
  const { mutate: analyzePlan, isPending: isPlanPending } = useAnalyzePlan();

  const isPending = activeTab === 'query' ? isQueryPending : isPlanPending;

  const handleAnalyzeQuery = useCallback(() => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      toast.error('쿼리를 입력해주세요.');
      return;
    }

    const trimmedTitle = title.trim();
    analyzeQuery(
      { query: trimmedQuery, ...(trimmedTitle && { title: trimmedTitle }) },
      {
        onSuccess: (result) => {
          toast.success('쿼리 분석이 완료되었습니다.');
          onAnalysisComplete?.(result);
        },
        onError: (error) => {
          toast.error(error.detail || '쿼리 분석 중 오류가 발생했습니다.');
        },
      }
    );
  }, [query, title, analyzeQuery, onAnalysisComplete]);

  const handleAnalyzePlan = useCallback(() => {
    const trimmedPlanJson = planJson.trim();
    if (!trimmedPlanJson) {
      toast.error('EXPLAIN JSON을 입력해주세요.');
      return;
    }

    // Parse JSON
    let parsedPlan: Record<string, unknown> | Record<string, unknown>[];
    try {
      parsedPlan = JSON.parse(trimmedPlanJson);
    } catch {
      toast.error('유효한 JSON 형식이 아닙니다.');
      return;
    }

    // Validate structure
    const planData = Array.isArray(parsedPlan) ? parsedPlan[0] : parsedPlan;
    if (!planData || typeof planData !== 'object' || !('Plan' in planData)) {
      toast.error('EXPLAIN JSON 형식이 올바르지 않습니다. "Plan" 키가 필요합니다.');
      return;
    }

    const trimmedTitle = planTitle.trim();
    const trimmedOriginalQuery = originalQuery.trim();

    analyzePlan(
      {
        plan_json: parsedPlan,
        ...(trimmedTitle && { title: trimmedTitle }),
        ...(trimmedOriginalQuery && { original_query: trimmedOriginalQuery }),
      },
      {
        onSuccess: (result) => {
          toast.success('Plan 분석이 완료되었습니다.');
          onAnalysisComplete?.(result);
        },
        onError: (error) => {
          toast.error(error.detail || 'Plan 분석 중 오류가 발생했습니다.');
        },
      }
    );
  }, [planJson, planTitle, originalQuery, analyzePlan, onAnalysisComplete]);

  const handleAnalyze = activeTab === 'query' ? handleAnalyzeQuery : handleAnalyzePlan;

  const handleClear = useCallback(() => {
    if (activeTab === 'query') {
      setQuery('');
      setTitle('');
    } else {
      setPlanJson('');
      setPlanTitle('');
      setOriginalQuery('');
    }
  }, [activeTab]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Ctrl/Cmd + Enter to analyze
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleAnalyze();
      }
    },
    [handleAnalyze]
  );

  const isAnalyzeDisabled = activeTab === 'query' ? !query.trim() : !planJson.trim();

  return (
    <Card className="animate-fade-in" onKeyDown={handleKeyDown}>
      <CardHeader>
        <CardTitle>SQL 쿼리 분석</CardTitle>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            disabled={isAnalyzeDisabled || isPending}
            leftIcon={<Trash2 className="h-4 w-4" />}
          >
            초기화
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleAnalyze}
            isLoading={isPending}
            leftIcon={<Play className="h-4 w-4" />}
            disabled={isAnalyzeDisabled}
          >
            분석 실행
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Tab Navigation */}
        <div className="mb-4 flex border-b border-gray-200 dark:border-gray-700">
          <button
            type="button"
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'query'
                ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('query')}
          >
            <Database className="h-4 w-4" />
            쿼리 분석
          </button>
          <button
            type="button"
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'plan'
                ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('plan')}
          >
            <Code className="h-4 w-4" />
            Plan JSON 분석
          </button>
        </div>

        {/* Query Tab Content */}
        {activeTab === 'query' && (
          <>
            <div className="mb-3 flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              <Info className="h-4 w-4 flex-shrink-0" />
              <span>
                <strong>SELECT</strong> 쿼리만 분석 가능합니다. INSERT, UPDATE, DELETE 등 데이터 변경 쿼리는 지원되지 않습니다.
              </span>
            </div>
            <div className="mb-3">
              <label htmlFor="query-title" className="mb-1 flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                <FileText className="h-4 w-4" />
                제목 (선택사항)
              </label>
              <input
                id="query-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="쿼리를 구분할 수 있는 제목을 입력하세요"
                maxLength={255}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>
            <SqlEditor
              value={query}
              onChange={setQuery}
              minHeight="200px"
              maxHeight="400px"
            />
          </>
        )}

        {/* Plan JSON Tab Content */}
        {activeTab === 'plan' && (
          <>
            <div className="mb-3 flex items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
              <Info className="h-4 w-4 flex-shrink-0" />
              <span>
                <strong>EXPLAIN (ANALYZE, FORMAT JSON)</strong> 결과를 직접 붙여넣어 분석할 수 있습니다.
              </span>
            </div>
            <div className="mb-3">
              <label htmlFor="plan-title" className="mb-1 flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                <FileText className="h-4 w-4" />
                제목 (선택사항)
              </label>
              <input
                id="plan-title"
                type="text"
                value={planTitle}
                onChange={(e) => setPlanTitle(e.target.value)}
                placeholder="분석 결과를 구분할 수 있는 제목을 입력하세요"
                maxLength={255}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>
            <div className="mb-3">
              <label htmlFor="original-query" className="mb-1 flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                <Database className="h-4 w-4" />
                원본 쿼리 (선택사항)
              </label>
              <textarea
                id="original-query"
                value={originalQuery}
                onChange={(e) => setOriginalQuery(e.target.value)}
                placeholder="원본 SQL 쿼리를 입력하세요 (선택사항)"
                rows={3}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>
            <div>
              <label htmlFor="plan-json" className="mb-1 flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                <Code className="h-4 w-4" />
                EXPLAIN JSON
              </label>
              <textarea
                id="plan-json"
                value={planJson}
                onChange={(e) => setPlanJson(e.target.value)}
                placeholder={`EXPLAIN (ANALYZE, FORMAT JSON) 결과를 붙여넣으세요.

예시:
[
  {
    "Plan": {
      "Node Type": "Seq Scan",
      "Relation Name": "users",
      "Startup Cost": 0.00,
      "Total Cost": 10.00,
      "Plan Rows": 100,
      "Plan Width": 32
    },
    "Execution Time": 0.123
  }
]`}
                rows={12}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>
          </>
        )}

        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          단축키: <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">Ctrl</kbd> + <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">Enter</kbd> 로 분석 실행
        </p>
      </CardContent>
    </Card>
  );
}
