/**
 * 실행 계획 분석 알고리즘
 * - 트리 평탄화
 * - 비용 기여도 계산
 * - 병목 탐지
 * - 최적화 제안 생성
 */

import type {
  PlanNode,
  FlattenedNode,
  CostContribution,
  BottleneckNode,
  OptimizationSuggestion,
  PlanAnalysisResult,
  SuggestionPriority,
  AnalyzeMetrics,
  NodeTiming,
  EstimateAccuracy,
} from '@/types';

/**
 * 실행 계획 트리를 평탄화
 */
export function flattenPlanTree(
  plan: PlanNode,
  depth = 0,
  parentId?: string
): FlattenedNode[] {
  const nodes: FlattenedNode[] = [];
  const id = generateNodeId(plan, depth, parentId);

  // ANALYZE 메트릭 추출
  const actualRows = plan['Actual Rows'];
  const actualLoops = plan['Actual Loops'];
  const actualStartupTime = plan['Actual Startup Time'];
  const actualTotalTime = plan['Actual Total Time'];
  const planRows = plan['Plan Rows'] ?? 0;

  // 추정 정확도 계산 (planRows 대비 actualRows 비율)
  let rowsAccuracy: number | undefined;
  if (actualRows !== undefined && planRows > 0) {
    rowsAccuracy = actualRows / planRows;
  }

  const flatNode: FlattenedNode = {
    id,
    depth,
    nodeType: plan['Node Type'] || 'Unknown',
    relationName: plan['Relation Name'] || plan['Alias'],
    totalCost: plan['Total Cost'] ?? 0,
    startupCost: plan['Startup Cost'] ?? 0,
    planRows,
    planWidth: plan['Plan Width'] ?? 0,
    filter: plan['Filter'],
    indexCond: plan['Index Cond'],
    indexName: plan['Index Name'],
    sortKey: plan['Sort Key'],
    joinType: plan['Join Type'],
    cteName: plan['CTE Name'],
    parentId,
    raw: plan,
    // ANALYZE 메트릭
    actualRows,
    actualLoops,
    actualStartupTime,
    actualTotalTime,
    rowsAccuracy,
  };

  nodes.push(flatNode);

  // 자식 노드 재귀 처리
  if (plan.Plans && Array.isArray(plan.Plans)) {
    for (const childPlan of plan.Plans) {
      const childNodes = flattenPlanTree(childPlan, depth + 1, id);
      nodes.push(...childNodes);
    }
  }

  return nodes;
}

/**
 * 노드 ID 생성
 */
function generateNodeId(plan: PlanNode, depth: number, parentId?: string): string {
  const nodeType = plan['Node Type'] || 'Unknown';
  const relation = plan['Relation Name'] || plan['Alias'] || '';
  const base = `${nodeType}-${relation}-${depth}`;
  return parentId ? `${parentId}/${base}` : base;
}

/**
 * 각 노드의 비용 기여도 계산
 */
export function calculateCostContributions(
  nodes: FlattenedNode[],
  rootCost: number
): Map<string, CostContribution> {
  const contributions = new Map<string, CostContribution>();

  if (rootCost <= 0) {
    return contributions;
  }

  // 비용 기준 정렬
  const sortedNodes = [...nodes].sort((a, b) => b.totalCost - a.totalCost);

  let cumulativePercentage = 0;
  for (const node of sortedNodes) {
    const percentage = (node.totalCost / rootCost) * 100;
    cumulativePercentage += percentage;

    contributions.set(node.id, {
      nodeId: node.id,
      absoluteCost: node.totalCost,
      percentage: Math.min(percentage, 100),
      cumulativePercentage: Math.min(cumulativePercentage, 100),
    });
  }

  return contributions;
}

/**
 * 병목 지점 탐지
 */
