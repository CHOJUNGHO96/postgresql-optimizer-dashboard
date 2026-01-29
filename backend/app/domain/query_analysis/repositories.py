"""쿼리 분석 리포지토리 추상 인터페이스.

도메인 계층에서 정의하며, 인프라 계층에서 구현한다.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.query_analysis.entities import QueryPlan


class AbstractQueryAnalysisRepository(ABC):
    """쿼리 분석 리포지토리 인터페이스."""

    @abstractmethod
    async def save(self, query_plan: QueryPlan) -> QueryPlan:
        """쿼리 실행 계획을 저장한다.

        Args:
            query_plan: 저장할 쿼리 실행 계획 엔티티

        Returns:
            저장된 쿼리 실행 계획
        """
        ...

    @abstractmethod
    async def find_by_id(self, plan_id: UUID) -> QueryPlan | None:
        """ID로 쿼리 실행 계획을 조회한다.

        Args:
            plan_id: 조회할 실행 계획 ID

        Returns:
            쿼리 실행 계획 또는 None
        """
        ...

    @abstractmethod
    async def find_all(
        self, limit: int = 100, offset: int = 0, title_search: str | None = None
    ) -> list[QueryPlan]:
        """쿼리 실행 계획 목록을 조회한다.

        Args:
            limit: 최대 조회 수
            offset: 건너뛸 수
            title_search: 제목 LIKE 검색어 (optional)

        Returns:
            쿼리 실행 계획 목록
        """
        ...

    @abstractmethod
    async def analyze_query(self, query: str) -> dict[str, Any]:
        """대상 DB에서 EXPLAIN을 실행하여 실행 계획을 분석한다.

        Args:
            query: 분석할 SQL 쿼리

        Returns:
            EXPLAIN JSON 결과
        """
        ...
