"""FastAPI 애플리케이션 진입점.

라우터, 미들웨어, 에러 핸들러를 조립한다.
"""

import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.container import Container
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.presentation.middleware import RequestLoggingMiddleware
from app.presentation.query_analysis.router import health_router, router as query_analysis_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리."""
    logger.info("애플리케이션 시작")
    yield
    # 종료 시 DB 엔진 정리
    container: Container = app.state.container
    db_engine = container.db_engine()
    target_db_engine = container.target_db_engine()
    await db_engine.dispose()
    await target_db_engine.dispose()
    logger.info("애플리케이션 종료")


def create_app() -> FastAPI:
    """FastAPI 앱을 생성하고 구성한다."""
    settings = get_settings()

    # 로깅 초기화
    setup_logging(log_level=settings.LOG_LEVEL)

    # DI 컨테이너 초기화
    container = Container()

    app = FastAPI(
        title="PostgreSQL Optimizer Dashboard API",
        description="PostgreSQL 쿼리 최적화 대시보드 백엔드 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 컨테이너를 앱 상태에 저장
    app.state.container = container

    # 전역 에러 핸들러 등록
    register_error_handlers(app)

    # 미들웨어 등록
    app.add_middleware(RequestLoggingMiddleware)

    # 라우터 등록
    app.include_router(health_router)
    app.include_router(query_analysis_router)

    logger.info("FastAPI 앱 초기화 완료 (env=%s)", settings.APP_ENV)

    return app


# uvicorn 실행용
app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, access_log=False)
