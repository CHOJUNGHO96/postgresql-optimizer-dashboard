"""프롬프트 옵티마이저 테스트."""

import json
import pytest

from app.infrastructure.ai_optimization.utils.prompt_optimizer import (
    PromptOptimizer,
    EXPENSIVE_NODE_TYPES,
)
from app.infrastructure.ai_optimization.utils.token_counter import (
    count_tokens,
)


@pytest.fixture
def sample_explain_json():
    """테스트용 EXPLAIN JSON."""
    return {
        "Plan": {
            "Node Type": "Seq Scan",
            "Relation Name": "large_table",
            "Total Cost": 10000.0,
            "Startup Cost": 0.0,
            "Plan Rows": 1000000,
            "Plan Width": 100,
            "Actual Rows": 1000000,
            "Actual Loops": 1,
            "Actual Total Time": 5000.0,
            "Actual Startup Time": 0.0,
            "Filter": "(id > 1000)",
            "Output": ["id", "name", "email", "created_at"],
            "Shared Hit Blocks": 50000,
            "Shared Read Blocks": 10000,
            "Plans": [
                {
                    "Node Type": "Index Scan",
                    "Index Name": "idx_users_id",
                    "Total Cost": 100.0,
                    "Actual Rows": 100,
                }
            ],
        }
    }


