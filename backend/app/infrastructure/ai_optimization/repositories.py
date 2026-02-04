"""AI 최적화 리포지토리 구현."""

from typing import Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ai_optimization.entities import OptimizedQuery, OptimizationTask
from app.domain.ai_optimization.repositories import AbstractAIOptimizationRepository
from app.infrastructure.ai_optimization.models import OptimizedQueryModel, OptimizationTaskModel


class SQLAlchemyAIOptimizationRepository(AbstractAIOptimizationRepository):
    """SQLAlchemy 기반 AI 최적화 리포지토리 구현."""

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        """리포지토리를 초기화한다.

        Args:
            session_factory: AsyncSession 생성 팩토리
        """
        self._session_factory = session_factory

    async def save(self, optimization: OptimizedQuery) -> OptimizedQuery:
        """최적화 결과를 저장한다."""
        async with self._session_factory() as session:
            model = OptimizedQueryModel.from_entity(optimization)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model.to_entity()

    async def find_by_id(self, optimization_id: UUID) -> OptimizedQuery | None:
        """ID로 최적화 결과를 조회한다."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(OptimizedQueryModel).where(
                    OptimizedQueryModel.id == optimization_id
                )
            )
            model = result.scalar_one_or_none()
            return model.to_entity() if model else None

    async def find_by_plan_id(self, plan_id: UUID) -> list[OptimizedQuery]:
        """원본 쿼리 계획 ID로 최적화 결과 목록을 조회한다."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(OptimizedQueryModel)
                .where(OptimizedQueryModel.original_plan_id == plan_id)
                .order_by(OptimizedQueryModel.created_at.desc())
            )
            models = result.scalars().all()
            return [model.to_entity() for model in models]

    async def delete(self, optimization_id: UUID) -> bool:
        """최적화 결과를 삭제한다."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(OptimizedQueryModel).where(
                    OptimizedQueryModel.id == optimization_id
                )
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def create_task(self, task: OptimizationTask) -> OptimizationTask:
        """최적화 작업을 생성한다."""
        async with self._session_factory() as session:
            model = OptimizationTaskModel.from_entity(task)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model.to_entity()

    async def find_task_by_id(self, task_id: UUID) -> OptimizationTask | None:
        """ID로 최적화 작업을 조회한다."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(OptimizationTaskModel).where(OptimizationTaskModel.id == task_id)
            )
            model = result.scalar_one_or_none()
            return model.to_entity() if model else None

    async def update_task(self, task: OptimizationTask) -> OptimizationTask:
        """최적화 작업 상태를 업데이트한다."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(OptimizationTaskModel).where(OptimizationTaskModel.id == task.id)
            )
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Task not found: {task.id}")

            # Update fields from entity
            model.status = task.status.value
            model.optimization_id = task.optimization_id
            model.error_message = task.error_message
            model.error_type = task.error_type
            model.started_at = task.started_at
            model.completed_at = task.completed_at

            await session.commit()
            await session.refresh(model)
            return model.to_entity()
