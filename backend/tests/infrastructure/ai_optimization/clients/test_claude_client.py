"""Claude AI 클라이언트 회귀 테스트."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.ai_optimization.clients.claude import ClaudeAIClient


class TestClaudeAIClient:
    """Claude AI 클라이언트 회귀 테스트 - 기존 기능이 정상 작동하는지 확인."""

    @pytest.mark.asyncio
    async def test_성공적인_API_호출(self, sample_explain_json: dict[str, Any], sample_optimization_response: str):
        """Claude 정상 동작 확인."""
        with patch('app.infrastructure.ai_optimization.clients.claude.AsyncAnthropic') as MockAsyncAnthropic:
            # Mock response
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text=sample_optimization_response)]

            mock_client = MagicMock()
            mock_client.messages.create = AsyncMock(return_value=mock_message)
            MockAsyncAnthropic.return_value = mock_client

            client = ClaudeAIClient(
                api_key="test-key",
                model_name="claude-3-5-sonnet-20241022",
                timeout=30
            )

            result = await client.optimize_query(
                original_query="SELECT * FROM users",
                explain_json=sample_explain_json
            )

            # Verify result
            assert result is not None
            assert "optimized_query" in result
            assert result["optimized_query"] == "SELECT id FROM users WHERE id = 1 LIMIT 1"
            assert result["confidence_score"] == 0.9

            # Verify API call
            mock_client.messages.create.assert_called_once()
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
            assert call_kwargs["max_tokens"] > 0

    @pytest.mark.asyncio
    async def test_타임아웃_처리(self, sample_explain_json: dict[str, Any]):
        """타임아웃 확인."""
        with patch('app.infrastructure.ai_optimization.clients.claude.AsyncAnthropic') as MockAsyncAnthropic:
            mock_client = MagicMock()

            async def slow_create(*args, **kwargs):
                import asyncio
                await asyncio.sleep(5)  # 1초 타임아웃 초과

            mock_client.messages.create = AsyncMock(side_effect=slow_create)
            MockAsyncAnthropic.return_value = mock_client

            client = ClaudeAIClient(
                api_key="test-key",
                model_name="claude-3-5-sonnet-20241022",
                timeout=1
            )

            with pytest.raises(TimeoutError) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            assert "timed out after 1 seconds" in str(exc_info.value)

    def test_모델명_반환(self):
        """get_model_name() 메서드 확인."""
        with patch('app.infrastructure.ai_optimization.clients.claude.AsyncAnthropic'):
            client = ClaudeAIClient(
                api_key="test-key",
                model_name="claude-3-5-sonnet-20241022",
                timeout=30
            )
            assert client.get_model_name() == "claude-3-5-sonnet-20241022"
