"""AI 최적화 리포지토리 인터페이스."""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.ai_optimization.entities import OptimizedQuery, OptimizationTask


class AbstractAIOptimizationRepository(ABC):
    """AI 최적화 리포지토리 추상 인터페이스."""

    @abstractmethod
    async def save(self, optimization: OptimizedQuery) -> OptimizedQuery:
        """최적화 결과를 저장한다.

        Args:
            optimization: 저장할 최적화 엔티티

        Returns:
            저장된 최적화 엔티티
        """
        pass

    @abstractmethod
    async def find_by_id(self, optimization_id: UUID) -> OptimizedQuery | None:
        """ID로 최적화 결과를 조회한다.

        Args:
            optimization_id: 최적화 식별자

        Returns:
            최적화 엔티티 또는 None
        """
        pass

    @abstractmethod
    async def find_by_plan_id(self, plan_id: UUID) -> list[OptimizedQuery]:
        """원본 쿼리 계획 ID로 최적화 결과 목록을 조회한다.

        Args:
            plan_id: 원본 쿼리 계획 ID

        Returns:
            최적화 엔티티 목록
        """
        pass

    @abstractmethod
    async def delete(self, optimization_id: UUID) -> bool:
        """최적화 결과를 삭제한다.

        Args:
            optimization_id: 최적화 식별자

        Returns:
            삭제 성공 여부
        """
        pass

    @abstractmethod
    async def create_task(self, task: OptimizationTask) -> OptimizationTask:
        """최적화 작업을 생성한다.

        Args:
            task: 생성할 작업 엔티티

        Returns:
            생성된 작업 엔티티
        """
        pass

    @abstractmethod
    async def find_task_by_id(self, task_id: UUID) -> OptimizationTask | None:
        """ID로 최적화 작업을 조회한다.

        Args:
            task_id: 작업 식별자

        Returns:
            작업 엔티티 또는 None
        """
        pass

    @abstractmethod
    async def update_task(self, task: OptimizationTask) -> OptimizationTask:
        """최적화 작업 상태를 업데이트한다.

        Args:
            task: 업데이트할 작업 엔티티

        Returns:
            업데이트된 작업 엔티티
        """
        pass
