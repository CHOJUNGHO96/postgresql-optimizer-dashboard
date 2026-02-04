"""AI 최적화 도메인 엔티티."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.ai_optimization.value_objects import (
    AIModel,
    ConfidenceScore,
    OptimizationMetrics,
    RiskLevel,
)


class TaskStatus(str, Enum):
    """최적화 작업 상태."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


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


class OptimizationTask(BaseModel):
    """최적화 작업 엔티티.

    백그라운드에서 실행되는 쿼리 최적화 작업을 추적.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="작업 식별자")
    plan_id: UUID = Field(description="원본 쿼리 계획 ID")
    ai_model: AIModel = Field(description="사용할 AI 모델")
    validate_optimization: bool = Field(default=False, description="최적화 검증 여부")
    include_schema_context: bool = Field(default=False, description="스키마 컨텍스트 포함 여부")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="작업 상태")
    optimization_id: UUID | None = Field(default=None, description="완료된 최적화 ID")
    error_message: str | None = Field(default=None, description="에러 메시지")
    error_type: str | None = Field(default=None, description="에러 타입")
    created_at: datetime = Field(default_factory=_utcnow, description="생성 시각")
    started_at: datetime | None = Field(default=None, description="시작 시각")
    completed_at: datetime | None = Field(default=None, description="완료 시각")
    estimated_duration_seconds: int | None = Field(default=None, description="예상 소요 시간(초)")

    def mark_as_processing(self) -> None:
        """작업을 처리 중 상태로 변경한다."""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot process task with status {self.status}")
        self.status = TaskStatus.PROCESSING
        self.started_at = _utcnow()

    def mark_as_completed(self, optimization_id: UUID) -> None:
        """작업을 완료 상태로 변경한다."""
        if self.status != TaskStatus.PROCESSING:
            raise ValueError(f"Cannot complete task with status {self.status}")
        self.status = TaskStatus.COMPLETED
        self.optimization_id = optimization_id
        self.completed_at = _utcnow()

    def mark_as_failed(self, error_message: str, error_type: str = "unexpected") -> None:
        """작업을 실패 상태로 변경한다."""
        if self.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            raise ValueError(f"Cannot fail task with status {self.status}")
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.error_type = error_type
        self.completed_at = _utcnow()
