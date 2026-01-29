"""Alembic 비동기 마이그레이션 환경 설정."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.core.database import Base

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터 등록 (모델 자동 감지용)
from app.infrastructure.query_analysis.models import (  # noqa: F401, E402
    AnalysisSessionModel,
    OptimizationSuggestionModel,
    QueryPlanModel,
    QueryPlanNodeModel,
    QueryStatisticsModel,
)

target_metadata = Base.metadata

# .env에서 스키마 설정 로드
_settings = get_settings()
TARGET_SCHEMA = _settings.DB_SCHEMA


def run_migrations_offline() -> None:
    """오프라인 모드로 마이그레이션을 실행한다."""
    settings = get_settings()
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=TARGET_SCHEMA,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """마이그레이션을 실행한다."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=TARGET_SCHEMA,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진으로 마이그레이션을 실행한다."""
    settings = get_settings()
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 스키마 생성은 별도 트랜잭션으로 처리
    async with connectable.begin() as connection:
        await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA}"))

    # 마이그레이션 실행
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드로 마이그레이션을 실행한다."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