export function identifyBottlenecks(
  nodes: FlattenedNode[],
  contributions: Map<string, CostContribution>
): BottleneckNode[] {
  const bottlenecks: BottleneckNode[] = [];
  const ROWS_THRESHOLD_LARGE = 10000;
  const ROWS_THRESHOLD_HUGE = 100000;

  for (const node of nodes) {
    const contribution = contributions.get(node.id);
    if (!contribution) continue;

    let score = 0;
    const reasons: string[] = [];

    // 비용 기여도 점수
    if (contribution.percentage >= 50) {
      score += 40;
      reasons.push(`전체 비용의 ${contribution.percentage.toFixed(1)}% 차지`);
    } else if (contribution.percentage >= 30) {
      score += 25;
      reasons.push(`전체 비용의 ${contribution.percentage.toFixed(1)}% 차지`);
    } else if (contribution.percentage >= 15) {
      score += 15;
      reasons.push(`전체 비용의 ${contribution.percentage.toFixed(1)}% 차지`);
    }

    // Seq Scan + 대량 행
    if (node.nodeType === 'Seq Scan' && node.planRows >= ROWS_THRESHOLD_LARGE) {
      score += 30;
      reasons.push(`대량 데이터(${formatRows(node.planRows)}행) 순차 스캔`);
    }

    // Nested Loop + 대량 행
    if (node.nodeType === 'Nested Loop' && node.planRows >= 50000) {
      score += 25;
      reasons.push(`대량 행(${formatRows(node.planRows)})에 대한 중첩 루프`);
    }

    // Sort + 대량 행
    if (node.nodeType === 'Sort' && node.planRows >= ROWS_THRESHOLD_HUGE) {
      score += 20;
      reasons.push(`대량 데이터(${formatRows(node.planRows)}행) 정렬`);
    }

    // Filter without Index
    if (node.filter && !node.indexCond && node.planRows >= ROWS_THRESHOLD_LARGE) {
      score += 15;
      reasons.push('인덱스 없는 필터 조건');
    }

    // Bitmap Heap Scan + 대량 행 (인덱스 활용하지만 많은 행)
    if (node.nodeType === 'Bitmap Heap Scan' && node.planRows >= ROWS_THRESHOLD_HUGE) {
      score += 10;
      reasons.push('비트맵 힙 스캔으로 대량 행 접근');
    }

    // Hash 생성 비용
    if (node.nodeType === 'Hash' && node.planRows >= ROWS_THRESHOLD_HUGE) {
      score += 10;
      reasons.push('대량 해시 테이블 생성');
    }

    // 점수가 충분히 높은 경우 병목으로 판단
    if (score >= 15) {
      const severity = getSeverityFromScore(score);
      bottlenecks.push({
        node,
        contribution,
        severity,
        reason: reasons.join(', '),
        score,
      });
    }
  }

  // 점수 기준 정렬 후 상위 5개
  return bottlenecks
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);
}

/**
 * 최적화 제안 생성
 */
