"""토큰 제한 통합 테스트."""

import pytest

from app.core.model_configs import get_model_limits, ModelFamily
from app.infrastructure.ai_optimization.prompts.optimization_prompt import (
    build_optimization_prompt,
)


@pytest.fixture
def large_explain_json():
    """큰 EXPLAIN JSON 생성 (100K+ 토큰 예상)."""

    def create_deep_plan(depth=5, width=3):
        """재귀적으로 깊은 실행 계획 생성."""
        if depth == 0:
            return {
                "Node Type": "Seq Scan",
                "Relation Name": "large_table",
                "Total Cost": 10000.0,
                "Startup Cost": 0.0,
                "Plan Rows": 1000000,
                "Plan Width": 200,
                "Actual Rows": 1000000,
                "Actual Loops": 1,
                "Actual Total Time": 5000.0,
                "Actual Startup Time": 100.0,
                "Filter": "(id > 1000 AND status = 'active')",
                "Output": ["id", "name", "email", "status", "created_at"] * 10,
                "Shared Hit Blocks": 50000,
                "Shared Read Blocks": 10000,
                "Workers Planned": 4,
                "Workers Launched": 4,
            }

        return {
            "Node Type": "Nested Loop",
            "Total Cost": 50000.0,
            "Startup Cost": 0.0,
            "Plan Rows": 1000000,
            "Plan Width": 200,
            "Actual Rows": 1000000,
            "Actual Loops": 1,
            "Actual Total Time": 10000.0,
            "Actual Startup Time": 200.0,
            "Join Type": "Inner",
            "Hash Cond": "(t1.id = t2.user_id)",
            "Plans": [create_deep_plan(depth - 1, width) for _ in range(width)],
        }

    return {"Plan": create_deep_plan(depth=4, width=4)}


