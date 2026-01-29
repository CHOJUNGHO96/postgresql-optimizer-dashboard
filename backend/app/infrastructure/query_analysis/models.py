"""쿼리 분석 SQLAlchemy ORM 모델."""

import hashlib
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.query_analysis.entities import QueryPlan
from app.domain.query_analysis.value_objects import CostEstimate, PlanNodeType


def compute_query_hash(query: str) -> str:
    """쿼리 텍스트를 정규화하고 SHA-256 해시를 생성한다.

    Args:
        query: 원본 SQL 쿼리

    Returns:
        64자 해시 문자열
    """
    normalized = " ".join(query.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


class AnalysisSessionModel(Base):
    """분석 세션 ORM 모델.

    쿼리 분석 작업을 논리적으로 그룹화하는 세션.
    """

    __tablename__ = "analysis_sessions"
    __table_args__ = (
        Index("ix_sessions_status", "status"),
        Index("ix_sessions_created_at", "created_at"),
        {"comment": "분석 세션 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="세션 식별자"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="세션 이름")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="세션 설명")
    target_database: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="분석 대상 DB명")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", comment="상태 (active/completed/archived)"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, comment="생성 시각")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시각"
    )

    # Relationships
    query_plans: Mapped[list["QueryPlanModel"]] = relationship("QueryPlanModel", back_populates="session", lazy="dynamic")


class QueryPlanModel(Base):
    """쿼리 실행 계획 ORM 모델.

    PostgreSQL EXPLAIN 결과를 저장하는 핵심 테이블.
    """

    __tablename__ = "query_plans"
    __table_args__ = (
        Index("ix_query_plans_session_id", "session_id"),
        Index("ix_query_plans_query_hash", "query_hash"),
        Index("ix_query_plans_created_at", "created_at"),
        Index("ix_query_plans_node_type", "node_type"),
        Index("ix_query_plans_total_cost", "total_cost"),
        {"comment": "쿼리 실행 계획 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="고유 식별자"
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_sessions.id", ondelete="SET NULL"), nullable=True, comment="분석 세션 참조"
    )
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="쿼리 해시 (SHA-256)")
    query: Mapped[str] = mapped_column(Text, nullable=False, comment="분석 대상 SQL")
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="쿼리 제목")
    plan_raw: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, comment="EXPLAIN JSON 원본")
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="최상위 노드 유형")
    startup_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="시작 비용")
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="총 비용")
    plan_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="예상 행 수")
    plan_width: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="예상 행 폭")
    actual_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True, comment="실제 실행 시간 (ms)")
    planning_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True, comment="계획 수립 시간 (ms)")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, comment="생성 시각")

    # Relationships
    session: Mapped["AnalysisSessionModel | None"] = relationship("AnalysisSessionModel", back_populates="query_plans")
    nodes: Mapped[list["QueryPlanNodeModel"]] = relationship(
        "QueryPlanNodeModel", back_populates="plan", cascade="all, delete-orphan", lazy="dynamic"
    )
    suggestions: Mapped[list["OptimizationSuggestionModel"]] = relationship(
        "OptimizationSuggestionModel", back_populates="plan", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_entity(self) -> QueryPlan:
        """ORM 모델을 도메인 엔티티로 변환한다."""
        try:
            node_type = PlanNodeType(self.node_type)
        except ValueError:
            node_type = PlanNodeType.OTHER

        return QueryPlan(
            id=self.id,
            query=self.query,
            title=self.title,
            plan_raw=self.plan_raw,
            node_type=node_type,
            cost_estimate=CostEstimate(
                startup_cost=self.startup_cost,
                total_cost=self.total_cost,
                plan_rows=self.plan_rows,
                plan_width=self.plan_width,
            ),
            execution_time_ms=self.actual_time_ms,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: QueryPlan, session_id: uuid.UUID | None = None) -> "QueryPlanModel":
        """도메인 엔티티를 ORM 모델로 변환한다.

        Args:
            entity: 도메인 엔티티
            session_id: 선택적 세션 ID
        """
        return cls(
            id=entity.id,
            session_id=session_id,
            query_hash=compute_query_hash(entity.query),
            query=entity.query,
            title=entity.title,
            plan_raw=entity.plan_raw,
            node_type=entity.node_type.value,
            startup_cost=entity.cost_estimate.startup_cost,
            total_cost=entity.cost_estimate.total_cost,
            plan_rows=entity.cost_estimate.plan_rows,
            plan_width=entity.cost_estimate.plan_width,
            actual_time_ms=entity.execution_time_ms,
            created_at=entity.created_at,
        )


class QueryPlanNodeModel(Base):
    """쿼리 실행 계획 노드 ORM 모델.

    쿼리 실행 계획의 계층적 노드 구조를 저장.
    Self-referencing으로 부모-자식 관계를 표현한다.
    """

    __tablename__ = "query_plan_nodes"
    __table_args__ = (
        Index("ix_plan_nodes_plan_id", "plan_id"),
        Index("ix_plan_nodes_parent_node_id", "parent_node_id"),
        Index("ix_plan_nodes_node_type", "node_type"),
        {"comment": "실행 계획 노드 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="노드 식별자"
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("query_plans.id", ondelete="CASCADE"), nullable=False, comment="상위 계획 참조"
    )
    parent_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("query_plan_nodes.id", ondelete="CASCADE"), nullable=True, comment="부모 노드 (self-reference)"
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="트리 깊이")
    node_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="동일 깊이 내 순서")
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="노드 유형")
    relation_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="대상 테이블/인덱스명")
    startup_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="노드 시작 비용")
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="노드 총 비용")
    plan_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="예상 행 수")
    actual_rows: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="실제 행 수")
    loops: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="반복 횟수")
    node_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, comment="노드 추가 데이터")

    # Relationships
    plan: Mapped["QueryPlanModel"] = relationship("QueryPlanModel", back_populates="nodes")
    parent: Mapped["QueryPlanNodeModel | None"] = relationship(
        "QueryPlanNodeModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["QueryPlanNodeModel"]] = relationship(
        "QueryPlanNodeModel", back_populates="parent", cascade="all, delete-orphan"
    )


