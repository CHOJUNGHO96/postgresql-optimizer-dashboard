"""데이터베이스 연결 모듈.

SQLAlchemy async engine 및 session 팩토리를 제공한다.
"""

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy ORM 모델 기본 클래스."""

    pass


def create_engine(database_url: str, schema: str = "public"):
    """비동기 엔진을 생성한다.

    Args:
        database_url: PostgreSQL 연결 URL (postgresql+asyncpg:// 스킴)
        schema: 사용할 스키마 이름 (기본값: public)
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

    # 연결 시 search_path 설정
    @event.listens_for(engine.sync_engine, "connect")
    def set_search_path(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()

    return engine


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """비동기 세션 팩토리를 생성한다.

    Args:
        engine: SQLAlchemy 비동기 엔진
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
