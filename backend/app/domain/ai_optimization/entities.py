"""AI 최적화 도메인 엔티티."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.ai_optimization.value_objects import (
    AIModel,
    ConfidenceScore,
    OptimizationMetrics,
    RiskLevel,
)


def _utcnow() -> datetime:
    """UTC 현재 시각을 반환한다."""
    return datetime.now(UTC)


class OptimizedQuery(BaseModel):
    """최적화된 쿼리 엔티티.

    AI 모델이 생성한 쿼리 최적화 결과를 표현하는 도메인 객체.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="최적화 식별자")
    original_plan_id: UUID = Field(description="원본 쿼리 계획 ID")
    ai_model: AIModel = Field(description="사용된 AI 모델")
    model_version: str | None = Field(default=None, description="모델 버전")
    optimized_query: str = Field(description="최적화된 SQL 쿼리")
    optimization_rationale: str = Field(description="최적화 근거 설명")
    optimization_category: str | None = Field(
        default=None, description="최적화 카테고리"
    )
    confidence_score: ConfidenceScore = Field(description="AI 신뢰도 점수")
    metrics: OptimizationMetrics = Field(description="최적화 성능 메트릭")
    applied_techniques: list[str] = Field(
        default_factory=list, description="적용된 최적화 기법"
    )
    changes_summary: dict[str, Any] | None = Field(
        default=None, description="변경사항 요약"
    )
    risk_assessment: RiskLevel = Field(
        default=RiskLevel.MEDIUM, description="위험도 평가"
    )
    created_at: datetime = Field(default_factory=_utcnow, description="생성 시각")
