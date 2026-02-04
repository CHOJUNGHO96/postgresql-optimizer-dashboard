"""AI optimization test fixtures."""

from typing import Any
import pytest


@pytest.fixture
def sample_explain_json() -> dict[str, Any]:
    """샘플 EXPLAIN JSON 결과."""
    return {
        "Plan": {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Total Cost": 35.5,
            "Startup Cost": 0.0,
            "Plan Rows": 100,
            "Plan Width": 50,
        }
    }


@pytest.fixture
def sample_optimization_response() -> str:
    """샘플 AI 최적화 응답 (JSON 문자열)."""
    import json
    return json.dumps({
        "optimized_query": "SELECT id FROM users WHERE id = 1 LIMIT 1",
        "optimization_rationale": "Added LIMIT 1 to reduce result set size",
        "estimated_cost_reduction": 0.5,
        "confidence_score": 0.9,
        "optimization_category": "result_set_limiting",
        "applied_techniques": ["limit_clause"],
        "risk_assessment": "low"
    })
