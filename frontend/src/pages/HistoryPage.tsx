import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/layout';
import { HistoryTable } from '@/components/analysis';
import { Button } from '@/components/common';
import { Plus } from 'lucide-react';
import { useQueryPlanList } from '@/hooks';

const PAGE_SIZE = 10;

export function HistoryPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);

  const { data, isLoading, error, refetch } = useQueryPlanList({
    limit: PAGE_SIZE,
    offset: (page - 1) * PAGE_SIZE,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="분석 히스토리"
        description="이전에 분석한 쿼리들의 기록을 확인하세요."
        action={
          <Button
            variant="primary"
            onClick={() => navigate('/')}
            leftIcon={<Plus className="h-4 w-4" />}
          >
            새 쿼리 분석
          </Button>
        }
      />

      <HistoryTable
        data={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        isLoading={isLoading}
        error={error?.detail}
        onRetry={() => refetch()}
      />
    </div>
  );
}
