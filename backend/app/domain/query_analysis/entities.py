"""쿼리 분석 도메인 엔티티."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.query_analysis.value_objects import CostEstimate, PlanNodeType


def _utcnow() -> datetime:
    """UTC 현재 시각을 반환한다."""
    return datetime.now(UTC)


class QueryPlan(BaseModel):
    """쿼리 실행 계획 엔티티.

    PostgreSQL EXPLAIN 결과를 구조화한 도메인 객체.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="고유 식별자")
    query: str = Field(description="분석 대상 SQL 쿼리")
    title: str | None = Field(default=None, description="쿼리 제목")
    plan_raw: dict[str, Any] = Field(description="EXPLAIN JSON 원본 결과")
    node_type: PlanNodeType = Field(description="최상위 노드 유형")
    cost_estimate: CostEstimate = Field(description="비용 추정치")
    execution_time_ms: float | None = Field(default=None, description="실제 실행 시간(ms)")
    created_at: datetime = Field(default_factory=_utcnow, description="생성 시각")
