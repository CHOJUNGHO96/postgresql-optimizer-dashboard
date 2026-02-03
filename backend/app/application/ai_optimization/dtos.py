"""AI 최적화 DTO (Data Transfer Objects)."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class OptimizeQueryInput(BaseModel):
    """쿼리 최적화 입력 DTO."""

    plan_id: UUID = Field(description="원본 쿼리 계획 ID")
    ai_model: str = Field(description="사용할 AI 모델")
    validate_optimization: bool = Field(
        default=False, description="최적화 쿼리를 실제 실행하여 검증할지 여부"
    )
    include_schema_context: bool = Field(
        default=False, description="스키마 정보를 포함할지 여부"
    )


class OptimizationMetricsOutput(BaseModel):
    """최적화 메트릭 출력 DTO."""

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


class OptimizeQueryOutput(BaseModel):
    """쿼리 최적화 출력 DTO."""

    id: UUID = Field(description="최적화 식별자")
    original_plan_id: UUID = Field(description="원본 쿼리 계획 ID")
    ai_model: str = Field(description="사용된 AI 모델")
    model_version: str | None = Field(default=None, description="모델 버전")
    optimized_query: str = Field(description="최적화된 SQL 쿼리")
    optimization_rationale: str = Field(description="최적화 근거 설명")
    optimization_category: str | None = Field(
        default=None, description="최적화 카테고리"
    )
    confidence_score: float = Field(description="AI 신뢰도 점수 (0.0-1.0)")
    metrics: OptimizationMetricsOutput = Field(description="최적화 성능 메트릭")
    applied_techniques: list[str] = Field(description="적용된 최적화 기법")
    changes_summary: dict[str, Any] | None = Field(
        default=None, description="변경사항 요약"
    )
    risk_assessment: str = Field(description="위험도 평가 (low/medium/high)")
    created_at: str = Field(description="생성 시각 (ISO 8601)")

    @classmethod
    def from_entity(cls, entity: Any) -> "OptimizeQueryOutput":
        """도메인 엔티티로부터 DTO를 생성한다."""
        return cls(
            id=entity.id,
            original_plan_id=entity.original_plan_id,
            ai_model=entity.ai_model.value,
            model_version=entity.model_version,
            optimized_query=entity.optimized_query,
            optimization_rationale=entity.optimization_rationale,
            optimization_category=entity.optimization_category,
            confidence_score=entity.confidence_score.value,
            metrics=OptimizationMetricsOutput(
                estimated_cost_reduction=entity.metrics.estimated_cost_reduction,
                estimated_time_reduction=entity.metrics.estimated_time_reduction,
                optimized_total_cost=entity.metrics.optimized_total_cost,
                optimized_execution_time_ms=entity.metrics.optimized_execution_time_ms,
            ),
            applied_techniques=entity.applied_techniques,
            changes_summary=entity.changes_summary,
            risk_assessment=entity.risk_assessment.value,
            created_at=entity.created_at.isoformat(),
        )
