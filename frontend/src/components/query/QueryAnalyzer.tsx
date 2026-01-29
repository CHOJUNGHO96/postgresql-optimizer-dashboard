import { useState, useCallback } from 'react';
import { Play, Trash2, Info, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/common';
import { SqlEditor } from './SqlEditor';
import { useAnalyzeQuery } from '@/hooks';
import type { QueryPlanResponse } from '@/types';

interface QueryAnalyzerProps {
  onAnalysisComplete?: (result: QueryPlanResponse) => void;
}

export function QueryAnalyzer({ onAnalysisComplete }: QueryAnalyzerProps) {
  const [query, setQuery] = useState('');
  const [title, setTitle] = useState('');
  const { mutate: analyze, isPending } = useAnalyzeQuery();

  const handleAnalyze = useCallback(() => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      toast.error('쿼리를 입력해주세요.');
      return;
    }

    const trimmedTitle = title.trim();
    analyze(
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
  }, [query, title, analyze, onAnalysisComplete]);

  const handleClear = useCallback(() => {
    setQuery('');
    setTitle('');
  }, []);

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

  return (
    <Card className="animate-fade-in" onKeyDown={handleKeyDown}>
      <CardHeader>
        <CardTitle>SQL 쿼리 입력</CardTitle>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            disabled={!query || isPending}
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
            disabled={!query.trim()}
          >
            분석 실행
          </Button>
        </div>
      </CardHeader>
      <CardContent>
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
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          단축키: <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">Ctrl</kbd> + <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">Enter</kbd> 로 분석 실행
        </p>
      </CardContent>
    </Card>
  );
}
