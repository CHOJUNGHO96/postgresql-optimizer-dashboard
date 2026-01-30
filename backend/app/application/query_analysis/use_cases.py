"""쿼리 분석 유스케이스.

비즈니스 로직을 오케스트레이션한다.
"""

import logging
from uuid import UUID

from app.application.exceptions import QueryAnalysisFailedError
from app.application.query_analysis.dtos import AnalyzePlanInput, AnalyzeQueryInput, AnalyzeQueryOutput, QueryPlanListOutput
from app.domain.exceptions import InvalidQueryError, QueryNotFoundError
from app.domain.query_analysis.entities import QueryPlan
from app.domain.query_analysis.repositories import AbstractQueryAnalysisRepository
from app.domain.query_analysis.value_objects import CostEstimate, PlanNodeType

logger = logging.getLogger(__name__)


class AnalyzeQueryUseCase:
    """SQL 쿼리를 분석하고 실행 계획을 저장하는 유스케이스."""

    def __init__(self, repository: AbstractQueryAnalysisRepository) -> None:
        self._repository = repository

    async def execute(self, input_dto: AnalyzeQueryInput) -> AnalyzeQueryOutput:
        """쿼리를 분석하고 결과를 저장한다.

        Args:
            input_dto: 분석 요청 DTO

        Returns:
            분석 결과 DTO

        Raises:
            InvalidQueryError: 쿼리가 유효하지 않을 때
            QueryAnalysisFailedError: 분석 실행에 실패했을 때
        """
        logger.info("쿼리 분석 시작: %s", input_dto.query[:100])

        try:
            # 대상 DB에서 EXPLAIN 실행
            plan_raw = await self._repository.analyze_query(input_dto.query)
        except Exception as e:
            logger.error("쿼리 분석 실패: %s", str(e))
            raise QueryAnalysisFailedError(
                reason="쿼리 분석에 실패했습니다.",
                detail=str(e),
            )

        # EXPLAIN 결과에서 엔티티 구성
        plan_data = plan_raw[0].get("Plan", {}) if isinstance(plan_raw, list) else plan_raw.get("Plan", {})

        node_type_str = plan_data.get("Node Type", "Other")
        try:
            node_type = PlanNodeType(node_type_str)
        except ValueError:
            node_type = PlanNodeType.OTHER

        cost_estimate = CostEstimate(
            startup_cost=plan_data.get("Startup Cost", 0.0),
            total_cost=plan_data.get("Total Cost", 0.0),
            plan_rows=plan_data.get("Plan Rows", 0),
            plan_width=plan_data.get("Plan Width", 0),
        )

        execution_time_ms = plan_raw[0].get("Execution Time") if isinstance(plan_raw, list) else None

        query_plan = QueryPlan(
            query=input_dto.query,
            title=input_dto.title,
            plan_raw=plan_raw if isinstance(plan_raw, dict) else plan_raw[0] if plan_raw else {},
            node_type=node_type,
            cost_estimate=cost_estimate,
            execution_time_ms=execution_time_ms,
        )

        # 내부 DB에 결과 저장
        saved_plan = await self._repository.save(query_plan)
        logger.info("쿼리 분석 완료: plan_id=%s", saved_plan.id)

        return AnalyzeQueryOutput(
            id=saved_plan.id,
            query=saved_plan.query,
            title=saved_plan.title,
            node_type=saved_plan.node_type,
            cost_estimate=saved_plan.cost_estimate,
            execution_time_ms=saved_plan.execution_time_ms,
            plan_raw=saved_plan.plan_raw,
            created_at=saved_plan.created_at,
        )


