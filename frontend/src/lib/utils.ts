import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { NodeTypeInfo, PlanNodeType, NodeTypeCategory } from '@/types';

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format number with locale
 */
export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat('ko-KR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format cost value
 */
export function formatCost(cost: number): string {
  if (cost >= 1_000_000) {
    return `${formatNumber(cost / 1_000_000, 2)}M`;
  }
  if (cost >= 1_000) {
    return `${formatNumber(cost / 1_000, 2)}K`;
  }
  return formatNumber(cost, 2);
}

/**
 * Format execution time
 */
export function formatExecutionTime(ms: number | null): string {
  if (ms === null) return '-';
  if (ms < 1) return `${formatNumber(ms * 1000, 2)} us`;
  if (ms < 1000) return `${formatNumber(ms, 2)} ms`;
  return `${formatNumber(ms / 1000, 2)} s`;
}

/**
 * Format date
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Format relative time
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return '방금 전';
  if (diffMin < 60) return `${diffMin}분 전`;
  if (diffHour < 24) return `${diffHour}시간 전`;
  if (diffDay < 7) return `${diffDay}일 전`;
  return formatDate(dateString);
}

/**
 * Get node type category
 */
export function getNodeTypeCategory(nodeType: PlanNodeType): NodeTypeCategory {
  if (nodeType.includes('Scan')) return 'scan';
  if (nodeType.includes('Join') || nodeType === 'Nested Loop') return 'join';
  if (nodeType.includes('Aggregate') || nodeType === 'Hash') return 'aggregate';
  if (nodeType === 'Sort' || nodeType === 'Materialize') return 'sort';
  return 'other';
}

/**
 * Get node type info for styling
 */
export function getNodeTypeInfo(nodeType: PlanNodeType): NodeTypeInfo {
  const category = getNodeTypeCategory(nodeType);

  const categoryInfo: Record<NodeTypeCategory, Omit<NodeTypeInfo, 'label'>> = {
    scan: {
      category: 'scan',
      description: '테이블 스캔 작업',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10 border-blue-500/30',
    },
    join: {
      category: 'join',
      description: '조인 작업',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10 border-purple-500/30',
    },
    aggregate: {
      category: 'aggregate',
      description: '집계 작업',
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10 border-orange-500/30',
    },
    sort: {
      category: 'sort',
      description: '정렬 작업',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10 border-green-500/30',
    },
    other: {
      category: 'other',
      description: '기타 작업',
      color: 'text-gray-400',
      bgColor: 'bg-gray-500/10 border-gray-500/30',
    },
  };

  const descriptions: Record<string, string> = {
    'Seq Scan': '전체 테이블 순차 스캔',
    'Index Scan': '인덱스를 사용한 스캔',
    'Index Only Scan': '인덱스만으로 데이터 조회',
    'Bitmap Index Scan': '비트맵 인덱스 스캔',
    'Bitmap Heap Scan': '비트맵 힙 스캔',
    'Nested Loop': '중첩 루프 조인',
    'Hash Join': '해시 조인',
    'Merge Join': '병합 조인',
    'Sort': '정렬 작업',
    'Hash': '해시 테이블 생성',
    'Aggregate': '집계 연산',
    'Group Aggregate': '그룹별 집계',
    'HashAggregate': '해시 기반 집계',
    'Limit': '결과 제한',
    'Append': '결과 연결',
    'Materialize': '중간 결과 저장',
    'Subquery Scan': '서브쿼리 스캔',
    'CTE Scan': 'CTE 스캔',
    'Result': '결과 반환',
    'Gather': '병렬 워커 결과 수집',
    'Gather Merge': '병렬 워커 정렬 병합',
    'Other': '기타 작업',
  };

  return {
    ...categoryInfo[category],
    label: nodeType,
    description: descriptions[nodeType] || categoryInfo[category].description,
  };
}

/**
 * Truncate string with ellipsis
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}

/**
 * Get cost severity level
 */
export function getCostSeverity(totalCost: number): 'low' | 'medium' | 'high' | 'critical' {
  if (totalCost < 100) return 'low';
  if (totalCost < 1000) return 'medium';
  if (totalCost < 10000) return 'high';
  return 'critical';
}

/**
 * Get cost severity styles
 */
export function getCostSeverityStyles(severity: 'low' | 'medium' | 'high' | 'critical') {
  const styles = {
    low: {
      color: 'text-green-400',
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      label: '낮음',
    },
    medium: {
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      label: '보통',
    },
    high: {
      color: 'text-orange-400',
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/30',
      label: '높음',
    },
    critical: {
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      label: '심각',
    },
  };
  return styles[severity];
}