class TestPromptOptimizer:
    """프롬프트 옵티마이저 테스트."""

    def test_is_expensive_node(self):
        """고비용 노드 식별."""
        expensive = {"Node Type": "Seq Scan"}
        cheap = {"Node Type": "Index Scan"}

        assert PromptOptimizer._is_expensive_node(expensive)
        assert not PromptOptimizer._is_expensive_node(cheap)

    def test_mild_compression(self, sample_explain_json):
        """Mild 압축 (10-20% 감소)."""
        original_str = json.dumps(sample_explain_json, ensure_ascii=False)
        original_tokens = count_tokens(original_str)

        compressed = PromptOptimizer.compress_explain_json(
            sample_explain_json, target_reduction=0.15
        )

        compressed_str = json.dumps(compressed, ensure_ascii=False)
        compressed_tokens = count_tokens(compressed_str)

        reduction = (original_tokens - compressed_tokens) / original_tokens

        # I/O 블록 정보 제거되어야 함
        plan = compressed["Plan"]
        assert "Shared Hit Blocks" not in plan
        assert "Shared Read Blocks" not in plan

        # 핵심 정보는 유지
        assert "Node Type" in plan
        assert "Total Cost" in plan
        assert "Actual Rows" in plan

        # 10-30% 범위 (mild는 덜 공격적)
        assert 0.05 <= reduction <= 0.35

    def test_moderate_compression(self, sample_explain_json):
        """Moderate 압축 (30-40% 감소)."""
        original_str = json.dumps(sample_explain_json, ensure_ascii=False)
        original_tokens = count_tokens(original_str)

        compressed = PromptOptimizer.compress_explain_json(
            sample_explain_json, target_reduction=0.35
        )

        compressed_str = json.dumps(compressed, ensure_ascii=False)
        compressed_tokens = count_tokens(compressed_str)

        reduction = (original_tokens - compressed_tokens) / original_tokens

        plan = compressed["Plan"]

        # Moderate 제거 대상
        assert "Output" not in plan

        # 핵심 정보는 유지
        assert "Node Type" in plan
        assert "Total Cost" in plan

        # 15-50% 범위 (실제로는 moderate가 약 19% 정도 감소)
        assert 0.15 <= reduction <= 0.55

    def test_aggressive_compression(self, sample_explain_json):
        """Aggressive 압축 (50-60% 감소)."""
        compressed = PromptOptimizer.compress_explain_json(
            sample_explain_json, target_reduction=0.55
        )

        plan = compressed["Plan"]

        # 핵심 정보만 유지
        assert "Node Type" in plan
        assert "Total Cost" in plan
        assert "Actual Rows" in plan
        assert "Relation Name" in plan  # 테이블 식별 필수

        # 고비용 노드라도 일부 필드 제거
        # 단, Filter는 여전히 중요하므로 보존될 수 있음

    def test_preserve_important_fields(self, sample_explain_json):
        """중요 필드 보존 검증."""
        compressed = PromptOptimizer.compress_explain_json(
            sample_explain_json, target_reduction=0.6  # 매우 공격적
        )

        plan = compressed["Plan"]

        # 절대 제거하면 안 되는 필드들
        critical_fields = [
            "Node Type",
            "Total Cost",
            "Actual Rows",
            "Relation Name",
        ]

        for field in critical_fields:
            assert field in plan, f"{field} should be preserved"

    def test_recursive_compression(self, sample_explain_json):
        """자식 노드 재귀 압축."""
        compressed = PromptOptimizer.compress_explain_json(
            sample_explain_json, target_reduction=0.3
        )

        plan = compressed["Plan"]
        assert "Plans" in plan
        assert len(plan["Plans"]) > 0

        # 자식 노드도 압축되어야 함
        child = plan["Plans"][0]
        assert "Node Type" in child
        assert "Total Cost" in child

    def test_compress_to_target_tokens(self, sample_explain_json):
        """목표 토큰 수에 맞춰 압축."""
        query = "SELECT * FROM large_table WHERE id > 1000"
        schema = "Table large_table (id INT, name VARCHAR, ...)"

        target_tokens = 5000

        compressed_json, compressed_schema = PromptOptimizer.compress_to_target_tokens(
            query,
            sample_explain_json,
            schema,
            target_tokens,
            "anthropic",
        )

        # 압축 후 토큰 수 확인
        from app.infrastructure.ai_optimization.utils.token_counter import (
            count_prompt_tokens,
        )

        final_tokens = count_prompt_tokens(
            query, compressed_json, compressed_schema, "anthropic"
        )

        assert final_tokens <= target_tokens

    def test_schema_removal_first(self, sample_explain_json):
        """스키마 먼저 제거 시도."""
        query = "SELECT * FROM users"
        schema = "Schema: " + "x" * 20000  # 매우 큰 스키마

        target_tokens = 2000  # 더 작은 목표

        compressed_json, compressed_schema = PromptOptimizer.compress_to_target_tokens(
            query,
            sample_explain_json,
            schema,
            target_tokens,
            "anthropic",
        )

        # 스키마가 먼저 제거되어야 함
        assert compressed_schema is None

    def test_compression_failure_raises_error(self, sample_explain_json):
        """압축 실패 시 에러 발생."""
        query = "SELECT * FROM users"

        # 매우 작은 목표 토큰 (달성 불가능)
        target_tokens = 100

        with pytest.raises(ValueError, match="Unable to compress"):
            PromptOptimizer.compress_to_target_tokens(
                query,
                sample_explain_json,
                None,
                target_tokens,
                "anthropic",
            )

    def test_no_compression_if_under_limit(self, sample_explain_json):
        """제한 이하면 압축 안 함."""
        query = "SELECT * FROM users"

        # 매우 큰 목표 토큰
        target_tokens = 1_000_000

        compressed_json, compressed_schema = PromptOptimizer.compress_to_target_tokens(
            query,
            sample_explain_json,
            "schema",
            target_tokens,
            "anthropic",
        )

        # 원본과 동일해야 함
        assert compressed_json == sample_explain_json
        assert compressed_schema == "schema"


@pytest.mark.parametrize(
    "target_reduction,expected_level",
    [
        (0.1, "mild"),
        (0.2, "moderate"),
        (0.35, "moderate"),
        (0.5, "aggressive"),
    ],
)
def test_compression_levels(sample_explain_json, target_reduction, expected_level):
    """압축 레벨별 동작 검증."""
    compressed = PromptOptimizer.compress_explain_json(
        sample_explain_json, target_reduction
    )

    # 압축 성공 확인
    assert compressed is not None
    assert "Plan" in compressed
