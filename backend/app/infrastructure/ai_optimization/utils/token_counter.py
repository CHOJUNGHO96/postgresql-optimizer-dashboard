"""토큰 카운팅 유틸리티."""

import json
import tiktoken
from typing import Any


class TokenCounter:
    """토큰 카운터 (Singleton 패턴)."""

    _instance: "TokenCounter | None" = None
    _encoder: tiktoken.Encoding | None = None

    def __new__(cls) -> "TokenCounter":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def encoder(self) -> tiktoken.Encoding:
        """tiktoken 인코더 (캐싱)."""
        if self._encoder is None:
            # cl100k_base: GPT-4, Claude, Gemini 등 대부분 모델에서 사용
            self._encoder = tiktoken.get_encoding("cl100k_base")
        return self._encoder

    def count(self, text: str) -> int:
        """텍스트의 토큰 수 계산.

        Args:
            text: 토큰을 계산할 텍스트

        Returns:
            int: 토큰 수
        """
        return len(self.encoder.encode(text))


# Singleton 인스턴스
_counter = TokenCounter()


def count_tokens(text: str, model_family: str = "anthropic") -> int:
    """텍스트의 토큰 수 계산.

    Args:
        text: 토큰을 계산할 텍스트
        model_family: 모델 패밀리 (현재는 모두 동일한 인코더 사용)

    Returns:
        int: 토큰 수
    """
    return _counter.count(text)


def count_prompt_tokens(
    original_query: str,
    explain_json: dict[str, Any],
    schema_context: str | None,
    model_family: str = "anthropic",
) -> int:
    """프롬프트 전체의 토큰 수 추정.

    Args:
        original_query: 원본 SQL 쿼리
        explain_json: EXPLAIN JSON 결과
        schema_context: 스키마 컨텍스트 (옵션)
        model_family: 모델 패밀리

    Returns:
        int: 예상 토큰 수
    """
    # 1. 쿼리 토큰
    query_tokens = count_tokens(original_query, model_family)

    # 2. EXPLAIN JSON 토큰
    explain_str = json.dumps(explain_json, ensure_ascii=False)
    explain_tokens = count_tokens(explain_str, model_family)

    # 3. 스키마 컨텍스트 토큰
    schema_tokens = 0
    if schema_context:
        schema_tokens = count_tokens(schema_context, model_family)

    # 4. 프롬프트 템플릿 오버헤드 (약 1000 토큰)
    template_overhead = 1000

    total = query_tokens + explain_tokens + schema_tokens + template_overhead

    return total
