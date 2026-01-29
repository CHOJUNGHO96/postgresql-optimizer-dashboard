import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/layout';
import { QueryAnalyzer } from '@/components/query';
import { AnalysisResult } from '@/components/analysis';
import { Button } from '@/components/common';
import { History } from 'lucide-react';
import type { QueryPlanResponse } from '@/types';

export function Dashboard() {
  const navigate = useNavigate();
  const [analysisResult, setAnalysisResult] = useState<QueryPlanResponse | null>(null);

  const handleAnalysisComplete = useCallback((result: QueryPlanResponse) => {
    setAnalysisResult(result);
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="쿼리 분석"
        description="PostgreSQL 쿼리를 입력하고 실행 계획을 분석하세요."
        action={
          <Button
            variant="outline"
            onClick={() => navigate('/history')}
            leftIcon={<History className="h-4 w-4" />}
          >
            분석 히스토리
          </Button>
        }
      />

      <QueryAnalyzer onAnalysisComplete={handleAnalysisComplete} />

      {analysisResult && (
        <div className="animate-slide-in">
          <AnalysisResult result={analysisResult} showQuery={false} />
        </div>
      )}
    </div>
  );
}
