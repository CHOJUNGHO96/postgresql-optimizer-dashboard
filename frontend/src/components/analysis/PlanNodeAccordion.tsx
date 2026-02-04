import { useState, useCallback } from 'react';
import {
  ChevronRight,
  ChevronDown,
  Table2,
  Database,
  Filter,
  ArrowUpDown,
  Link2,
  Hash,
  Zap,
  AlertTriangle,
  CheckCircle2,
  Info,
  XCircle,
  Timer,
  BarChart3,
  RefreshCw,
} from 'lucide-react';
import { Badge } from '@/components/common';
import { TooltipBadge } from './TooltipBadge';
import { formatCost, cn, getNodeTypeCategory } from '@/lib/utils';
import type { NodeTypeCategory } from '@/types';

interface PlanNodeAccordionProps {
  planRaw: Record<string, unknown>;
  className?: string;
}

interface PlanNodeMetrics {
  nodeType: string;
  startupCost: number;
  totalCost: number;
  planRows: number;
  planWidth: number;
  relationName?: string;
  alias?: string;
  indexName?: string;
  indexCond?: string;
  filter?: string;
  sortKey?: string[];
  joinType?: string;
  hashCond?: string;
  mergeCond?: string;
  cteName?: string;
  subplanName?: string;
  parallelAware?: boolean;
  plans?: PlanNodeMetrics[];
  // ANALYZE 메트릭
  actualRows?: number;
  actualLoops?: number;
  actualStartupTime?: number;
  actualTotalTime?: number;
}

// Parse plan node from raw JSON
function parsePlanNode(plan: Record<string, unknown>): PlanNodeMetrics {
  const nodeType = (plan['Node Type'] as string) || 'Unknown';

  const result: PlanNodeMetrics = {
    nodeType,
    startupCost: (plan['Startup Cost'] as number) || 0,
    totalCost: (plan['Total Cost'] as number) || 0,
    planRows: (plan['Plan Rows'] as number) || 0,
    planWidth: (plan['Plan Width'] as number) || 0,
  };

  // Optional fields
  if (plan['Relation Name']) result.relationName = plan['Relation Name'] as string;
  if (plan['Alias']) result.alias = plan['Alias'] as string;
  if (plan['Index Name']) result.indexName = plan['Index Name'] as string;
  if (plan['Index Cond']) result.indexCond = plan['Index Cond'] as string;
  if (plan['Filter']) result.filter = plan['Filter'] as string;
  if (plan['Sort Key']) result.sortKey = plan['Sort Key'] as string[];
  if (plan['Join Type']) result.joinType = plan['Join Type'] as string;
  if (plan['Hash Cond']) result.hashCond = plan['Hash Cond'] as string;
  if (plan['Merge Cond']) result.mergeCond = plan['Merge Cond'] as string;
  if (plan['CTE Name']) result.cteName = plan['CTE Name'] as string;
  if (plan['Subplan Name']) result.subplanName = plan['Subplan Name'] as string;
  if (plan['Parallel Aware']) result.parallelAware = plan['Parallel Aware'] as boolean;

  // ANALYZE metrics
  if (plan['Actual Rows'] !== undefined) result.actualRows = plan['Actual Rows'] as number;
  if (plan['Actual Loops'] !== undefined) result.actualLoops = plan['Actual Loops'] as number;
  if (plan['Actual Startup Time'] !== undefined)
    result.actualStartupTime = plan['Actual Startup Time'] as number;
  if (plan['Actual Total Time'] !== undefined)
    result.actualTotalTime = plan['Actual Total Time'] as number;

  // Recursively parse child plans
  if (plan['Plans'] && Array.isArray(plan['Plans'])) {
    result.plans = (plan['Plans'] as Record<string, unknown>[]).map(parsePlanNode);
  }

  return result;
}

// Get category badge variant
const categoryBadgeVariants: Record<NodeTypeCategory, 'info' | 'primary' | 'warning' | 'success' | 'default'> = {
  scan: 'info',
  join: 'primary',
  aggregate: 'warning',
  sort: 'success',
  other: 'default',
};

