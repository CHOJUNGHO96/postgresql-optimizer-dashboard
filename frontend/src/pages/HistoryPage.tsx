import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/layout';
import { HistoryTable } from '@/components/analysis';
import { Button, Card } from '@/components/common';
import { Plus, Search, X } from 'lucide-react';
import { useQueryPlanList } from '@/hooks';
import { useDebounce } from '@/hooks/useDebounce';

const PAGE_SIZE = 10;

export function HistoryPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounce(searchInput, 300);

  const { data, isLoading, error, refetch } = useQueryPlanList({
    limit: PAGE_SIZE,
    offset: (page - 1) * PAGE_SIZE,
    ...(debouncedSearch && { title_search: debouncedSearch }),
  });

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    setPage(1);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setPage(1);
  };

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

      {/* Search Bar */}
      <Card padding="sm">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            placeholder="제목으로 검색..."
            className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-10 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
          />
          {searchInput && (
            <button
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        {debouncedSearch && (
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            "{debouncedSearch}" 검색 결과
          </p>
        )}
      </Card>

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
