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
from app.presentation.ai_optimization.router import router as ai_optimization_router
from app.presentation.middleware import RequestLoggingMiddleware
from app.presentation.query_analysis.router import (
    health_router,
    router as query_analysis_router,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리."""
    logger.info("애플리케이션 시작")
    yield
    # 종료 시 리소스 정리
    container: Container = app.state.container

    # DB 엔진 정리
    db_engine = container.db_engine()
    target_db_engine = container.target_db_engine()
    await db_engine.dispose()
    await target_db_engine.dispose()

    # AI 클라이언트 정리
    try:
        gemini_client = container.gemini_client()
        if hasattr(gemini_client, 'close'):
            await gemini_client.close()
            logger.info("Gemini 클라이언트 종료 완료")
    except Exception as e:
        logger.warning(f"Gemini 클라이언트 종료 중 에러 (무시): {e}")

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
    app.include_router(ai_optimization_router)

    logger.info("FastAPI 앱 초기화 완료 (env=%s)", settings.APP_ENV)

    return app


# uvicorn 실행용
app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, access_log=False)
