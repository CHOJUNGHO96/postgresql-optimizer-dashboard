import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/common';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <div className="mb-8">
        <h1 className="text-9xl font-bold text-gray-200 dark:text-gray-800">404</h1>
        <h2 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
          페이지를 찾을 수 없습니다
        </h2>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          요청하신 페이지가 존재하지 않거나 이동되었습니다.
        </p>
      </div>
      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={() => navigate(-1)}
          leftIcon={<ArrowLeft className="h-4 w-4" />}
        >
          뒤로 가기
        </Button>
        <Button
          variant="primary"
          onClick={() => navigate('/')}
          leftIcon={<Home className="h-4 w-4" />}
        >
          홈으로 이동
        </Button>
      </div>
    </div>
  );
}
