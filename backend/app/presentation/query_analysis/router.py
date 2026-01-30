"""쿼리 분석 API 라우터."""

from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.application.query_analysis.dtos import AnalyzePlanInput, AnalyzeQueryInput
from app.application.query_analysis.use_cases import AnalyzePlanUseCase, AnalyzeQueryUseCase, GetQueryPlanUseCase, ListQueryPlansUseCase
from app.core.container import Container
from app.presentation.query_analysis.schemas import (
    AnalyzePlanRequest,
    AnalyzeQueryRequest,
    QueryPlanListResponse,
    QueryPlanResponse,
    HealthResponse,
)

router = APIRouter(prefix="/api/v1/query-analysis", tags=["쿼리 분석"])


@router.post("/analyze", response_model=QueryPlanResponse, status_code=201)
@inject
async def analyze_query(
    request: AnalyzeQueryRequest,
    use_case: AnalyzeQueryUseCase = Depends(Provide[Container.analyze_query_use_case]),
) -> QueryPlanResponse:
    """SQL 쿼리를 분석하고 실행 계획을 반환한다."""
    input_dto = AnalyzeQueryInput(query=request.query, title=request.title)
    output = await use_case.execute(input_dto)
    return QueryPlanResponse(**output.model_dump())


@router.post("/analyze-plan", response_model=QueryPlanResponse, status_code=201)
@inject
async def analyze_plan(
    request: AnalyzePlanRequest,
    use_case: AnalyzePlanUseCase = Depends(Provide[Container.analyze_plan_use_case]),
) -> QueryPlanResponse:
    """EXPLAIN JSON을 직접 입력받아 분석한다."""
    input_dto = AnalyzePlanInput(
        plan_json=request.plan_json,
        title=request.title,
        original_query=request.original_query,
    )
    output = await use_case.execute(input_dto)
    return QueryPlanResponse(**output.model_dump())


@router.get("/{plan_id}", response_model=QueryPlanResponse)
@inject
async def get_query_plan(
    plan_id: UUID,
    use_case: GetQueryPlanUseCase = Depends(Provide[Container.get_query_plan_use_case]),
) -> QueryPlanResponse:
    """ID로 쿼리 실행 계획을 조회한다."""
    output = await use_case.execute(plan_id)
    return QueryPlanResponse(**output.model_dump())


@router.get("/", response_model=QueryPlanListResponse)
@inject
async def list_query_plans(
    limit: int = Query(default=100, ge=1, le=1000, description="최대 조회 수"),
    offset: int = Query(default=0, ge=0, description="건너뛸 수"),
    title_search: str | None = Query(default=None, max_length=255, description="제목 LIKE 검색어"),
    use_case: ListQueryPlansUseCase = Depends(Provide[Container.list_query_plans_use_case]),
) -> QueryPlanListResponse:
    """쿼리 실행 계획 목록을 조회한다."""
    output = await use_case.execute(limit=limit, offset=offset, title_search=title_search)
    return QueryPlanListResponse(
        items=[item.model_dump() for item in output.items],
        total=output.total,
    )


# ─── 헬스체크 (별도 라우터) ───

health_router = APIRouter(prefix="/api/v1", tags=["시스템"])


@health_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """애플리케이션 헬스체크."""
    return HealthResponse(status="ok")