export function generateOptimizationSuggestions(
  nodes: FlattenedNode[],
  contributions: Map<string, CostContribution>
): OptimizationSuggestion[] {
  const suggestions: OptimizationSuggestion[] = [];
  const ROWS_THRESHOLD_LARGE = 10000;
  const ROWS_THRESHOLD_HUGE = 100000;

  for (const node of nodes) {
    const contribution = contributions.get(node.id);
    const percentage = contribution?.percentage ?? 0;

    // Seq Scan + Filter + 대량 행 → 인덱스 제안
    if (
      node.nodeType === 'Seq Scan' &&
      node.filter &&
      node.planRows >= ROWS_THRESHOLD_LARGE &&
      node.relationName
    ) {
      const filterColumn = extractColumnFromFilter(node.filter);
      const priority = getPriorityFromPercentage(percentage);

      suggestions.push({
        id: `idx-${node.id}`,
        nodeId: node.id,
        priority,
        category: 'index',
        title: `${node.relationName} 테이블에 인덱스 추가 권장`,
        description: `${formatRows(node.planRows)}행에 대한 순차 스캔이 발생합니다. 필터 조건에 대한 인덱스를 생성하면 성능이 개선될 수 있습니다.`,
        sql: filterColumn
          ? `CREATE INDEX idx_${node.relationName}_${filterColumn}\nON ${node.relationName} (${filterColumn});`
          : `-- 필터 조건 분석 필요\n-- CREATE INDEX idx_${node.relationName}_<column>\n-- ON ${node.relationName} (<column>);`,
        expectedImpact: 'Seq Scan → Index Scan 전환으로 대량 데이터 스캔 최소화',
      });
    }

    // Sort + 대량 행 → 정렬 키 인덱스
    if (
      node.nodeType === 'Sort' &&
      node.sortKey &&
      node.sortKey.length > 0 &&
      node.planRows >= ROWS_THRESHOLD_HUGE
    ) {
      const sortColumns = node.sortKey.map(extractSortColumn).filter(Boolean);
      const priority = getPriorityFromPercentage(percentage);

      // 부모 노드에서 테이블 이름 찾기
      const tableName = findRelationName(nodes, node);

      if (tableName && sortColumns.length > 0) {
        suggestions.push({
          id: `sort-idx-${node.id}`,
          nodeId: node.id,
          priority,
          category: 'sort',
          title: `정렬 키에 대한 인덱스 추가 권장`,
          description: `${formatRows(node.planRows)}행에 대한 정렬이 발생합니다. 정렬 키에 인덱스를 생성하면 정렬 작업을 피할 수 있습니다.`,
          sql: `CREATE INDEX idx_${tableName}_${sortColumns.join('_')}\nON ${tableName} (${sortColumns.join(', ')});`,
          expectedImpact: '메모리/디스크 정렬 제거, 인덱스 순서 활용',
        });
      }
    }

    // Nested Loop + 대량 행 → Hash Join 검토
    if (node.nodeType === 'Nested Loop' && node.planRows >= 50000) {
      const priority = getPriorityFromPercentage(percentage);

      suggestions.push({
        id: `join-${node.id}`,
        nodeId: node.id,
        priority,
        category: 'join',
        title: '조인 전략 검토 권장',
        description: `${formatRows(node.planRows)}행에 대한 Nested Loop 조인이 발생합니다. 대량 데이터의 경우 Hash Join이 더 효율적일 수 있습니다.`,
        sql: `-- enable_nestloop = off 설정으로 Hash Join 강제 테스트\nSET enable_nestloop = off;\n-- 쿼리 실행 후 비용 비교\n-- SET enable_nestloop = on;`,
        expectedImpact: 'Nested Loop → Hash Join 전환 시 반복 스캔 감소',
      });
    }

    // Filter 조건이 있지만 Index Cond가 없는 경우
    if (
      node.filter &&
      !node.indexCond &&
      !['Seq Scan'].includes(node.nodeType) &&
      node.planRows >= ROWS_THRESHOLD_LARGE
    ) {
      const filterColumn = extractColumnFromFilter(node.filter);
      const tableName = node.relationName || findRelationName(nodes, node);
      const priority: SuggestionPriority = percentage >= 20 ? 'high' : 'medium';

      if (tableName && filterColumn) {
        suggestions.push({
          id: `filter-idx-${node.id}`,
          nodeId: node.id,
          priority,
          category: 'filter',
          title: `필터 조건에 대한 인덱스 검토`,
          description: `필터 조건이 인덱스를 활용하지 않고 있습니다. 해당 컬럼에 인덱스를 추가하면 필터링 성능이 개선될 수 있습니다.`,
          sql: `CREATE INDEX idx_${tableName}_${filterColumn}\nON ${tableName} (${filterColumn});`,
          expectedImpact: '필터 조건의 인덱스 활용으로 스캔 범위 축소',
        });
      }
    }

    // CTE Scan + 대량 행 → Materialized 검토
    if (node.nodeType === 'CTE Scan' && node.planRows >= ROWS_THRESHOLD_LARGE && node.cteName) {
      suggestions.push({
        id: `cte-${node.id}`,
        nodeId: node.id,
        priority: 'medium',
        category: 'general',
        title: `CTE 최적화 검토 (${node.cteName})`,
        description: `CTE가 ${formatRows(node.planRows)}행을 반환합니다. PostgreSQL 12+에서는 NOT MATERIALIZED 힌트로 인라인화를 유도할 수 있습니다.`,
        sql: `-- CTE를 서브쿼리로 변환하거나 NOT MATERIALIZED 힌트 사용\nWITH ${node.cteName} AS NOT MATERIALIZED (\n  -- 원본 CTE 쿼리\n)`,
        expectedImpact: 'CTE 물리화 비용 제거, 옵티마이저 최적화 기회 증가',
      });
    }
  }

  // 우선순위 기준 정렬
  const priorityOrder: Record<SuggestionPriority, number> = {
    critical: 0,
    high: 1,
    medium: 2,
    low: 3,
  };

  return suggestions
    .sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
    .slice(0, 10);
}

