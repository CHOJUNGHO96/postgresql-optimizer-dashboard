"""테스트 공통 fixture."""

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.query_analysis.entities import QueryPlan
from app.domain.query_analysis.repositories import AbstractQueryAnalysisRepository
from app.domain.query_analysis.value_objects import CostEstimate, PlanNodeType


@pytest.fixture
def sample_explain_result() -> list[dict[str, Any]]:
    """샘플 EXPLAIN JSON 결과를 반환한다."""
    return [
        {
            "Plan": {
                "Node Type": "Seq Scan",
                "Relation Name": "users",
                "Alias": "users",
                "Startup Cost": 0.0,
                "Total Cost": 35.5,
                "Plan Rows": 10,
                "Plan Width": 244,
            },
            "Execution Time": 0.125,
        }
    ]


@pytest.fixture
def sample_query_plan() -> QueryPlan:
    """샘플 쿼리 실행 계획 엔티티를 반환한다."""
    return QueryPlan(
        id=uuid4(),
        query="SELECT * FROM users WHERE id = 1",
        plan_raw={
            "Plan": {
                "Node Type": "Seq Scan",
                "Startup Cost": 0.0,
                "Total Cost": 35.5,
                "Plan Rows": 10,
                "Plan Width": 244,
            }
        },
        node_type=PlanNodeType.SEQ_SCAN,
        cost_estimate=CostEstimate(
            startup_cost=0.0,
            total_cost=35.5,
            plan_rows=10,
            plan_width=244,
        ),
        execution_time_ms=0.125,
    )


@pytest.fixture
def mock_repository(sample_query_plan: QueryPlan, sample_explain_result: list[dict]) -> AsyncMock:
    """목 리포지토리를 반환한다."""
    mock = AsyncMock(spec=AbstractQueryAnalysisRepository)
    mock.analyze_query.return_value = sample_explain_result
    mock.save.return_value = sample_query_plan
    mock.find_by_id.return_value = sample_query_plan
    mock.find_all.return_value = [sample_query_plan]
    return mock
