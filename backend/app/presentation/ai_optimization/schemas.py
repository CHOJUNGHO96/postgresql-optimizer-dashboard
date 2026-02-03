"""AI 최적화 API 스키마."""

from typing import Any

from pydantic import BaseModel, Field


class OptimizeQueryRequest(BaseModel):
    """쿼리 최적화 요청 스키마."""

    ai_model: str = Field(
        description="사용할 AI 모델 (claude-3-5-sonnet-20241022, glm-4.5-flash, gemini-2.5-flash)"
    )
    validate_optimization: bool = Field(
        default=False, description="최적화 쿼리를 실제 실행하여 검증할지 여부"
    )
    include_schema_context: bool = Field(
        default=False, description="스키마 정보를 포함할지 여부"
    )


class OptimizationMetricsResponse(BaseModel):
    """최적화 메트릭 응답 스키마."""

    estimated_cost_reduction: float | None = Field(
        default=None, description="예상 비용 절감률 (%)"
    )
    estimated_time_reduction: float | None = Field(
        default=None, description="예상 시간 단축률 (%)"
    )
    optimized_total_cost: float | None = Field(
        default=None, description="최적화 쿼리 예상 총 비용"
    )
    optimized_execution_time_ms: float | None = Field(
        default=None, description="최적화 쿼리 실제 실행 시간 (ms)"
    )


class OptimizedQueryResponse(BaseModel):
    """최적화된 쿼리 응답 스키마."""

    id: str = Field(description="최적화 식별자")
    original_plan_id: str = Field(description="원본 쿼리 계획 ID")
    ai_model: str = Field(description="사용된 AI 모델")
    model_version: str | None = Field(default=None, description="모델 버전")
    optimized_query: str = Field(description="최적화된 SQL 쿼리")
    optimization_rationale: str = Field(description="최적화 근거 설명")
    optimization_category: str | None = Field(
        default=None, description="최적화 카테고리"
    )
    confidence_score: float = Field(description="AI 신뢰도 점수 (0.0-1.0)")
    metrics: OptimizationMetricsResponse = Field(description="최적화 성능 메트릭")
    applied_techniques: list[str] = Field(description="적용된 최적화 기법")
    changes_summary: dict[str, Any] | None = Field(
        default=None, description="변경사항 요약"
    )
    risk_assessment: str = Field(description="위험도 평가 (low/medium/high)")
    created_at: str = Field(description="생성 시각 (ISO 8601)")