/**
 * 전체 분석 실행
 */
export function analyzePlan(planRaw: Record<string, unknown>): PlanAnalysisResult | null {
  // EXPLAIN 결과 구조 파싱 (배열 또는 단일 객체)
  let rootPlan: PlanNode | null = null;
  let executionTime = 0;
  let planningTime = 0;

  if (Array.isArray(planRaw)) {
    // [{ "Plan": {...}, "Execution Time": ..., "Planning Time": ... }] 형식
    const firstItem = planRaw[0];
    if (firstItem && typeof firstItem === 'object' && 'Plan' in firstItem) {
      rootPlan = (firstItem as { Plan: PlanNode }).Plan;
      executionTime = (firstItem as { 'Execution Time'?: number })['Execution Time'] ?? 0;
      planningTime = (firstItem as { 'Planning Time'?: number })['Planning Time'] ?? 0;
    }
  } else if ('Plan' in planRaw) {
    // { "Plan": {...} } 형식
    rootPlan = (planRaw as { Plan: PlanNode }).Plan;
    executionTime = (planRaw as { 'Execution Time'?: number })['Execution Time'] ?? 0;
    planningTime = (planRaw as { 'Planning Time'?: number })['Planning Time'] ?? 0;
  } else if ('Node Type' in planRaw) {
    // 직접 Plan 노드
    rootPlan = planRaw as unknown as PlanNode;
  }

  if (!rootPlan) {
    return null;
  }

  const flattenedNodes = flattenPlanTree(rootPlan);
  const rootCost = rootPlan['Total Cost'] ?? 0;
  const costContributions = calculateCostContributions(flattenedNodes, rootCost);
  const bottlenecks = identifyBottlenecks(flattenedNodes, costContributions);
  const suggestions = generateOptimizationSuggestions(flattenedNodes, costContributions);
  const analyzeMetrics = extractAnalyzeMetrics(flattenedNodes, executionTime, planningTime);

  return {
    flattenedNodes,
    costContributions,
    bottlenecks,
    suggestions,
    totalCost: rootCost,
    rootNodeType: rootPlan['Node Type'] || 'Unknown',
    analyzeMetrics,
  };
}

/**
 * ANALYZE 메트릭 추출
 */
export function extractAnalyzeMetrics(
  nodes: FlattenedNode[],
  executionTime: number,
  planningTime: number
): AnalyzeMetrics | undefined {
  // ANALYZE 데이터가 있는지 확인
  const hasAnalyzeData = nodes.some(
    (node) => node.actualRows !== undefined || node.actualTotalTime !== undefined
  );

  if (!hasAnalyzeData && executionTime === 0) {
    return undefined;
  }

  // 노드별 타이밍 정보 추출
  const nodeTimings: NodeTiming[] = [];
  const totalActualTime = executionTime > 0 ? executionTime : calculateTotalActualTime(nodes);

  for (const node of nodes) {
    if (node.actualTotalTime !== undefined) {
      const actualTime = node.actualTotalTime * (node.actualLoops ?? 1);
      const timePercentage = totalActualTime > 0 ? (actualTime / totalActualTime) * 100 : 0;
      const rowsAccuracy =
        node.planRows > 0 && node.actualRows !== undefined
          ? node.actualRows / node.planRows
          : 1;

      nodeTimings.push({
        nodeId: node.id,
        nodeType: node.nodeType,
        actualTime,
        timePercentage,
        actualRows: node.actualRows ?? 0,
        planRows: node.planRows,
        rowsAccuracy,
        loops: node.actualLoops ?? 1,
      });
    }
  }

  // 시간 비율 기준 정렬
  nodeTimings.sort((a, b) => b.timePercentage - a.timePercentage);

  return {
    executionTime,
    planningTime,
    nodeTimings,
    hasAnalyzeData,
  };
}

/**
 * 루트 노드의 총 실제 시간 계산
 */
function calculateTotalActualTime(nodes: FlattenedNode[]): number {
  // depth가 0인 루트 노드 찾기
  const rootNode = nodes.find((n) => n.depth === 0);
  if (rootNode?.actualTotalTime !== undefined) {
    return rootNode.actualTotalTime * (rootNode.actualLoops ?? 1);
  }
  return 0;
}

