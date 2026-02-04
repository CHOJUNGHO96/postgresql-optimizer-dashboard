"""AI 최적화 유스케이스."""

import logging
from typing import Callable
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ai_optimization.dtos import (
    CreateTaskInput,
    OptimizeQueryInput,
    OptimizeQueryOutput,
    TaskOutput,
)
from app.core.model_configs import get_model_limits
from app.domain.ai_optimization.entities import OptimizedQuery, OptimizationTask, TaskStatus
from app.domain.ai_optimization.repositories import AbstractAIOptimizationRepository
from app.domain.ai_optimization.services import AbstractAIClientService
from app.domain.ai_optimization.value_objects import (
    AIModel,
    ConfidenceScore,
    OptimizationMetrics,
    RiskLevel,
)
from app.domain.query_analysis.repositories import AbstractQueryAnalysisRepository

logger = logging.getLogger(__name__)


class OptimizeQueryUseCase:
    """쿼리 최적화 유스케이스."""

    def __init__(
        self,
        query_repo: AbstractQueryAnalysisRepository,
        optimization_repo: AbstractAIOptimizationRepository,
        ai_clients: dict[str, AbstractAIClientService],
        target_session_factory: Callable[[], AsyncSession] | None = None,
    ) -> None:
        """유스케이스를 초기화한다.

        Args:
            query_repo: 쿼리 분석 리포지토리
            optimization_repo: AI 최적화 리포지토리
            ai_clients: AI 클라이언트 딕셔너리 (모델명 -> 클라이언트)
            target_session_factory: 대상 DB 세션 팩토리 (검증용)
        """
        self.query_repo = query_repo
        self.optimization_repo = optimization_repo
        self.ai_clients = ai_clients
        self.target_session_factory = target_session_factory

    async def execute(
        self, input_dto: OptimizeQueryInput
    ) -> OptimizeQueryOutput:
        """쿼리를 최적화한다.

        Args:
            input_dto: 최적화 입력 DTO

        Returns:
            최적화 출력 DTO

        Raises:
            ValueError: 원본 쿼리를 찾을 수 없거나 AI 모델이 지원되지 않음
            Exception: AI API 호출 실패
        """
        # 1. 원본 쿼리 계획 조회
        original_plan = await self.query_repo.find_by_id(input_dto.plan_id)
        if not original_plan:
            raise ValueError(f"Query plan not found: {input_dto.plan_id}")

        # 2. AI 클라이언트 선택
        ai_client = self._get_ai_client(input_dto.ai_model)

        # 3. 스키마 컨텍스트 생성 (옵션)
        schema_context = None
        if input_dto.include_schema_context:
            schema_context = await self._get_schema_context()

        # 4. AI API 호출 (재시도 로직 포함)
        logger.info(
            f"Optimizing query {input_dto.plan_id} with {input_dto.ai_model}"
        )
        ai_response = await ai_client.optimize_query_with_retry(
            original_query=original_plan.query,
            explain_json=original_plan.plan_raw,
            schema_context=schema_context,
            max_retries=2,  # 최대 2회 재시도 (총 3번 시도)
        )

        # 5. 검증 (옵션)
        optimized_execution_time = None
        optimized_cost = None
        if input_dto.validate_optimization and self.target_session_factory:
            try:
                validation_result = await self._validate_optimization(
                    ai_response["optimized_query"]
                )
                optimized_execution_time = validation_result.get("execution_time_ms")
                optimized_cost = validation_result.get("total_cost")
            except Exception as e:
                logger.warning(f"Optimization validation failed: {e}")

        # 6. 엔티티 생성
        optimization = OptimizedQuery(
            original_plan_id=input_dto.plan_id,
            ai_model=AIModel(input_dto.ai_model),
            model_version=ai_client.get_model_name(),
            optimized_query=ai_response["optimized_query"],
            optimization_rationale=ai_response["optimization_rationale"],
            optimization_category=ai_response.get("optimization_category"),
            confidence_score=ConfidenceScore(value=ai_response["confidence_score"]),
            metrics=OptimizationMetrics(
                estimated_cost_reduction=ai_response.get("estimated_cost_reduction"),
                estimated_time_reduction=ai_response.get("estimated_time_reduction"),
                optimized_total_cost=optimized_cost,
                optimized_execution_time_ms=optimized_execution_time,
            ),
            applied_techniques=ai_response.get("applied_techniques", []),
            changes_summary=ai_response.get("changes_summary"),
            risk_assessment=RiskLevel(ai_response.get("risk_assessment", "medium")),
        )

        # 7. 저장
        saved_optimization = await self.optimization_repo.save(optimization)

        # 8. DTO 반환
        return OptimizeQueryOutput.from_entity(saved_optimization)

    def _get_ai_client(self, model_name: str) -> AbstractAIClientService:
        """AI 클라이언트를 가져온다."""
        # Map model name to client key
        if "claude" in model_name.lower():
            client_key = "claude"
        elif "glm" in model_name.lower():
            client_key = "glm"
        elif "gemini" in model_name.lower():
            client_key = "gemini"
        else:
            raise ValueError(f"Unsupported AI model: {model_name}")

        client = self.ai_clients.get(client_key)
        if not client:
            raise ValueError(f"AI client not configured: {client_key}")

        return client

    async def _get_schema_context(self) -> str:
        """스키마 컨텍스트를 가져온다.

        TODO: 실제 스키마 정보를 조회하여 반환
        """
        return "Schema context not yet implemented"

    async def _validate_optimization(self, optimized_query: str) -> dict:
        """최적화된 쿼리를 실제 실행하여 검증한다.

        Args:
            optimized_query: 최적화된 SQL 쿼리

        Returns:
            검증 결과 딕셔너리
        """
        if not self.target_session_factory:
            raise ValueError("Target session factory not configured")

        # EXPLAIN ANALYZE 실행
        explain_result = await self.query_repo.analyze_query(
            f"EXPLAIN (ANALYZE, FORMAT JSON) {optimized_query}"
        )

        plan = explain_result[0]["Plan"]
        return {
            "total_cost": plan.get("Total Cost"),
            "execution_time_ms": plan.get("Actual Total Time"),
        }


