"""Gemini AI 클라이언트 테스트."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from app.infrastructure.ai_optimization.clients.gemini import GeminiAIClient


class TestGeminiAIClient:
    """Gemini AI 클라이언트 테스트."""

    @pytest.mark.asyncio
    async def test_성공적인_API_호출(self, sample_explain_json: dict[str, Any], sample_optimization_response: str):
        """정상 응답 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            # Mock response
            mock_response = MagicMock()
            mock_response.text = sample_optimization_response

            # Mock async client
            mock_aclient = MagicMock()

            # Create an async mock for generate_content
            async def mock_generate_content(*args, **kwargs):
                return mock_response

            mock_aclient.models.generate_content = mock_generate_content

            # Mock client with aio context manager
            mock_client = MagicMock()

            # Create async context manager behavior
            async def mock_aenter(self):
                return mock_aclient

            async def mock_aexit(self, *args):
                pass

            mock_client.aio.__aenter__ = mock_aenter
            mock_client.aio.__aexit__ = mock_aexit
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=30)

            result = await client.optimize_query(
                original_query="SELECT * FROM users",
                explain_json=sample_explain_json
            )

            # Verify result
            assert result is not None
            assert "optimized_query" in result
            assert result["optimized_query"] == "SELECT id FROM users WHERE id = 1 LIMIT 1"
            assert result["confidence_score"] == 0.9

    @pytest.mark.asyncio
    async def test_타임아웃_처리(self, sample_explain_json: dict[str, Any]):
        """타임아웃 시 TimeoutError 발생 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            async def slow_generate(*args, **kwargs):
                import asyncio
                await asyncio.sleep(5)  # 1초 타임아웃 초과

            # Mock async client
            mock_aclient = MagicMock()
            mock_aclient.models.generate_content.side_effect = slow_generate

            # Mock client with aio context manager
            mock_client = MagicMock()
            mock_client.aio.__aenter__.return_value = mock_aclient
            mock_client.aio.__aexit__.return_value = None
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=1)

            with pytest.raises(TimeoutError) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            assert "timed out after 1 seconds" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_404_모델_없음_오류(self, sample_explain_json: dict[str, Any]):
        """잘못된 모델명 오류 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            # Mock async client
            mock_aclient = MagicMock()

            # Create an async mock that raises APIError with correct constructor
            async def mock_generate_content(*args, **kwargs):
                error_response = {
                    "error": {
                        "code": 404,
                        "message": "Model not found: gemini-invalid"
                    }
                }
                raise errors.APIError(code=404, response_json=error_response)

            mock_aclient.models.generate_content = mock_generate_content

            # Mock client with aio context manager
            mock_client = MagicMock()

            # Create async context manager behavior
            async def mock_aenter(self):
                return mock_aclient

            async def mock_aexit(self, *args):
                pass

            mock_client.aio.__aenter__ = mock_aenter
            mock_client.aio.__aexit__ = mock_aexit
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-invalid", timeout=30)

            with pytest.raises(Exception) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            # BaseAIClient wraps APIError in Exception with "AI API call failed" message
            assert "AI API call failed" in str(exc_info.value)
            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_빈_응답_처리(self, sample_explain_json: dict[str, Any]):
        """response.text가 None인 경우 처리 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            # Mock empty response
            mock_response = MagicMock()
            mock_response.text = None

            # Mock async client
            mock_aclient = MagicMock()

            # Create an async mock for generate_content
            async def mock_generate_content(*args, **kwargs):
                return mock_response

            mock_aclient.models.generate_content = mock_generate_content

            # Mock client with aio context manager
            mock_client = MagicMock()

            # Create async context manager behavior
            async def mock_aenter(self):
                return mock_aclient

            async def mock_aexit(self, *args):
                pass

            mock_client.aio.__aenter__ = mock_aenter
            mock_client.aio.__aexit__ = mock_aexit
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=30)

            with pytest.raises(Exception) as exc_info:
                await client.optimize_query(
                    original_query="SELECT * FROM users",
                    explain_json=sample_explain_json
                )

            # BaseAIClient wraps ValueError in Exception with "AI API call failed" message
            assert "AI API call failed" in str(exc_info.value) and "Empty response from Gemini API" in str(exc_info.value)

    def test_모델명_반환(self):
        """get_model_name() 메서드 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai'):
            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=30)
            assert client.get_model_name() == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_동일_인스턴스로_여러번_호출(self, sample_explain_json: dict[str, Any], sample_optimization_response: str):
        """Singleton 패턴에서 동일 인스턴스로 여러 번 호출 시 정상 작동 확인 (RuntimeError 발생하지 않음)."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            # Mock response
            mock_response = MagicMock()
            mock_response.text = sample_optimization_response

            # Mock async client with AsyncMock for async methods
            mock_aclient = MagicMock()

            # Create an async mock for generate_content
            async def mock_generate_content(*args, **kwargs):
                return mock_response

            mock_aclient.models.generate_content = mock_generate_content

            # Mock client with aio context manager
            mock_client = MagicMock()

            # Create async context manager behavior
            async def mock_aenter(self):
                return mock_aclient

            async def mock_aexit(self, *args):
                pass

            mock_client.aio.__aenter__ = mock_aenter
            mock_client.aio.__aexit__ = mock_aexit
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=30)

            # 첫 번째 호출 - 성공해야 함
            result1 = await client.optimize_query(
                original_query="SELECT * FROM users WHERE id = 1",
                explain_json=sample_explain_json
            )
            assert result1 is not None
            assert "optimized_query" in result1

            # 두 번째 호출 - 동일 인스턴스로 정상 작동해야 함 (RuntimeError 발생하지 않음)
            result2 = await client.optimize_query(
                original_query="SELECT * FROM orders WHERE user_id = 1",
                explain_json=sample_explain_json
            )
            assert result2 is not None
            assert "optimized_query" in result2

            # 세 번째 호출 - 여전히 정상 작동해야 함
            result3 = await client.optimize_query(
                original_query="SELECT * FROM products WHERE category = 'books'",
                explain_json=sample_explain_json
            )
            assert result3 is not None
            assert "optimized_query" in result3

            # _ensure_client가 여러 번 호출되어도 내부적으로 한 번만 초기화됨
            assert client._aclient is not None

    @pytest.mark.asyncio
    async def test_close_메서드로_리소스_정리(self, sample_explain_json: dict[str, Any], sample_optimization_response: str):
        """close() 메서드로 리소스가 정상적으로 정리되는지 확인."""
        with patch('app.infrastructure.ai_optimization.clients.gemini.genai') as MockGenai:
            # Mock response
            mock_response = MagicMock()
            mock_response.text = sample_optimization_response

            # Mock async client
            mock_aclient = MagicMock()

            # Create an async mock for generate_content
            async def mock_generate_content(*args, **kwargs):
                return mock_response

            mock_aclient.models.generate_content = mock_generate_content

            # Track __aexit__ calls
            aexit_call_count = 0

            # Mock client with aio context manager
            mock_client = MagicMock()

            # Create async context manager behavior
            async def mock_aenter(self):
                return mock_aclient

            async def mock_aexit(self, *args):
                nonlocal aexit_call_count
                aexit_call_count += 1

            mock_client.aio.__aenter__ = mock_aenter
            mock_client.aio.__aexit__ = mock_aexit
            MockGenai.Client.return_value = mock_client

            client = GeminiAIClient(api_key="test-key", model_name="gemini-2.5-flash", timeout=30)

            # API 호출
            result = await client.optimize_query(
                original_query="SELECT * FROM users",
                explain_json=sample_explain_json
            )
            assert result is not None

            # 리소스 정리
            await client.close()

            # __aexit__가 호출되어야 함
            assert aexit_call_count == 1

            # close 후 _aclient가 None이 되어야 함
            assert client._aclient is None
