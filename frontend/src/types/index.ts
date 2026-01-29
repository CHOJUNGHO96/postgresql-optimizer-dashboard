// API Response Types

export interface CostEstimate {
  startup_cost: number;
  total_cost: number;
  plan_rows: number;
  plan_width: number;
}

export interface QueryPlanResponse {
  id: string;
  query: string;
  title: string | null;
  node_type: PlanNodeType;
  cost_estimate: CostEstimate;
  execution_time_ms: number | null;
  plan_raw: Record<string, unknown>;
  created_at: string;
}

export interface QueryPlanListResponse {
  items: QueryPlanResponse[];
  total: number;
}

export interface AnalyzeQueryRequest {
  query: string;
  title?: string;
}

export interface HealthResponse {
  status: string;
}

// Plan Node Types
export type PlanNodeType =
  | 'Seq Scan'
  | 'Index Scan'
  | 'Index Only Scan'
  | 'Bitmap Index Scan'
  | 'Bitmap Heap Scan'
  | 'Nested Loop'
  | 'Hash Join'
  | 'Merge Join'
  | 'Sort'
  | 'Hash'
  | 'Aggregate'
  | 'Group Aggregate'
  | 'HashAggregate'
  | 'Limit'
  | 'Append'
  | 'Materialize'
  | 'Subquery Scan'
  | 'CTE Scan'
  | 'Result'
  | 'Gather'
  | 'Gather Merge'
  | 'Other';

// Node Type Categories for styling
export type NodeTypeCategory = 'scan' | 'join' | 'aggregate' | 'sort' | 'other';

export interface NodeTypeInfo {
  category: NodeTypeCategory;
  label: string;
  description: string;
  color: string;
  bgColor: string;
}

// API Error
export interface ApiError {
  detail: string;
  status?: number;
}

// Plan Analysis Types

/** PostgreSQL EXPLAIN 노드의 원시 타입 */
export interface PlanNode {
  'Node Type': string;
  'Relation Name'?: string;
  'Alias'?: string;
  'Schema'?: string;
  'Startup Cost'?: number;
  'Total Cost'?: number;
  'Plan Rows'?: number;
  'Plan Width'?: number;
  'Filter'?: string;
  'Index Cond'?: string;
  'Index Name'?: string;
  'Sort Key'?: string[];
  'Join Type'?: string;
  'Hash Cond'?: string;
  'Merge Cond'?: string;
  'CTE Name'?: string;
  'Subplan Name'?: string;
  'Output'?: string[];
  'Actual Rows'?: number;
  'Actual Loops'?: number;
  'Actual Startup Time'?: number;
  'Actual Total Time'?: number;
  Plans?: PlanNode[];
  [key: string]: unknown;
}

/** 트리를 평탄화한 노드 */
export interface FlattenedNode {
  id: string;
  depth: number;
  nodeType: string;
  relationName?: string;
  totalCost: number;
  startupCost: number;
  planRows: number;
  planWidth: number;
  filter?: string;
  indexCond?: string;
  indexName?: string;
  sortKey?: string[];
  joinType?: string;
  cteName?: string;
  parentId?: string;
  raw: PlanNode;
}

/** 비용 기여도 정보 */
export interface CostContribution {
  nodeId: string;
  absoluteCost: number;
  percentage: number;
  cumulativePercentage: number;
}

/** 병목 노드 정보 */
export interface BottleneckNode {
  node: FlattenedNode;
  contribution: CostContribution;
  severity: 'critical' | 'high' | 'medium' | 'low';
  reason: string;
  score: number;
}

/** 최적화 제안 타입 */
export type SuggestionPriority = 'critical' | 'high' | 'medium' | 'low';
export type SuggestionCategory = 'index' | 'join' | 'sort' | 'filter' | 'scan' | 'general';

/** 최적화 제안 */
export interface OptimizationSuggestion {
  id: string;
  nodeId: string;
  priority: SuggestionPriority;
  category: SuggestionCategory;
  title: string;
  description: string;
  sql?: string;
  expectedImpact: string;
  relatedNodes?: string[];
}

/** 실행 계획 분석 결과 */
export interface PlanAnalysisResult {
  flattenedNodes: FlattenedNode[];
  costContributions: Map<string, CostContribution>;
  bottlenecks: BottleneckNode[];
  suggestions: OptimizationSuggestion[];
  totalCost: number;
  rootNodeType: string;
}
