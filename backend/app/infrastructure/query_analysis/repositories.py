"""쿼리 분석 리포지토리 SQLAlchemy 구현체."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.query_analysis.entities import QueryPlan
from app.domain.query_analysis.repositories import AbstractQueryAnalysisRepository
from app.infrastructure.exceptions import DatabaseConnectionError, QueryExecutionError
from app.infrastructure.query_analysis.models import QueryPlanModel

logger = logging.getLogger(__name__)


class SQLAlchemyQueryAnalysisRepository(AbstractQueryAnalysisRepository):
    """SQLAlchemy 기반 쿼리 분석 리포지토리 구현체.

    내부 DB(session_factory)와 대상 DB(target_session_factory)를 분리하여 사용한다.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        target_session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._target_session_factory = target_session_factory

    async def save(self, query_plan: QueryPlan) -> QueryPlan:
        """쿼리 실행 계획을 내부 DB에 저장한다."""
        try:
            async with self._session_factory() as session:
                model = QueryPlanModel.from_entity(query_plan)
                session.add(model)
                await session.commit()
                await session.refresh(model)
                logger.debug("쿼리 실행 계획 저장 완료: id=%s", model.id)
                return model.to_entity()
        except Exception as e:
            logger.error("쿼리 실행 계획 저장 실패: %s", str(e))
            raise DatabaseConnectionError(detail=str(e))

    async def find_by_id(self, plan_id: UUID) -> QueryPlan | None:
        """ID로 쿼리 실행 계획을 조회한다."""
        try:
            async with self._session_factory() as session:
                stmt = select(QueryPlanModel).where(QueryPlanModel.id == plan_id)
                result = await session.execute(stmt)
                model = result.scalar_one_or_none()
                if model is None:
                    return None
                return model.to_entity()
        except Exception as e:
            logger.error("쿼리 실행 계획 조회 실패: %s", str(e))
            raise DatabaseConnectionError(detail=str(e))

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[QueryPlan]:
        """쿼리 실행 계획 목록을 조회한다."""
        try:
            async with self._session_factory() as session:
                stmt = (
                    select(QueryPlanModel)
                    .order_by(QueryPlanModel.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                models = result.scalars().all()
                return [model.to_entity() for model in models]
        except Exception as e:
            logger.error("쿼리 실행 계획 목록 조회 실패: %s", str(e))
            raise DatabaseConnectionError(detail=str(e))

    async def analyze_query(self, query: str) -> dict[str, Any]:
        """대상 DB에서 EXPLAIN ANALYZE를 실행한다."""
        try:
            async with self._target_session_factory() as session:
                explain_query = text(f"EXPLAIN (ANALYZE, FORMAT JSON) {query}")
                result = await session.execute(explain_query)
                row = result.scalar_one()
                logger.debug("EXPLAIN 실행 완료")
                return row
        except Exception as e:
            logger.error("EXPLAIN 실행 실패: %s", str(e))
            raise QueryExecutionError(detail=str(e))
