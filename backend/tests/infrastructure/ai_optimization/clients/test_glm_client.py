"""GLM AI 클라이언트 테스트."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.ai_optimization.clients.glm import GLMAIClient


class TestGLMAIClient:
    """GLM AI 클라이언트 테스트."""

    def test_클라이언트_초기화_시_타임아웃_전달(self):
        """타임아웃이 ZhipuAI SDK에 전달되는지 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            client = GLMAIClient(
                api_key="test-key",
                model_name="glm-4.5-flash",
                timeout=60
            )

            # ZhipuAI 생성자에 timeout과 max_retries 전달 확인
            MockZhipuAI.assert_called_once_with(
                api_key="test-key",
                timeout=60,
                max_retries=0
            )
            assert client.timeout == 60
            assert client.model_name == "glm-4.5-flash"

    @pytest.mark.asyncio
    async def test_성공적인_API_호출(self, sample_explain_json: dict[str, Any], sample_optimization_response: str):
        """정상 응답 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            # Mock response
            mock_message = MagicMock()
            mock_message.content = sample_optimization_response

            mock_choice = MagicMock()
            mock_choice.message = mock_message

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockZhipuAI.return_value = mock_client

            client = GLMAIClient(api_key="test-key", model_name="glm-4.5-flash", timeout=30)

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
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "glm-4.5-flash"
            assert len(call_kwargs["messages"]) > 0

    @pytest.mark.asyncio
    async def test_타임아웃_처리(self, sample_explain_json: dict[str, Any]):
        """타임아웃 시 TimeoutError 발생 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            mock_client = MagicMock()

            def slow_create(*args, **kwargs):
                import time
                time.sleep(5)  # 1초 타임아웃 초과

            mock_client.chat.completions.create.side_effect = slow_create
            MockZhipuAI.return_value = mock_client

            client = GLMAIClient(api_key="test-key", model_name="glm-4", timeout=1)

            with pytest.raises(TimeoutError) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            assert "timed out after 1 seconds" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_404_모델_없음_오류(self, sample_explain_json: dict[str, Any]):
        """잘못된 모델명 오류 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            mock_client = MagicMock()

            # Simulate 404-like error
            mock_client.chat.completions.create.side_effect = Exception("Model not found: GLM-4.7-Flash")
            MockZhipuAI.return_value = mock_client

            client = GLMAIClient(api_key="test-key", model_name="GLM-4.7-Flash", timeout=30)

            with pytest.raises(Exception) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            assert "Model not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_빈_응답_처리(self, sample_explain_json: dict[str, Any]):
        """빈 choices 리스트 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            # Mock empty response
            mock_response = MagicMock()
            mock_response.choices = []

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockZhipuAI.return_value = mock_client

            client = GLMAIClient(api_key="test-key", model_name="glm-4.5-flash", timeout=30)

            with pytest.raises(Exception) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            # BaseAIClient wraps ValueError in Exception with "AI API call failed" message
            assert "AI API call failed" in str(exc_info.value) and "Empty response from GLM API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_API_오류_전파(self, sample_explain_json: dict[str, Any]):
        """인증 실패 등 API 오류 전파 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI') as MockZhipuAI:
            mock_client = MagicMock()

            # Simulate authentication error
            mock_client.chat.completions.create.side_effect = Exception("Invalid API key")
            MockZhipuAI.return_value = mock_client

            client = GLMAIClient(api_key="invalid-key", model_name="glm-4", timeout=30)

            with pytest.raises(Exception) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            assert "Invalid API key" in str(exc_info.value)

    def test_모델명_반환(self):
        """get_model_name() 메서드 확인."""
        with patch('app.infrastructure.ai_optimization.clients.glm.ZhipuAI'):
            client = GLMAIClient(api_key="test-key", model_name="glm-4.5-flash", timeout=30)
            assert client.get_model_name() == "glm-4.5-flash"
