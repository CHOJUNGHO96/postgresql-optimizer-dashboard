"""Gemini (Google) AI 클라이언트."""

from google import genai
from google.genai import errors

from app.core.model_configs import get_model_limits
from app.infrastructure.ai_optimization.clients.base import BaseAIClient


class GeminiAIClient(BaseAIClient):
    """Gemini (Google) AI 클라이언트 구현."""

    def __init__(self, api_key: str, model_name: str, timeout: int = 60) -> None:
        """Gemini 클라이언트를 초기화한다.

        Args:
            api_key: Google AI API 키
            model_name: 모델명 (예: gemini-2.5-flash)
            timeout: API 호출 타임아웃 (초)
        """
        super().__init__(api_key, model_name, timeout)
        # Client 생성 (aio는 lazy하게 초기화)
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._aclient = None  # Lazy initialization

    async def _ensure_client(self):
        """Async client를 lazy하게 초기화한다.

        Note:
            Singleton 패턴에서 async context manager를 반복 사용하면
            httpx AsyncClient가 닫혀서 재사용 불가능한 문제를 해결한다.
            첫 호출 시 한 번만 초기화하고 이후 재사용한다.
        """
        if self._aclient is None:
            self._aclient = await self._client.aio.__aenter__()
        return self._aclient

    async def _call_api(self, prompt: str) -> str:
        """Gemini API를 호출한다.

        Note:
            새 google-genai SDK는 네이티브 async 지원 (.aio 사용)
            Context manager를 직접 사용하지 않고 lazy initialization으로
            연결을 재사용하여 Singleton 패턴과 호환되도록 한다.
        """
        try:
            # 모델별 출력 토큰 제한 동적 설정
            model_limits = get_model_limits(self._model_name)

            aclient = await self._ensure_client()
            response = await aclient.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "max_output_tokens": model_limits.safe_output_tokens,
                }
            )

            if response.text:
                return response.text
            raise ValueError("Empty response from Gemini API")

        except errors.APIError as e:
            # 404, 500 등 API 에러를 상위로 전파
            raise Exception(f"Gemini API error [{e.code}]: {e.message}") from e

    async def close(self) -> None:
        """애플리케이션 종료 시 리소스를 정리한다."""
        if self._aclient is not None:
            await self._client.aio.__aexit__(None, None, None)
            self._aclient = None