/**
 * 추정 정확도 분석
 */
export function calculateEstimateAccuracy(nodes: FlattenedNode[]): EstimateAccuracy[] {
  const accuracies: EstimateAccuracy[] = [];

  for (const node of nodes) {
    if (node.actualRows !== undefined && node.planRows > 0) {
      const accuracy = node.actualRows / node.planRows;
      let severity: EstimateAccuracy['severity'];

      if (accuracy >= 0.5 && accuracy <= 2) {
        severity = 'accurate';
      } else if (accuracy > 2 && accuracy <= 10) {
        severity = 'underestimate';
      } else if (accuracy < 0.5 && accuracy >= 0.1) {
        severity = 'overestimate';
      } else {
        severity = 'severe';
      }

      accuracies.push({
        nodeId: node.id,
        nodeType: node.nodeType,
        estimatedRows: node.planRows,
        actualRows: node.actualRows,
        accuracy,
        severity,
      });
    }
  }

  // 심각도 기준 정렬 (severe > underestimate/overestimate > accurate)
  const severityOrder: Record<EstimateAccuracy['severity'], number> = {
    severe: 0,
    underestimate: 1,
    overestimate: 1,
    accurate: 2,
  };

  return accuracies.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
}

/**
 * 시간 기준 병목 노드 식별
 */
export function identifyTimeBottlenecks(nodes: FlattenedNode[]): FlattenedNode[] {
  const nodesWithTime = nodes.filter(
    (n) => n.actualTotalTime !== undefined && n.actualTotalTime > 0
  );

  // 실제 시간 기준 정렬하여 상위 5개 반환
  return nodesWithTime
    .sort((a, b) => {
      const timeA = (a.actualTotalTime ?? 0) * (a.actualLoops ?? 1);
      const timeB = (b.actualTotalTime ?? 0) * (b.actualLoops ?? 1);
      return timeB - timeA;
    })
    .slice(0, 5);
}

// === Helper Functions ===

function formatRows(rows: number): string {
  if (rows >= 1_000_000) {
    return `${(rows / 1_000_000).toFixed(1)}M`;
  }
  if (rows >= 1_000) {
    return `${(rows / 1_000).toFixed(1)}K`;
  }
  return rows.toLocaleString('ko-KR');
}

function getSeverityFromScore(score: number): BottleneckNode['severity'] {
  if (score >= 50) return 'critical';
  if (score >= 35) return 'high';
  if (score >= 20) return 'medium';
  return 'low';
}

function getPriorityFromPercentage(percentage: number): SuggestionPriority {
  if (percentage >= 40) return 'critical';
  if (percentage >= 25) return 'high';
  if (percentage >= 10) return 'medium';
  return 'low';
}

function extractColumnFromFilter(filter: string): string | null {
  // 간단한 패턴 매칭: (column = value) 또는 column = value
  const patterns = [
    /\((\w+)\s*=\s*/,
    /(\w+)\s*=\s*/,
    /\((\w+)\s*[<>]/,
    /(\w+)\s*[<>]/,
    /(\w+)\s+IS\s+/i,
    /(\w+)\s+IN\s*\(/i,
    /(\w+)\s+LIKE\s+/i,
  ];

  for (const pattern of patterns) {
    const match = filter.match(pattern);
    if (match && match[1]) {
      return match[1].toLowerCase();
    }
  }

  return null;
}

function extractSortColumn(sortKey: string): string | null {
  // "column ASC" 또는 "column DESC" 에서 컬럼명 추출
  const match = sortKey.match(/^(\w+)/);
  return match ? match[1].toLowerCase() : null;
}

function findRelationName(nodes: FlattenedNode[], targetNode: FlattenedNode): string | null {
  // 현재 노드의 자식들 중 테이블 이름 찾기
  const childNodes = nodes.filter((n) => n.parentId === targetNode.id);
  for (const child of childNodes) {
    if (child.relationName) {
      return child.relationName;
    }
    const childRelation = findRelationName(nodes, child);
    if (childRelation) {
      return childRelation;
    }
  }

  // 부모 노드에서 찾기
  if (targetNode.parentId) {
    const parent = nodes.find((n) => n.id === targetNode.parentId);
    if (parent?.relationName) {
      return parent.relationName;
    }
  }

  return null;
}
