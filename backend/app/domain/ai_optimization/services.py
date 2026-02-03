"""AI 클라이언트 서비스 인터페이스."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractAIClientService(ABC):
    """AI 클라이언트 서비스 추상 인터페이스."""

    @abstractmethod
    async def optimize_query(
        self,
        original_query: str,
        explain_json: dict[str, Any],
        schema_context: str | None = None,
    ) -> dict[str, Any]:
        """쿼리를 최적화한다.

        Args:
            original_query: 원본 SQL 쿼리
            explain_json: EXPLAIN JSON 결과
            schema_context: 선택적 스키마 정보

        Returns:
            최적화 결과 딕셔너리:
            {
                "optimized_query": str,
                "optimization_rationale": str,
                "estimated_cost_reduction": float | None,
                "estimated_time_reduction": float | None,
                "confidence_score": float,
                "optimization_category": str | None,
                "applied_techniques": list[str],
                "changes_summary": dict | None,
                "risk_assessment": str
            }

        Raises:
            Exception: API 호출 실패 또는 타임아웃
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """모델명을 반환한다.

        Returns:
            AI 모델명
        """
        pass
