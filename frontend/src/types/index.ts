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
