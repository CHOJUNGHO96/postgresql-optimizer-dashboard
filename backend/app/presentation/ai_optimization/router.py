"""AI 최적화 API 라우터."""

import logging
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.ai_optimization.dtos import OptimizeQueryInput
from app.application.ai_optimization.use_cases import (
    GetOptimizationUseCase,
    GetOptimizationsUseCase,
    OptimizeQueryUseCase,
)
from app.core.container import Container
from app.presentation.ai_optimization.schemas import (
    OptimizationMetricsResponse,
    OptimizedQueryResponse,
    OptimizeQueryRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/query-analysis",
    tags=["AI Optimization"],
)


@router.post(
    "/{plan_id}/optimize",
    response_model=OptimizedQueryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="쿼리 최적화",
    description="AI 모델을 사용하여 쿼리를 최적화합니다.",
)
@inject
async def optimize_query(
    plan_id: UUID,
    request: OptimizeQueryRequest,
    use_case: OptimizeQueryUseCase = Depends(
        Provide[Container.optimize_query_use_case]
    ),
) -> OptimizedQueryResponse:
    """쿼리를 최적화한다.

    Args:
        plan_id: 원본 쿼리 계획 ID
        request: 최적화 요청
        use_case: 최적화 유스케이스

    Returns:
        최적화 결과

    Raises:
        HTTPException: 쿼리를 찾을 수 없거나 최적화 실패
    """
    try:
        input_dto = OptimizeQueryInput(
            plan_id=plan_id,
            ai_model=request.ai_model,
            validate_optimization=request.validate_optimization,
            include_schema_context=request.include_schema_context,
        )
        output_dto = await use_case.execute(input_dto)

        return OptimizedQueryResponse(
            id=str(output_dto.id),
            original_plan_id=str(output_dto.original_plan_id),
            ai_model=output_dto.ai_model,
            model_version=output_dto.model_version,
            optimized_query=output_dto.optimized_query,
            optimization_rationale=output_dto.optimization_rationale,
            optimization_category=output_dto.optimization_category,
            confidence_score=output_dto.confidence_score,
            metrics=OptimizationMetricsResponse(
                estimated_cost_reduction=output_dto.metrics.estimated_cost_reduction,
                estimated_time_reduction=output_dto.metrics.estimated_time_reduction,
                optimized_total_cost=output_dto.metrics.optimized_total_cost,
                optimized_execution_time_ms=output_dto.metrics.optimized_execution_time_ms,
            ),
            applied_techniques=output_dto.applied_techniques,
            changes_summary=output_dto.changes_summary,
            risk_assessment=output_dto.risk_assessment,
            created_at=output_dto.created_at,
        )
    except ValueError as e:
        logger.error(f"Validation error in optimize_query: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TimeoutError as e:
        logger.error(f"Timeout in optimize_query: {e}")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in optimize_query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize query",
        )


@router.get(
    "/{plan_id}/optimize",
    response_model=list[OptimizedQueryResponse],
    summary="최적화 기록 조회",
    description="특정 쿼리 계획의 최적화 기록을 조회합니다.",
)
@inject
async def get_optimizations(
    plan_id: UUID,
    use_case: GetOptimizationsUseCase = Depends(
        Provide[Container.get_optimizations_use_case]
    ),
) -> list[OptimizedQueryResponse]:
    """최적화 기록을 조회한다.

    Args:
        plan_id: 쿼리 계획 ID
        use_case: 조회 유스케이스

    Returns:
        최적화 기록 목록
    """
    try:
        output_dtos = await use_case.execute(plan_id)

        return [
            OptimizedQueryResponse(
                id=str(dto.id),
                original_plan_id=str(dto.original_plan_id),
                ai_model=dto.ai_model,
                model_version=dto.model_version,
                optimized_query=dto.optimized_query,
                optimization_rationale=dto.optimization_rationale,
                optimization_category=dto.optimization_category,
                confidence_score=dto.confidence_score,
                metrics=OptimizationMetricsResponse(
                    estimated_cost_reduction=dto.metrics.estimated_cost_reduction,
                    estimated_time_reduction=dto.metrics.estimated_time_reduction,
                    optimized_total_cost=dto.metrics.optimized_total_cost,
                    optimized_execution_time_ms=dto.metrics.optimized_execution_time_ms,
                ),
                applied_techniques=dto.applied_techniques,
                changes_summary=dto.changes_summary,
                risk_assessment=dto.risk_assessment,
                created_at=dto.created_at,
            )
            for dto in output_dtos
        ]
    except Exception as e:
        logger.error(f"Error in get_optimizations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve optimizations",
        )


@router.get(
    "/{plan_id}/optimize/{optimization_id}",
    response_model=OptimizedQueryResponse,
    summary="최적화 조회",
    description="특정 최적화 결과를 조회합니다.",
)
@inject
async def get_optimization(
    plan_id: UUID,  # Not used but kept for consistent URL structure
    optimization_id: UUID,
    use_case: GetOptimizationUseCase = Depends(
        Provide[Container.get_optimization_use_case]
    ),
) -> OptimizedQueryResponse:
    """최적화 결과를 조회한다.

    Args:
        plan_id: 쿼리 계획 ID (URL 일관성을 위해 포함)
        optimization_id: 최적화 식별자
        use_case: 조회 유스케이스

    Returns:
        최적화 결과

    Raises:
        HTTPException: 최적화를 찾을 수 없음
    """
    try:
        output_dto = await use_case.execute(optimization_id)

        return OptimizedQueryResponse(
            id=str(output_dto.id),
            original_plan_id=str(output_dto.original_plan_id),
            ai_model=output_dto.ai_model,
            model_version=output_dto.model_version,
            optimized_query=output_dto.optimized_query,
            optimization_rationale=output_dto.optimization_rationale,
            optimization_category=output_dto.optimization_category,
            confidence_score=output_dto.confidence_score,
            metrics=OptimizationMetricsResponse(
                estimated_cost_reduction=output_dto.metrics.estimated_cost_reduction,
                estimated_time_reduction=output_dto.metrics.estimated_time_reduction,
                optimized_total_cost=output_dto.metrics.optimized_total_cost,
                optimized_execution_time_ms=output_dto.metrics.optimized_execution_time_ms,
            ),
            applied_techniques=output_dto.applied_techniques,
            changes_summary=output_dto.changes_summary,
            risk_assessment=output_dto.risk_assessment,
            created_at=output_dto.created_at,
        )
    except ValueError as e:
        logger.error(f"Not found in get_optimization: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_optimization: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve optimization",
        )
