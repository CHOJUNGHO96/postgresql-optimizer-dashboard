"""AI 클라이언트 기본 클래스."""

import asyncio
import logging
import time
from typing import Any

from app.core.model_configs import get_model_limits
from app.domain.ai_optimization.services import AbstractAIClientService
from app.infrastructure.ai_optimization.prompts.optimization_prompt import (
    build_optimization_prompt,
    parse_optimization_response,
)

logger = logging.getLogger(__name__)


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
        # 프롬프트 생성 (자동 압축 포함)
        prompt, metadata = build_optimization_prompt(
            original_query,
            explain_json,
            schema_context,
            model_name=self.model_name,
            auto_compress=True,
        )

        # 로깅
        logger.info(
            f"Prompt generated: {metadata['token_count']:,} tokens, "
            f"compressed={metadata['compressed']}, "
            f"model={metadata['model_name']}"
        )

        if metadata["compressed"]:
            logger.info(
                f"Compression applied: {metadata['compression_level']} level, "
                f"{metadata['original_tokens']:,} → {metadata['token_count']:,} tokens "
                f"({metadata['reduction_percentage']:.1f}% reduction)"
            )

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
            # 토큰 관련 에러 특별 처리
            error_msg = str(e).lower()
            if any(word in error_msg for word in ["token", "length", "limit", "exceeded"]):
                model_limits = get_model_limits(self.model_name)
                raise ValueError(
                    f"Token limit exceeded for {self.model_name}. "
                    f"Max input: {model_limits.max_input_tokens:,} tokens. "
                    f"Current request: {metadata['token_count']:,} tokens."
                ) from e
            raise Exception(f"AI API call failed: {str(e)}")

    async def optimize_query_with_retry(
        self,
        original_query: str,
        explain_json: dict[str, Any],
        schema_context: str | None = None,
        max_retries: int = 2,
    ) -> dict[str, Any]:
        """재시도 로직이 포함된 쿼리 최적화.

        Args:
            original_query: 원본 SQL 쿼리
            explain_json: EXPLAIN JSON 결과
            schema_context: 스키마 컨텍스트 (선택)
            max_retries: 최대 재시도 횟수 (기본: 2회, 총 3번 시도)

        Returns:
            최적화 결과

        Raises:
            TimeoutError: 모든 재시도 후에도 타임아웃 발생
            Exception: 기타 에러
        """
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                logger.info(
                    f"AI optimization attempt {attempt + 1}/{max_retries + 1} "
                    f"(model: {self.model_name}, timeout: {self.timeout}s)"
                )

                result = await self.optimize_query(
                    original_query, explain_json, schema_context
                )

                elapsed = time.time() - start_time
                logger.info(
                    f"AI optimization succeeded in {elapsed:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                return result

            except TimeoutError:
                elapsed = time.time() - start_time
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s
                    logger.warning(
                        f"Timeout after {elapsed:.1f}s on attempt {attempt + 1}/{max_retries + 1}. "
                        f"Retrying in {wait_time}s... "
                        f"(model: {self.model_name}, timeout: {self.timeout}s)"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"All retry attempts exhausted. "
                        f"Final timeout after {elapsed:.1f}s "
                        f"(model: {self.model_name}, timeout: {self.timeout}s, "
                        f"attempts: {max_retries + 1})"
                    )
                    raise
            except Exception as e:
                # 다른 에러는 재시도하지 않고 즉시 실패
                logger.error(
                    f"AI optimization failed with non-timeout error: {str(e)} "
                    f"(model: {self.model_name}, attempt: {attempt + 1})"
                )
                raise

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