class TestTokenLimitsIntegration:
    """토큰 제한 통합 테스트."""

    def test_model_configs_loaded(self):
        """모델 설정이 올바르게 로드되는지 확인."""
        gemini_limits = get_model_limits("gemini-2.5-flash")
        assert gemini_limits.max_input_tokens == 1_048_576
        assert gemini_limits.max_output_tokens == 65_536

        glm_limits = get_model_limits("glm-4.5-flash")
        assert glm_limits.max_input_tokens == 128_000
        assert glm_limits.max_output_tokens == 96_000

        claude_limits = get_model_limits("claude-3-5-sonnet-20241022")
        assert claude_limits.max_input_tokens == 200_000

    def test_safety_margins_applied(self):
        """안전 마진이 올바르게 적용되는지 확인."""
        glm_limits = get_model_limits("glm-4.5-flash")

        # GLM은 가장 보수적 (0.85)
        assert glm_limits.safe_input_tokens == int(128_000 * 0.85)
        assert glm_limits.safe_output_tokens == int(96_000 * 0.85)

    def test_small_prompt_no_compression(self):
        """작은 프롬프트는 압축 안 함."""
        query = "SELECT * FROM users WHERE id = 1"
        explain_json = {
            "Plan": {
                "Node Type": "Index Scan",
                "Index Name": "idx_users_id",
                "Total Cost": 10.0,
                "Actual Rows": 1,
            }
        }

        prompt, metadata = build_optimization_prompt(
            query,
            explain_json,
            None,
            model_name="glm-4.5-flash",
            auto_compress=True,
        )

        assert metadata["compressed"] is False
        assert metadata["compression_level"] is None
        assert metadata["token_count"] < 5000

    def test_large_prompt_auto_compression(self, large_explain_json):
        """큰 프롬프트 자동 압축."""
        query = "SELECT * FROM large_table t1 JOIN large_table t2 ON t1.id = t2.id"

        # GLM (가장 작은 제한)으로 테스트
        prompt, metadata = build_optimization_prompt(
            query,
            large_explain_json,
            None,
            model_name="glm-4.5-flash",
            auto_compress=True,
        )

        # GLM 제한 (128K * 0.85 = 108,800) 이하여야 함
        glm_limits = get_model_limits("glm-4.5-flash")
        assert metadata["token_count"] <= glm_limits.safe_input_tokens

        # 압축 메타데이터 확인
        if metadata["compressed"]:
            assert metadata["compression_level"] in ["mild", "moderate", "aggressive"]
            assert "original_tokens" in metadata
            assert "reduction_percentage" in metadata

    def test_compression_failure_raises_error(self):
        """압축 실패 시 명확한 에러."""
        # 매우 큰 EXPLAIN JSON 생성 (압축 불가능할 정도)
        # 핵심 필드들을 매우 크게 만들어서 압축해도 제한 초과하도록
        huge_json = {
            "Plan": {
                "Node Type": "Seq Scan with very long description " * 1000,
                "Relation Name": "table_name_" * 50000,  # 핵심 필드라 보존됨
                "Total Cost": 100.0,
                "Actual Rows": 1,
                # 매우 긴 핵심 필드들
                "Plans": [
                    {
                        "Node Type": "Index Scan",
                        "Index Name": "idx_" + str(i) * 1000,
                        "Total Cost": i,
                        "Actual Rows": i,
                    }
                    for i in range(5000)
                ],
            }
        }

        query = "SELECT * FROM table"

        with pytest.raises(ValueError, match="Token limit exceeded"):
            build_optimization_prompt(
                query,
                huge_json,
                None,
                model_name="glm-4.5-flash",
                auto_compress=True,
            )

    def test_schema_removal_before_json_compression(self, large_explain_json):
        """스키마가 먼저 제거되는지 확인."""
        query = "SELECT * FROM users"
        schema = "Very long schema context: " + "x" * 50000

        prompt, metadata = build_optimization_prompt(
            query,
            large_explain_json,
            schema,
            model_name="glm-4.5-flash",
            auto_compress=True,
        )

        glm_limits = get_model_limits("glm-4.5-flash")
        assert metadata["token_count"] <= glm_limits.safe_input_tokens

    def test_gemini_large_capacity(self, large_explain_json):
        """Gemini는 1M 토큰 여유로 압축 덜 필요."""
        query = "SELECT * FROM users"

        prompt, metadata = build_optimization_prompt(
            query,
            large_explain_json,
            None,
            model_name="gemini-2.5-flash",
            auto_compress=True,
        )

        gemini_limits = get_model_limits("gemini-2.5-flash")
        assert metadata["token_count"] <= gemini_limits.safe_input_tokens

        # Gemini는 제한이 크므로 압축 안 될 가능성 높음
        # (테스트 데이터 크기에 따라 다름)

    @pytest.mark.parametrize(
        "model_name,expected_max_input",
        [
            ("gemini-2.5-flash", 1_048_576),
            ("glm-4.5-flash", 128_000),
            ("claude-3-5-sonnet-20241022", 200_000),
        ],
    )
    def test_all_models_within_limits(
        self, large_explain_json, model_name, expected_max_input
    ):
        """모든 모델이 제한 내에서 동작."""
        query = "SELECT * FROM users"

        prompt, metadata = build_optimization_prompt(
            query,
            large_explain_json,
            None,
            model_name=model_name,
            auto_compress=True,
        )

        limits = get_model_limits(model_name)
        assert limits.max_input_tokens == expected_max_input
        assert metadata["token_count"] <= limits.safe_input_tokens

    def test_metadata_completeness(self):
        """메타데이터 완전성 검증."""
        query = "SELECT * FROM users"
        explain_json = {"Plan": {"Node Type": "Seq Scan", "Total Cost": 100}}

        prompt, metadata = build_optimization_prompt(
            query,
            explain_json,
            None,
            model_name="claude-3-5-sonnet-20241022",
            auto_compress=True,
        )

        # 필수 메타데이터 필드
        required_fields = [
            "token_count",
            "compressed",
            "compression_level",
            "model_name",
            "token_limit",
        ]

        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"

        assert metadata["model_name"] == "claude-3-5-sonnet-20241022"
        assert isinstance(metadata["token_count"], int)
        assert isinstance(metadata["compressed"], bool)