class GetOptimizationsUseCase:
    """최적화 기록 조회 유스케이스."""

    def __init__(self, optimization_repo: AbstractAIOptimizationRepository) -> None:
        """유스케이스를 초기화한다."""
        self.optimization_repo = optimization_repo

    async def execute(self, plan_id: UUID) -> list[OptimizeQueryOutput]:
        """특정 쿼리 계획의 최적화 기록을 조회한다.

        Args:
            plan_id: 쿼리 계획 ID

        Returns:
            최적화 출력 DTO 목록
        """
        optimizations = await self.optimization_repo.find_by_plan_id(plan_id)
        return [OptimizeQueryOutput.from_entity(opt) for opt in optimizations]


class GetOptimizationUseCase:
    """단일 최적화 조회 유스케이스."""

    def __init__(self, optimization_repo: AbstractAIOptimizationRepository) -> None:
        """유스케이스를 초기화한다."""
        self.optimization_repo = optimization_repo

    async def execute(self, optimization_id: UUID) -> OptimizeQueryOutput:
        """최적화 결과를 조회한다.

        Args:
            optimization_id: 최적화 식별자

        Returns:
            최적화 출력 DTO

        Raises:
            ValueError: 최적화를 찾을 수 없음
        """
        optimization = await self.optimization_repo.find_by_id(optimization_id)
        if not optimization:
            raise ValueError(f"Optimization not found: {optimization_id}")

        return OptimizeQueryOutput.from_entity(optimization)


class CreateOptimizationTaskUseCase:
    """최적화 작업 생성 유스케이스."""

    def __init__(self, repository: AbstractAIOptimizationRepository) -> None:
        """유스케이스를 초기화한다."""
        self.repository = repository

    async def execute(self, input_dto: CreateTaskInput) -> TaskOutput:
        """최적화 작업을 생성한다.

        Args:
            input_dto: 작업 생성 입력 DTO

        Returns:
            작업 출력 DTO
        """
        # Get estimated duration from model config
        model_limits = get_model_limits(input_dto.ai_model)

        # Create task entity
        task = OptimizationTask(
            id=uuid4(),
            plan_id=input_dto.plan_id,
            ai_model=AIModel(input_dto.ai_model),
            validate_optimization=input_dto.validate_optimization,
            include_schema_context=input_dto.include_schema_context,
            status=TaskStatus.PENDING,
            estimated_duration_seconds=model_limits.timeout_seconds,
        )

        # Save to database
        saved_task = await self.repository.create_task(task)
        return TaskOutput.from_entity(saved_task)


class GetOptimizationTaskUseCase:
    """최적화 작업 조회 유스케이스."""

    def __init__(self, repository: AbstractAIOptimizationRepository) -> None:
        """유스케이스를 초기화한다."""
        self.repository = repository

    async def execute(self, task_id: UUID) -> TaskOutput:
        """최적화 작업 상태를 조회한다.

        Args:
            task_id: 작업 식별자

        Returns:
            작업 출력 DTO

        Raises:
            ValueError: 작업을 찾을 수 없음
        """
        task = await self.repository.find_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        return TaskOutput.from_entity(task)


class ProcessOptimizationTaskUseCase:
    """최적화 작업 처리 유스케이스."""

    def __init__(
        self,
        task_repo: AbstractAIOptimizationRepository,
        optimize_use_case: OptimizeQueryUseCase,
    ) -> None:
        """유스케이스를 초기화한다."""
        self.task_repo = task_repo
        self.optimize_use_case = optimize_use_case

    async def execute(self, task_id: UUID) -> None:
        """백그라운드에서 최적화 작업을 처리한다.

        Args:
            task_id: 작업 식별자
        """
        logger.info(f"Starting background optimization task: {task_id}")

        # Load task
        task = await self.task_repo.find_task_by_id(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return

        try:
            # Mark as processing
            task.mark_as_processing()
            await self.task_repo.update_task(task)
            logger.info(f"Task {task_id} marked as processing")

            # Execute optimization
            input_dto = OptimizeQueryInput(
                plan_id=task.plan_id,
                ai_model=task.ai_model.value,
                validate_optimization=task.validate_optimization,
                include_schema_context=task.include_schema_context,
            )
            output_dto = await self.optimize_use_case.execute(input_dto)

            # Mark as completed
            task.mark_as_completed(output_dto.id)
            await self.task_repo.update_task(task)
            logger.info(
                f"Task {task_id} completed successfully. "
                f"Optimization ID: {output_dto.id}"
            )

        except TimeoutError as e:
            logger.error(f"Task {task_id} timed out: {e}")
            task.mark_as_failed(str(e), error_type="timeout")
            await self.task_repo.update_task(task)

        except ValueError as e:
            logger.error(f"Task {task_id} validation error: {e}")
            task.mark_as_failed(str(e), error_type="validation")
            await self.task_repo.update_task(task)

        except Exception as e:
            logger.error(f"Task {task_id} unexpected error: {e}", exc_info=True)
            task.mark_as_failed(str(e), error_type="unexpected")
            await self.task_repo.update_task(task)
