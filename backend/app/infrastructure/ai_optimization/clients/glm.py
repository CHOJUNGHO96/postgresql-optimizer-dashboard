"""GLM (Z.ai) 클라이언트."""

from zhipuai import ZhipuAI

from app.infrastructure.ai_optimization.clients.base import BaseAIClient


class GLMAIClient(BaseAIClient):
    """GLM (Z.ai) 클라이언트 구현."""

    def __init__(self, api_key: str, model_name: str, timeout: int = 30) -> None:
        """GLM 클라이언트를 초기화한다.

        Args:
            api_key: ZhipuAI API 키
            model_name: 모델명 (예: glm-4.5-flash, glm-4.7, glm-4.6)
            timeout: API 호출 타임아웃 (초, SDK에 전달됨)
        """
        super().__init__(api_key, model_name, timeout)
        # ZhipuAI SDK에 timeout 전달 + 재시도 비활성화
        self.client = ZhipuAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=0  # 재시도 비활성화
        )

    async def _call_api(self, prompt: str) -> str:
        """GLM API를 호출한다."""
        # GLM SDK는 동기 API만 제공하므로 asyncio.to_thread 사용
        import asyncio

        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        raise ValueError("Empty response from GLM API")