class AnalyzePlanUseCase:
    """EXPLAIN JSON을 직접 입력받아 분석하는 유스케이스."""

    def __init__(self, repository: AbstractQueryAnalysisRepository) -> None:
        self._repository = repository

    async def execute(self, input_dto: AnalyzePlanInput) -> AnalyzeQueryOutput:
        """EXPLAIN JSON을 분석하고 결과를 저장한다.

        Args:
            input_dto: EXPLAIN JSON 분석 요청 DTO

        Returns:
            분석 결과 DTO
        """
        logger.info("EXPLAIN JSON 직접 분석 시작")

        plan_raw = input_dto.plan_json

        # EXPLAIN 결과에서 엔티티 구성
        plan_data = plan_raw[0].get("Plan", {}) if isinstance(plan_raw, list) else plan_raw.get("Plan", {})

        node_type_str = plan_data.get("Node Type", "Other")
        try:
            node_type = PlanNodeType(node_type_str)
        except ValueError:
            node_type = PlanNodeType.OTHER

        cost_estimate = CostEstimate(
            startup_cost=plan_data.get("Startup Cost", 0.0),
            total_cost=plan_data.get("Total Cost", 0.0),
            plan_rows=plan_data.get("Plan Rows", 0),
            plan_width=plan_data.get("Plan Width", 0),
        )

        execution_time_ms = plan_raw[0].get("Execution Time") if isinstance(plan_raw, list) else None

        # 원본 쿼리가 없으면 빈 문자열 대신 플레이스홀더 사용
        query = input_dto.original_query or "-- EXPLAIN JSON 직접 입력"

        query_plan = QueryPlan(
            query=query,
            title=input_dto.title,
            plan_raw=plan_raw if isinstance(plan_raw, dict) else plan_raw[0] if plan_raw else {},
            node_type=node_type,
            cost_estimate=cost_estimate,
            execution_time_ms=execution_time_ms,
        )

        # 내부 DB에 결과 저장
        saved_plan = await self._repository.save(query_plan)
        logger.info("EXPLAIN JSON 분석 완료: plan_id=%s", saved_plan.id)

        return AnalyzeQueryOutput(
            id=saved_plan.id,
            query=saved_plan.query,
            title=saved_plan.title,
            node_type=saved_plan.node_type,
            cost_estimate=saved_plan.cost_estimate,
            execution_time_ms=saved_plan.execution_time_ms,
            plan_raw=saved_plan.plan_raw,
            created_at=saved_plan.created_at,
        )


class GetQueryPlanUseCase:
    """ID로 쿼리 실행 계획을 조회하는 유스케이스."""

    def __init__(self, repository: AbstractQueryAnalysisRepository) -> None:
        self._repository = repository

    async def execute(self, plan_id: UUID) -> AnalyzeQueryOutput:
        """쿼리 실행 계획을 조회한다.

        Args:
            plan_id: 조회할 실행 계획 ID

        Returns:
            분석 결과 DTO

        Raises:
            QueryNotFoundError: 해당 ID의 결과가 없을 때
        """
        logger.debug("쿼리 실행 계획 조회: plan_id=%s", plan_id)

        plan = await self._repository.find_by_id(plan_id)
        if plan is None:
            raise QueryNotFoundError(plan_id=str(plan_id))

        return AnalyzeQueryOutput(
            id=plan.id,
            query=plan.query,
            title=plan.title,
            node_type=plan.node_type,
            cost_estimate=plan.cost_estimate,
            execution_time_ms=plan.execution_time_ms,
            plan_raw=plan.plan_raw,
            created_at=plan.created_at,
        )


class ListQueryPlansUseCase:
    """쿼리 실행 계획 목록을 조회하는 유스케이스."""

    def __init__(self, repository: AbstractQueryAnalysisRepository) -> None:
        self._repository = repository

    async def execute(
        self, limit: int = 100, offset: int = 0, title_search: str | None = None
    ) -> QueryPlanListOutput:
        """쿼리 실행 계획 목록을 조회한다.

        Args:
            limit: 최대 조회 수
            offset: 건너뛸 수
            title_search: 제목 LIKE 검색어 (optional)

        Returns:
            분석 결과 목록 DTO
        """
        logger.debug(
            "쿼리 실행 계획 목록 조회: limit=%d, offset=%d, title_search=%s",
            limit,
            offset,
            title_search,
        )

        plans = await self._repository.find_all(
            limit=limit, offset=offset, title_search=title_search
        )

        items = [
            AnalyzeQueryOutput(
                id=plan.id,
                query=plan.query,
                title=plan.title,
                node_type=plan.node_type,
                cost_estimate=plan.cost_estimate,
                execution_time_ms=plan.execution_time_ms,
                plan_raw=plan.plan_raw,
                created_at=plan.created_at,
            )
            for plan in plans
        ]

        return QueryPlanListOutput(items=items, total=len(items))
