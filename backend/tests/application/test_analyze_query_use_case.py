"""AnalyzeQueryUseCase 단위 테스트.

외부 의존성 없이 AsyncMock으로 리포지토리를 대체하여 테스트한다.
"""

from unittest.mock import AsyncMock

import pytest

from app.application.query_analysis.dtos import AnalyzeQueryInput
from app.application.query_analysis.use_cases import AnalyzeQueryUseCase, GetQueryPlanUseCase, ListQueryPlansUseCase
from app.domain.exceptions import InvalidQueryError, QueryNotFoundError
from app.domain.query_analysis.entities import QueryPlan
from app.domain.query_analysis.value_objects import PlanNodeType


class TestAnalyzeQueryUseCase:
    """AnalyzeQueryUseCase 테스트."""

    async def test_성공적인_쿼리_분석(self, mock_repository: AsyncMock, sample_query_plan: QueryPlan):
        """SELECT 쿼리 분석이 성공적으로 수행되어야 한다."""
        use_case = AnalyzeQueryUseCase(repository=mock_repository)
        input_dto = AnalyzeQueryInput(query="SELECT * FROM users WHERE id = 1")

        result = await use_case.execute(input_dto)

        assert result.id == sample_query_plan.id
        assert result.query == sample_query_plan.query
        assert result.node_type == PlanNodeType.SEQ_SCAN
        mock_repository.analyze_query.assert_awaited_once()
        mock_repository.save.assert_awaited_once()

    async def test_SELECT가_아닌_쿼리는_거부(self, mock_repository: AsyncMock):
        """SELECT가 아닌 쿼리는 InvalidQueryError를 발생시켜야 한다."""
        use_case = AnalyzeQueryUseCase(repository=mock_repository)
        input_dto = AnalyzeQueryInput(query="DELETE FROM users WHERE id = 1")

        with pytest.raises(InvalidQueryError):
            await use_case.execute(input_dto)

        mock_repository.analyze_query.assert_not_awaited()

    async def test_분석_실패시_예외_발생(self, mock_repository: AsyncMock):
        """리포지토리 분석 실패 시 QueryAnalysisFailedError가 발생해야 한다."""
        from app.application.exceptions import QueryAnalysisFailedError

        mock_repository.analyze_query.side_effect = Exception("DB 연결 실패")
        use_case = AnalyzeQueryUseCase(repository=mock_repository)
        input_dto = AnalyzeQueryInput(query="SELECT 1")

        with pytest.raises(QueryAnalysisFailedError):
            await use_case.execute(input_dto)


class TestGetQueryPlanUseCase:
    """GetQueryPlanUseCase 테스트."""

    async def test_존재하는_계획_조회(self, mock_repository: AsyncMock, sample_query_plan: QueryPlan):
        """존재하는 ID로 조회하면 결과를 반환해야 한다."""
        use_case = GetQueryPlanUseCase(repository=mock_repository)

        result = await use_case.execute(sample_query_plan.id)

        assert result.id == sample_query_plan.id
        mock_repository.find_by_id.assert_awaited_once_with(sample_query_plan.id)

    async def test_존재하지_않는_계획_조회(self, mock_repository: AsyncMock, sample_query_plan: QueryPlan):
        """존재하지 않는 ID로 조회하면 QueryNotFoundError가 발생해야 한다."""
        mock_repository.find_by_id.return_value = None
        use_case = GetQueryPlanUseCase(repository=mock_repository)

        with pytest.raises(QueryNotFoundError):
            await use_case.execute(sample_query_plan.id)


class TestListQueryPlansUseCase:
    """ListQueryPlansUseCase 테스트."""

    async def test_목록_조회(self, mock_repository: AsyncMock):
        """실행 계획 목록을 조회해야 한다."""
        use_case = ListQueryPlansUseCase(repository=mock_repository)

        result = await use_case.execute(limit=10, offset=0)

        assert result.total == 1
        assert len(result.items) == 1
        mock_repository.find_all.assert_awaited_once_with(limit=10, offset=0)
