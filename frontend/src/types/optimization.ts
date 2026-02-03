/**
 * AI 기반 쿼리 최적화 타입 정의
 */

export type AIModel =
  | 'claude-3-5-sonnet-20241022'
  | 'glm-4.5-flash'
  | 'gemini-2.5-flash';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface OptimizeQueryRequest {
  ai_model: AIModel;
  validate_optimization?: boolean;
  include_schema_context?: boolean;
}

export interface OptimizationMetrics {
  estimated_cost_reduction: number | null;
  estimated_time_reduction: number | null;
  optimized_total_cost: number | null;
  optimized_execution_time_ms: number | null;
}

export interface OptimizedQueryResponse {
  id: string;
  original_plan_id: string;
  ai_model: string;
  model_version: string | null;
  optimized_query: string;
  optimization_rationale: string;
  optimization_category: string | null;
  confidence_score: number;
  metrics: OptimizationMetrics;
  applied_techniques: string[];
  changes_summary: {
    before?: string;
    after?: string;
    key_changes?: string[];
  } | null;
  risk_assessment: RiskLevel;
  created_at: string;
}

export interface AIModelOption {
  value: AIModel;
  label: string;
  description: string;
  provider: string;
}

export const AI_MODEL_OPTIONS: AIModelOption[] = [
  {
    value: 'claude-3-5-sonnet-20241022',
    label: 'Claude 3.5 Sonnet',
    description: '가장 뛰어난 코드 이해 능력을 갖춘 모델',
    provider: 'Anthropic',
  },
  {
    value: 'glm-4.5-flash',
    label: 'GLM-4.5-Flash',
    description: '빠르고 효율적인 중국어 모델',
    provider: 'Zhipu AI',
  },
  {
    value: 'gemini-2.5-flash',
    label: 'Gemini 2.5 Flash',
    description: 'Google의 빠르고 효율적인 최신 모델',
    provider: 'Google',
  },
];