// Node type assessment types
type AssessmentLevel = 'success' | 'warning' | 'danger' | 'info';

interface NodeAssessment {
  level: AssessmentLevel;
  label: string;
  tooltip: string;
  icon: React.ReactNode;
}

// Get node type assessment based on node characteristics
function getNodeAssessment(node: PlanNodeMetrics): NodeAssessment {
  const { nodeType, planRows, indexCond } = node;

  // Index Only Scan - Best performance
  if (nodeType === 'Index Only Scan') {
    return {
      level: 'success',
      label: '최적 인덱스',
      tooltip: '인덱스만으로 데이터를 조회합니다. 테이블 접근 없이 빠르게 결과를 반환합니다.',
      icon: <CheckCircle2 className="h-3 w-3" />,
    };
  }

  // Index Scan - Good performance
  if (nodeType === 'Index Scan' || nodeType === 'Bitmap Index Scan') {
    return {
      level: 'success',
      label: '인덱스 사용',
      tooltip: '인덱스를 활용하여 효율적으로 데이터를 검색합니다.',
      icon: <CheckCircle2 className="h-3 w-3" />,
    };
  }

  // Seq Scan - Evaluate based on row count
  if (nodeType === 'Seq Scan') {
    if (planRows < 1000) {
      return {
        level: 'success',
        label: '소규모 스캔',
        tooltip: '소규모 테이블의 전체 스캔입니다. 이 규모에서는 인덱스보다 효율적일 수 있습니다.',
        icon: <CheckCircle2 className="h-3 w-3" />,
      };
    }
    if (planRows < 100000) {
      return {
        level: 'warning',
        label: '중규모 스캔',
        tooltip: `${planRows.toLocaleString()}개 행을 전체 스캔합니다. 자주 실행되는 쿼리라면 인덱스 추가를 고려하세요.`,
        icon: <AlertTriangle className="h-3 w-3" />,
      };
    }
    return {
      level: 'danger',
      label: '대규모 스캔',
      tooltip: `${planRows.toLocaleString()}개 이상의 행을 전체 스캔합니다. 적절한 인덱스 생성을 강력히 권장합니다.`,
      icon: <XCircle className="h-3 w-3" />,
    };
  }

  // Nested Loop - Evaluate based on row count
  if (nodeType === 'Nested Loop') {
    if (planRows > 10000) {
      return {
        level: 'warning',
        label: '대량 중첩 루프',
        tooltip: `${planRows.toLocaleString()}개 행에 대한 중첩 루프입니다. 대량 데이터에서는 Hash Join이 더 효율적일 수 있습니다.`,
        icon: <AlertTriangle className="h-3 w-3" />,
      };
    }
    return {
      level: 'info',
      label: '중첩 루프',
      tooltip: '소규모 데이터셋에 적합한 조인 방식입니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Sort - Evaluate based on row count
  if (nodeType === 'Sort') {
    if (planRows > 100000) {
      return {
        level: 'warning',
        label: '대량 정렬',
        tooltip: `${planRows.toLocaleString()}개 행을 정렬합니다. 메모리 사용량이 높을 수 있으며, 정렬된 인덱스 활용을 고려하세요.`,
        icon: <AlertTriangle className="h-3 w-3" />,
      };
    }
    return {
      level: 'info',
      label: '정렬',
      tooltip: '데이터 정렬 작업입니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Hash Join
  if (nodeType === 'Hash Join' || nodeType === 'Hash') {
    return {
      level: 'info',
      label: '해시 조인',
      tooltip: '해시 테이블을 생성하여 조인합니다. 대량 데이터 조인에 효율적입니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Merge Join
  if (nodeType === 'Merge Join') {
    return {
      level: 'info',
      label: '병합 조인',
      tooltip: '정렬된 데이터를 병합하여 조인합니다. 이미 정렬된 데이터에 효율적입니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Aggregate
  if (nodeType === 'Aggregate' || nodeType === 'HashAggregate' || nodeType === 'GroupAggregate') {
    return {
      level: 'info',
      label: '집계',
      tooltip: '데이터를 그룹화하거나 집계 함수를 수행합니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // CTE Scan
  if (nodeType === 'CTE Scan') {
    return {
      level: 'info',
      label: 'CTE 스캔',
      tooltip: 'WITH 절로 정의된 공통 테이블 표현식(CTE)을 스캔합니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Bitmap Heap Scan
  if (nodeType === 'Bitmap Heap Scan') {
    if (!indexCond) {
      return {
        level: 'warning',
        label: '비트맵 힙 스캔',
        tooltip: '비트맵 인덱스 후 힙 스캔이 필요합니다. 필터 조건이 많을 수 있습니다.',
        icon: <AlertTriangle className="h-3 w-3" />,
      };
    }
    return {
      level: 'info',
      label: '비트맵 힙 스캔',
      tooltip: '비트맵 인덱스를 활용한 힙 스캔입니다.',
      icon: <Info className="h-3 w-3" />,
    };
  }

  // Default
  return {
    level: 'info',
    label: nodeType,
    tooltip: `${nodeType} 노드입니다.`,
    icon: <Info className="h-3 w-3" />,
  };
}

// Get additional warnings based on node characteristics
function getAdditionalWarnings(node: PlanNodeMetrics): NodeAssessment[] {
  const warnings: NodeAssessment[] = [];

  // Bulk processing warning
  if (node.planRows > 10000) {
    warnings.push({
      level: 'warning',
      label: '대량 처리',
      tooltip: `${node.planRows.toLocaleString()}개 행을 처리합니다. 대량 데이터 처리로 인해 성능에 영향을 줄 수 있습니다.`,
      icon: <AlertTriangle className="h-3 w-3" />,
    });
  }

  // Post-filter warning (filter without index condition)
  if (node.filter && !node.indexCond) {
    warnings.push({
      level: 'warning',
      label: '필터 후처리',
      tooltip: '데이터를 먼저 읽은 후 필터링합니다. 해당 조건에 인덱스를 추가하면 성능이 향상될 수 있습니다.',
      icon: <Filter className="h-3 w-3" />,
    });
  }

  return warnings;
}

// 시간 포맷팅 헬퍼
function formatTime(ms: number): string {
  if (ms < 1) {
    return `${(ms * 1000).toFixed(1)} µs`;
  }
  if (ms < 1000) {
    return `${ms.toFixed(2)} ms`;
  }
  return `${(ms / 1000).toFixed(2)} s`;
}

// 정확도 계산 및 평가
function getRowsAccuracyInfo(planRows: number, actualRows: number): {
  accuracy: number;
  label: string;
  variant: 'success' | 'warning' | 'danger';
  tooltip: string;
} {
  if (planRows === 0) {
    return {
      accuracy: 1,
      label: '-',
      variant: 'success',
      tooltip: '예상 행이 0이므로 정확도 계산 불가',
    };
  }

  const accuracy = actualRows / planRows;
  const percent = (accuracy * 100).toFixed(0);

  if (accuracy >= 0.5 && accuracy <= 2) {
    return {
      accuracy,
      label: `${percent}%`,
      variant: 'success',
      tooltip: `예상 행 수가 정확합니다 (예상: ${planRows.toLocaleString()}, 실제: ${actualRows.toLocaleString()})`,
    };
  }

  if (accuracy > 2) {
    const factor = accuracy.toFixed(1);
    return {
      accuracy,
      label: `${factor}x 과소`,
      variant: accuracy > 10 ? 'danger' : 'warning',
      tooltip: `실제 행이 예상보다 ${factor}배 많음 (예상: ${planRows.toLocaleString()}, 실제: ${actualRows.toLocaleString()}). 통계 갱신(ANALYZE)이 필요할 수 있습니다.`,
    };
  }

  const factor = (1 / accuracy).toFixed(1);
  return {
    accuracy,
    label: `${factor}x 과대`,
    variant: accuracy < 0.1 ? 'danger' : 'warning',
    tooltip: `실제 행이 예상보다 ${factor}배 적음 (예상: ${planRows.toLocaleString()}, 실제: ${actualRows.toLocaleString()}). 통계 갱신(ANALYZE)이 필요할 수 있습니다.`,
  };
}

// Performance Indicator component
function PerformanceIndicator({ node }: { node: PlanNodeMetrics }) {
  const assessment = getNodeAssessment(node);
  const additionalWarnings = getAdditionalWarnings(node);
  const hasAnalyzeData = node.actualRows !== undefined || node.actualTotalTime !== undefined;

  // Don't show duplicates
  const showBulkWarning = additionalWarnings.some((w) => w.label === '대량 처리');
  const showFilterWarning = additionalWarnings.some((w) => w.label === '필터 후처리');

  // 행 정확도 정보
  const rowsAccuracyInfo =
    hasAnalyzeData && node.actualRows !== undefined
      ? getRowsAccuracyInfo(node.planRows, node.actualRows)
      : null;

  return (
    <div className="mb-4">
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
        성능 상태
      </h4>
      <div className="flex flex-wrap gap-2">
        {/* Main node assessment */}
        <TooltipBadge variant={assessment.level} tooltip={assessment.tooltip}>
          {assessment.icon}
          <span>{assessment.label}</span>
        </TooltipBadge>

        {/* Bulk processing warning */}
        {showBulkWarning && (
          <TooltipBadge
            variant="warning"
            tooltip={`${node.planRows.toLocaleString()}개 행을 처리합니다. 대량 데이터 처리로 인해 성능에 영향을 줄 수 있습니다.`}
          >
            <AlertTriangle className="h-3 w-3" />
            <span>대량 처리</span>
          </TooltipBadge>
        )}

        {/* Post-filter warning */}
        {showFilterWarning && (
          <TooltipBadge
            variant="warning"
            tooltip="데이터를 먼저 읽은 후 필터링합니다. 해당 조건에 인덱스를 추가하면 성능이 향상될 수 있습니다."
          >
            <Filter className="h-3 w-3" />
            <span>필터 후처리</span>
          </TooltipBadge>
        )}

        {/* Parallel processing indicator */}
        {node.parallelAware && (
          <TooltipBadge
            variant="success"
            tooltip="병렬 처리가 가능한 노드입니다. 여러 워커가 동시에 작업하여 성능이 향상됩니다."
          >
            <Zap className="h-3 w-3" />
            <span>병렬 처리</span>
          </TooltipBadge>
        )}

        {/* ANALYZE: 행 정확도 표시 */}
        {rowsAccuracyInfo && (
          <TooltipBadge variant={rowsAccuracyInfo.variant} tooltip={rowsAccuracyInfo.tooltip}>
            <BarChart3 className="h-3 w-3" />
            <span>정확도 {rowsAccuracyInfo.label}</span>
          </TooltipBadge>
        )}
      </div>

      {/* ANALYZE 메트릭 상세 (실제 실행 데이터가 있을 때만) */}
      {hasAnalyzeData && (
        <div className="mt-3 rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
          <h5 className="mb-2 flex items-center gap-1 text-xs font-semibold text-blue-700 dark:text-blue-400">
            <Timer className="h-3 w-3" />
            실제 실행 데이터 (ANALYZE)
          </h5>
          <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            {node.actualTotalTime !== undefined && (
              <div>
                <span className="text-xs text-blue-600 dark:text-blue-400">실행 시간</span>
                <div className="font-medium text-blue-800 dark:text-blue-300">
                  {formatTime(node.actualTotalTime * (node.actualLoops ?? 1))}
                </div>
              </div>
            )}
            {node.actualRows !== undefined && (
              <div>
                <span className="text-xs text-blue-600 dark:text-blue-400">실제 행</span>
                <div className="font-medium text-blue-800 dark:text-blue-300">
                  {node.actualRows.toLocaleString()}
                  <span className="ml-1 text-xs text-blue-500">
                    (예상: {node.planRows.toLocaleString()})
                  </span>
                </div>
              </div>
            )}
            {node.actualLoops !== undefined && node.actualLoops > 1 && (
              <div>
                <span className="text-xs text-blue-600 dark:text-blue-400">루프 횟수</span>
                <div className="flex items-center gap-1 font-medium text-blue-800 dark:text-blue-300">
                  <RefreshCw className="h-3 w-3" />
                  {node.actualLoops.toLocaleString()}회
                </div>
              </div>
            )}
            {node.actualStartupTime !== undefined && (
              <div>
                <span className="text-xs text-blue-600 dark:text-blue-400">시작 시간</span>
                <div className="font-medium text-blue-800 dark:text-blue-300">
                  {formatTime(node.actualStartupTime)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Info status type
type InfoStatus = 'good' | 'neutral' | 'warning';

// Info item component with explanation and status
function InfoItem({
  icon,
  label,
  value,
  explanation,
  status = 'neutral',
}: {
  icon: React.ReactNode;
  label: string;
  value: string | string[];
  explanation?: string;
  status?: InfoStatus;
}) {
  const displayValue = Array.isArray(value) ? value.join(', ') : value;

  const statusBorderColors: Record<InfoStatus, string> = {
    good: 'border-l-green-500',
    neutral: 'border-l-gray-300 dark:border-l-gray-600',
    warning: 'border-l-yellow-500',
  };

  return (
    <div
      className={cn(
        'border-l-2 pl-3 py-1',
        statusBorderColors[status]
      )}
    >
      <div className="flex items-start gap-2 text-sm">
        <span className="flex-shrink-0 text-gray-400 dark:text-gray-500 mt-0.5">
          {icon}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-gray-500 dark:text-gray-400">{label}:</span>
            <span className="font-medium text-gray-700 dark:text-gray-300 break-all">
              {displayValue}
            </span>
          </div>
          {explanation && (
            <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
              {explanation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// Accordion item component
function PlanNodeItem({
  node,
  depth,
  defaultExpanded,
}: {
  node: PlanNodeMetrics;
  depth: number;
  defaultExpanded?: boolean;
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded ?? depth === 0);
  const category = getNodeTypeCategory(node.nodeType as never);
  const badgeVariant = categoryBadgeVariants[category];

  const toggleExpand = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  // Generate summary text
  const getSummary = () => {
    if (node.relationName) {
      return node.alias && node.alias !== node.relationName
        ? `${node.relationName} (${node.alias})`
        : node.relationName;
    }
    if (node.joinType) return node.joinType;
    if (node.cteName) return `CTE: ${node.cteName}`;
    if (node.sortKey) return `by ${node.sortKey.join(', ')}`;
    return null;
  };

  const summary = getSummary();
  const hasChildren = node.plans && node.plans.length > 0;
  const hasAdditionalInfo =
    node.relationName ||
    node.indexName ||
    node.indexCond ||
    node.filter ||
    node.sortKey ||
    node.hashCond ||
    node.mergeCond;

  // Get explanation and status for each info item
  const getTableExplanation = () => {
    if (node.nodeType === 'Seq Scan') {
      return { explanation: '전체 테이블을 순차적으로 스캔합니다.', status: 'neutral' as InfoStatus };
    }
    if (node.nodeType.includes('Index')) {
      return { explanation: '인덱스를 통해 효율적으로 접근합니다.', status: 'good' as InfoStatus };
    }
    return { explanation: '스캔 대상 테이블입니다.', status: 'neutral' as InfoStatus };
  };

  const getFilterExplanation = (): { explanation: string; status: InfoStatus } => {
    if (!node.indexCond) {
      return {
        explanation: '전체 데이터를 읽은 후 필터링됩니다. 이 조건에 인덱스 생성을 고려하세요.',
        status: 'warning',
      };
    }
    return {
      explanation: '인덱스 조건과 함께 사용되어 효율적으로 필터링됩니다.',
      status: 'good',
    };
  };

  return (
    <div
      className={cn(
        'rounded-lg border transition-all',
        isExpanded
          ? 'border-gray-300 dark:border-gray-600'
          : 'border-gray-200 dark:border-gray-700'
      )}
      style={{ marginLeft: depth > 0 ? '1rem' : 0 }}
    >
      {/* Header - always visible */}
      <button
        type="button"
        onClick={toggleExpand}
        className={cn(
          'flex w-full items-center gap-3 px-4 py-3 text-left transition-colors',
          'hover:bg-gray-50 dark:hover:bg-gray-800/50',
          'rounded-lg',
          isExpanded && 'rounded-b-none'
        )}
      >
        <span className="flex-shrink-0 text-gray-400">
          {isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </span>
        <Badge variant={badgeVariant} size="sm">
          {node.nodeType}
        </Badge>
        {summary && (
          <span className="truncate text-sm text-gray-600 dark:text-gray-400">
            {summary}
          </span>
        )}
        <span className="ml-auto flex-shrink-0 text-sm font-medium text-gray-500 dark:text-gray-400">
          총 비용: <span className="text-gray-900 dark:text-white">{formatCost(node.totalCost)}</span>
        </span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="border-t border-gray-200 px-4 py-4 dark:border-gray-700">
          {/* Performance indicator */}
          <PerformanceIndicator node={node} />

          {/* Additional info */}
          {hasAdditionalInfo && (
            <div className="mb-4">
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                실행 상세
              </h4>
              <div className="space-y-2 rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                {node.relationName && (
                  <InfoItem
                    icon={<Table2 className="h-4 w-4" />}
                    label="테이블"
                    value={
                      node.alias && node.alias !== node.relationName
                        ? `${node.relationName} (별칭: ${node.alias})`
                        : node.relationName
                    }
                    {...getTableExplanation()}
                  />
                )}
                {node.indexName && (
                  <InfoItem
                    icon={<Database className="h-4 w-4" />}
                    label="인덱스"
                    value={node.indexName}
                    explanation="검색에 사용되는 인덱스입니다."
                    status="good"
                  />
                )}
                {node.indexCond && (
                  <InfoItem
                    icon={<Link2 className="h-4 w-4" />}
                    label="인덱스 조건"
                    value={node.indexCond}
                    explanation="인덱스를 통해 직접 검색되는 조건입니다."
                    status="good"
                  />
                )}
                {node.filter && (
                  <InfoItem
                    icon={<Filter className="h-4 w-4" />}
                    label="필터"
                    value={node.filter}
                    {...getFilterExplanation()}
                  />
                )}
                {node.sortKey && (
                  <InfoItem
                    icon={<ArrowUpDown className="h-4 w-4" />}
                    label="정렬 키"
                    value={node.sortKey}
                    explanation={
                      node.planRows > 100000
                        ? '대량 데이터 정렬입니다. 정렬된 인덱스 사용을 고려하세요.'
                        : '이 컬럼 기준으로 정렬됩니다.'
                    }
                    status={node.planRows > 100000 ? 'warning' : 'neutral'}
                  />
                )}
                {node.hashCond && (
                  <InfoItem
                    icon={<Hash className="h-4 w-4" />}
                    label="해시 조건"
                    value={node.hashCond}
                    explanation="해시 테이블 생성 및 조인에 사용되는 조건입니다."
                    status="neutral"
                  />
                )}
                {node.mergeCond && (
                  <InfoItem
                    icon={<Link2 className="h-4 w-4" />}
                    label="병합 조건"
                    value={node.mergeCond}
                    explanation="정렬된 데이터를 병합하여 조인하는 조건입니다."
                    status="neutral"
                  />
                )}
              </div>
            </div>
          )}

          {/* Child plans */}
          {hasChildren && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                하위 계획 ({node.plans!.length})
              </h4>
              <div className="space-y-2">
                {node.plans!.map((childNode, index) => (
                  <PlanNodeItem
                    key={`${childNode.nodeType}-${index}`}
                    node={childNode}
                    depth={depth + 1}
                    defaultExpanded={false}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function PlanNodeAccordion({ planRaw, className }: PlanNodeAccordionProps) {
  // Parse the plan_raw to extract plan node
  const planNode = parsePlanNode(planRaw);

  return (
    <div className={cn('space-y-2', className)}>
      <PlanNodeItem node={planNode} depth={0} defaultExpanded />
    </div>
  );
}
