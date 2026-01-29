"""쿼리 분석 유스케이스 입출력 DTO."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.query_analysis.value_objects import CostEstimate, PlanNodeType


class AnalyzeQueryInput(BaseModel):
    """쿼리 분석 요청 DTO."""

    query: str = Field(min_length=1, description="분석할 SQL 쿼리")
    title: str | None = Field(default=None, max_length=255, description="쿼리 제목")


class AnalyzeQueryOutput(BaseModel):
    """쿼리 분석 결과 DTO."""

    id: UUID
    query: str
    title: str | None
    node_type: PlanNodeType
    cost_estimate: CostEstimate
    execution_time_ms: float | None
    plan_raw: dict[str, Any]
    created_at: datetime


class QueryPlanListOutput(BaseModel):
    """쿼리 분석 결과 목록 DTO."""

    items: list[AnalyzeQueryOutput]
    total: int