class OptimizationSuggestionModel(Base):
    """최적화 제안 ORM 모델.

    쿼리 실행 계획 분석 결과로 생성된 최적화 제안을 저장.
    """

    __tablename__ = "optimization_suggestions"
    __table_args__ = (
        Index("ix_suggestions_plan_id", "plan_id"),
        Index("ix_suggestions_severity", "severity"),
        {"comment": "최적화 제안 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="제안 식별자"
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("query_plans.id", ondelete="CASCADE"), nullable=False, comment="관련 계획"
    )
    suggestion_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="제안 유형")
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info", comment="심각도 (info/warning/critical)")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="제안 제목")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="상세 설명")
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True, comment="권장 조치")
    estimated_improvement: Mapped[float | None] = mapped_column(Float, nullable=True, comment="예상 개선율 (%)")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, comment="생성 시각")

    # Relationships
    plan: Mapped["QueryPlanModel"] = relationship("QueryPlanModel", back_populates="suggestions")


class QueryStatisticsModel(Base):
    """쿼리 통계 집계 ORM 모델.

    동일 쿼리의 실행 통계를 집계하여 저장.
    """

    __tablename__ = "query_statistics"
    __table_args__ = (
        Index("ix_statistics_query_hash", "query_hash", unique=True),
        Index("ix_statistics_avg_time_ms", "avg_time_ms"),
        {"comment": "쿼리 통계 집계 테이블"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="통계 식별자"
    )
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, comment="쿼리 해시")
    call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="호출 횟수")
    total_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="총 실행 시간 (ms)")
    min_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="최소 실행 시간 (ms)")
    max_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="최대 실행 시간 (ms)")
    avg_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="평균 실행 시간 (ms)")
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, comment="최초 발견 시각")
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, comment="최근 발견 시각")

    def update_statistics(self, execution_time_ms: float) -> None:
        """실행 시간으로 통계를 업데이트한다.

        Args:
            execution_time_ms: 새 실행 시간 (ms)
        """
        self.call_count += 1
        self.total_time_ms += execution_time_ms
        self.min_time_ms = min(self.min_time_ms, execution_time_ms)
        self.max_time_ms = max(self.max_time_ms, execution_time_ms)
        self.avg_time_ms = self.total_time_ms / self.call_count
        self.last_seen = datetime.utcnow()
