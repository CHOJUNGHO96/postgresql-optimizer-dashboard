import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { PageHeader } from '@/components/layout';
import { AnalysisResult } from '@/components/analysis';
import { Button, LoadingPage, ErrorMessage } from '@/components/common';
import { useQueryPlan } from '@/hooks';

export function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, error, refetch } = useQueryPlan(id || '');

  if (isLoading) {
    return <LoadingPage message="분석 결과를 불러오는 중..." />;
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="분석 결과"
          action={
            <Button
              variant="outline"
              onClick={() => navigate('/history')}
              leftIcon={<ArrowLeft className="h-4 w-4" />}
            >
              히스토리로 돌아가기
            </Button>
          }
        />
        <ErrorMessage
          title="분석 결과를 찾을 수 없습니다"
          message={error?.detail || '요청한 분석 결과가 존재하지 않거나 삭제되었습니다.'}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="분석 결과 상세"
        description={`ID: ${data.id}`}
        action={
          <Button
            variant="outline"
            onClick={() => navigate('/history')}
            leftIcon={<ArrowLeft className="h-4 w-4" />}
          >
            히스토리로 돌아가기
          </Button>
        }
      />

      <AnalysisResult result={data} showQuery />
    </div>
  );
}
