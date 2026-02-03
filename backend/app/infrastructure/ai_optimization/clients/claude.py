"""Claude AI 클라이언트."""

from anthropic import AsyncAnthropic

from app.infrastructure.ai_optimization.clients.base import BaseAIClient


class ClaudeAIClient(BaseAIClient):
    """Claude (Anthropic) AI 클라이언트 구현."""

    def __init__(self, api_key: str, model_name: str, timeout: int = 30) -> None:
        """Claude 클라이언트를 초기화한다."""
        super().__init__(api_key, model_name, timeout)
        self.client = AsyncAnthropic(
            api_key=api_key,
            max_retries=0,  # 재시도 비활성화
            timeout=timeout
        )

    async def _call_api(self, prompt: str) -> str:
        """Claude API를 호출한다."""
        message = await self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response
        if message.content and len(message.content) > 0:
            return message.content[0].text
        raise ValueError("Empty response from Claude API")
