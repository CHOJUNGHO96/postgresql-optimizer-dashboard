"""쿼리 분석 요청/응답 스키마.

Presentation 계층에서 사용하는 Pydantic 스키마.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyzeQueryRequest(BaseModel):
    """쿼리 분석 요청 스키마."""

    query: str = Field(min_length=1, description="분석할 SQL 쿼리", examples=["SELECT * FROM users WHERE id = 1"])
    title: str | None = Field(default=None, max_length=255, description="쿼리 제목", examples=["사용자 조회"])


class AnalyzePlanRequest(BaseModel):
    """EXPLAIN JSON 직접 분석 요청 스키마."""

    plan_json: dict[str, Any] | list[dict[str, Any]] = Field(
        description="EXPLAIN (FORMAT JSON) 결과",
        examples=[[{"Plan": {"Node Type": "Seq Scan", "Relation Name": "users"}}]],
    )
    title: str | None = Field(default=None, max_length=255, description="쿼리 제목")
    original_query: str | None = Field(default=None, description="원본 SQL 쿼리 (선택사항)")


class CostEstimateResponse(BaseModel):
    """비용 추정 응답 스키마."""

    startup_cost: float
    total_cost: float
    plan_rows: int
    plan_width: int


class QueryPlanResponse(BaseModel):
    """쿼리 실행 계획 응답 스키마."""

    id: UUID
    query: str
    title: str | None
    node_type: str
    cost_estimate: CostEstimateResponse
    execution_time_ms: float | None
    plan_raw: dict[str, Any]
    created_at: datetime


class QueryPlanListResponse(BaseModel):
    """쿼리 실행 계획 목록 응답 스키마."""

    items: list[QueryPlanResponse]
    total: int


class HealthResponse(BaseModel):
    """헬스체크 응답 스키마."""

    status: str = "ok"
