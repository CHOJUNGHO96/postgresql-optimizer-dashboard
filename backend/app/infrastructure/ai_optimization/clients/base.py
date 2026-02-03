"""AI 클라이언트 기본 클래스."""

import asyncio
from typing import Any

from app.domain.ai_optimization.services import AbstractAIClientService
from app.infrastructure.ai_optimization.prompts.optimization_prompt import (
    build_optimization_prompt,
    parse_optimization_response,
)


class BaseAIClient(AbstractAIClientService):
    """AI 클라이언트 기본 구현."""

    def __init__(self, api_key: str, model_name: str, timeout: int = 30) -> None:
        """클라이언트를 초기화한다.

        Args:
            api_key: API 키
            model_name: 모델명
            timeout: 타임아웃 (초)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout

    async def optimize_query(
        self,
        original_query: str,
        explain_json: dict[str, Any],
        schema_context: str | None = None,
    ) -> dict[str, Any]:
        """쿼리를 최적화한다 (기본 구현)."""
        prompt = build_optimization_prompt(original_query, explain_json, schema_context)

        try:
            response_text = await asyncio.wait_for(
                self._call_api(prompt), timeout=self.timeout
            )
            result = parse_optimization_response(response_text)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"AI API call timed out after {self.timeout} seconds"
            )
        except Exception as e:
            raise Exception(f"AI API call failed: {str(e)}")

    async def _call_api(self, prompt: str) -> str:
        """API를 호출한다 (서브클래스에서 구현).

        Args:
            prompt: 프롬프트 텍스트

        Returns:
            AI 응답 텍스트

        Raises:
            NotImplementedError: 서브클래스에서 구현 필요
        """
        raise NotImplementedError("Subclass must implement _call_api method")

    def get_model_name(self) -> str:
        """모델명을 반환한다."""
        return self.model_name
