"""토큰 카운터 테스트."""

import json
import time
import pytest

from app.infrastructure.ai_optimization.utils.token_counter import (
    count_tokens,
    count_prompt_tokens,
)


class TestTokenCounter:
    """토큰 카운터 테스트."""

    def test_count_simple_text(self):
        """간단한 텍스트의 토큰 수 계산."""
        text = "Hello, world!"
        tokens = count_tokens(text)
        assert tokens > 0
        assert tokens < 10  # 짧은 문장

    def test_count_korean_text(self):
        """한글 텍스트의 토큰 수 계산."""
        text = "안녕하세요, 세계!"
        tokens = count_tokens(text)
        assert tokens > 0

    def test_count_json(self):
        """JSON 데이터의 토큰 수 계산."""
        data = {
            "name": "test",
            "value": 123,
            "nested": {"key": "value"},
        }
        text = json.dumps(data, ensure_ascii=False)
        tokens = count_tokens(text)
        assert tokens > 0

    def test_count_large_text_performance(self):
        """대용량 텍스트 처리 성능 테스트 (<50ms)."""
        # 10KB 텍스트 생성
        text = "Hello, world! " * 1000

        start = time.perf_counter()
        tokens = count_tokens(text)
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert tokens > 0
        assert elapsed < 50, f"Token counting took {elapsed:.2f}ms (expected <50ms)"

    def test_count_prompt_tokens(self):
        """전체 프롬프트 토큰 수 계산."""
        query = "SELECT * FROM users WHERE id = 1"
        explain_json = {
            "Plan": {
                "Node Type": "Seq Scan",
                "Relation Name": "users",
                "Total Cost": 100.0,
            }
        }
        schema = "Table users (id INT, name VARCHAR)"

        tokens = count_prompt_tokens(query, explain_json, schema)
        assert tokens > 0
        assert tokens > 100  # 프롬프트 템플릿 포함

    def test_count_prompt_tokens_without_schema(self):
        """스키마 없는 프롬프트 토큰 수 계산."""
        query = "SELECT * FROM users"
        explain_json = {"Plan": {"Node Type": "Seq Scan"}}

        tokens_with_schema = count_prompt_tokens(
            query, explain_json, "Schema info"
        )
        tokens_without = count_prompt_tokens(query, explain_json, None)

        assert tokens_without < tokens_with_schema

    def test_model_family_parameter(self):
        """모델 패밀리 파라미터 테스트."""
        text = "Hello, world!"

        tokens_anthropic = count_tokens(text, "anthropic")
        tokens_google = count_tokens(text, "google")

        # 현재는 모두 동일한 인코더 사용
        assert tokens_anthropic == tokens_google


@pytest.mark.parametrize(
    "text,expected_min,expected_max",
    [
        ("", 0, 1),
        ("x", 1, 2),
        ("Hello", 1, 3),
        ("Hello, world!", 3, 6),
        ("SELECT * FROM users", 3, 10),
    ],
)
def test_token_ranges(text, expected_min, expected_max):
    """다양한 텍스트의 토큰 범위 검증."""
    tokens = count_tokens(text)
    assert expected_min <= tokens <= expected_max
