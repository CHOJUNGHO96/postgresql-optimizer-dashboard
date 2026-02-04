"""AI 최적화 SQLAlchemy ORM 모델."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.ai_optimization.entities import OptimizedQuery, OptimizationTask, TaskStatus
from app.domain.ai_optimization.value_objects import (
    AIModel,
    ConfidenceScore,
    OptimizationMetrics,
    RiskLevel,
)


class OptimizedQueryModel(Base):
    """최적화된 쿼리 ORM 모델.

    AI 모델이 생성한 쿼리 최적화 결과를 저장.
    """

    __tablename__ = "optimized_queries"
    __table_args__ = (
        Index("ix_optimized_queries_original_plan_id", "original_plan_id"),
        Index("ix_optimized_queries_ai_model", "ai_model"),
        Index("ix_optimized_queries_created_at", "created_at"),
        Index("ix_optimized_queries_confidence_score", "confidence_score"),
        {"schema": "pgs_analysis", "comment": "AI 기반 쿼리 최적화 결과 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="최적화 식별자",
    )
    original_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pgs_analysis.query_plans.id", ondelete="CASCADE"),
        nullable=False,
        comment="원본 쿼리 계획 참조",
    )
    ai_model: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="사용된 AI 모델명"
    )
    model_version: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="모델 버전"
    )
    optimized_query: Mapped[str] = mapped_column(
        Text, nullable=False, comment="최적화된 SQL 쿼리"
    )
    optimization_rationale: Mapped[str] = mapped_column(
        Text, nullable=False, comment="최적화 근거 설명"
    )
    estimated_cost_reduction: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="예상 비용 절감률 (%)"
    )
    estimated_time_reduction: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="예상 시간 단축률 (%)"
    )
    optimized_total_cost: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="최적화 쿼리 예상 총 비용"
    )
    optimized_execution_time_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="최적화 쿼리 실제 실행 시간 (ms)"
    )
    optimization_category: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="최적화 카테고리"
    )
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="AI 신뢰도 점수 (0.0-1.0)"
    )
    applied_techniques: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="적용된 최적화 기법 목록"
    )
    changes_summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="변경사항 요약"
    )
    risk_assessment: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", comment="위험도 평가"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="생성 시각",
    )

    # Relationships
    original_plan: Mapped["QueryPlanModel"] = relationship(  # type: ignore[name-defined]
        "QueryPlanModel", foreign_keys=[original_plan_id]
    )

    def to_entity(self) -> OptimizedQuery:
        """ORM 모델을 도메인 엔티티로 변환한다."""
        return OptimizedQuery(
            id=self.id,
            original_plan_id=self.original_plan_id,
            ai_model=AIModel(self.ai_model),
            model_version=self.model_version,
            optimized_query=self.optimized_query,
            optimization_rationale=self.optimization_rationale,
            optimization_category=self.optimization_category,
            confidence_score=ConfidenceScore(value=self.confidence_score),
            metrics=OptimizationMetrics(
                estimated_cost_reduction=self.estimated_cost_reduction,
                estimated_time_reduction=self.estimated_time_reduction,
                optimized_total_cost=self.optimized_total_cost,
                optimized_execution_time_ms=self.optimized_execution_time_ms,
            ),
            applied_techniques=self.applied_techniques or [],
            changes_summary=self.changes_summary,
            risk_assessment=RiskLevel(self.risk_assessment),
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: OptimizedQuery) -> "OptimizedQueryModel":
        """도메인 엔티티를 ORM 모델로 변환한다."""
        return cls(
            id=entity.id,
            original_plan_id=entity.original_plan_id,
            ai_model=entity.ai_model.value,
            model_version=entity.model_version,
            optimized_query=entity.optimized_query,
            optimization_rationale=entity.optimization_rationale,
            optimization_category=entity.optimization_category,
            confidence_score=entity.confidence_score.value,
            estimated_cost_reduction=entity.metrics.estimated_cost_reduction,
            estimated_time_reduction=entity.metrics.estimated_time_reduction,
            optimized_total_cost=entity.metrics.optimized_total_cost,
            optimized_execution_time_ms=entity.metrics.optimized_execution_time_ms,
            applied_techniques=entity.applied_techniques,
            changes_summary=entity.changes_summary,
            risk_assessment=entity.risk_assessment.value,
            created_at=entity.created_at,
        )


class OptimizationTaskModel(Base):
    """최적화 작업 ORM 모델.

    백그라운드 쿼리 최적화 작업 추적용 테이블.
    """

    __tablename__ = "optimization_tasks"
    __table_args__ = (
        Index("idx_optimization_tasks_plan_id", "plan_id"),
        Index("idx_optimization_tasks_status", "status"),
        Index("idx_optimization_tasks_status_created", "status", "created_at"),
        {"schema": "pgs_analysis", "comment": "백그라운드 최적화 작업 추적 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="작업 식별자",
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pgs_analysis.query_plans.id", ondelete="CASCADE"),
        nullable=False,
        comment="원본 쿼리 계획 참조",
    )
    ai_model: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="사용할 AI 모델명"
    )
    validate_optimization: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="최적화 검증 여부"
    )
    include_schema_context: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="스키마 컨텍스트 포함 여부"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", comment="작업 상태"
    )
    optimization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pgs_analysis.optimized_queries.id", ondelete="SET NULL"),
        nullable=True,
        comment="완료된 최적화 참조",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="에러 메시지"
    )
    error_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="에러 타입"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="생성 시각",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="시작 시각",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="완료 시각",
    )
    estimated_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="예상 소요 시간(초)"
    )

    # Relationships
    plan: Mapped["QueryPlanModel"] = relationship(  # type: ignore[name-defined]
        "QueryPlanModel", foreign_keys=[plan_id]
    )
    optimization: Mapped["OptimizedQueryModel"] = relationship(  # type: ignore[name-defined]
        "OptimizedQueryModel", foreign_keys=[optimization_id]
    )

    def to_entity(self) -> OptimizationTask:
        """ORM 모델을 도메인 엔티티로 변환한다."""
        return OptimizationTask(
            id=self.id,
            plan_id=self.plan_id,
            ai_model=AIModel(self.ai_model),
            validate_optimization=self.validate_optimization,
            include_schema_context=self.include_schema_context,
            status=TaskStatus(self.status),
            optimization_id=self.optimization_id,
            error_message=self.error_message,
            error_type=self.error_type,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            estimated_duration_seconds=self.estimated_duration_seconds,
        )

    @classmethod
    def from_entity(cls, entity: OptimizationTask) -> "OptimizationTaskModel":
        """도메인 엔티티를 ORM 모델로 변환한다."""
        return cls(
            id=entity.id,
            plan_id=entity.plan_id,
            ai_model=entity.ai_model.value,
            validate_optimization=entity.validate_optimization,
            include_schema_context=entity.include_schema_context,
            status=entity.status.value,
            optimization_id=entity.optimization_id,
            error_message=entity.error_message,
            error_type=entity.error_type,
            created_at=entity.created_at,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            estimated_duration_seconds=entity.estimated_duration_seconds,
        )
