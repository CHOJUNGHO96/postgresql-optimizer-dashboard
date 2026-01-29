"""전역 에러 핸들러 및 예외 계층 모듈.

계층별 예외를 HTTP 응답으로 매핑한다.
보안상 민감 정보는 응답에 노출하지 않는다.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ─── 기본 예외 계층 ───


class AppBaseError(Exception):
    """애플리케이션 최상위 예외."""

    def __init__(self, message: str = "내부 서버 오류가 발생했습니다.", detail: str | None = None) -> None:
        self.message = message
        self.detail = detail  # 내부 로깅용 (응답에 노출하지 않음)
        super().__init__(message)


class DomainError(AppBaseError):
    """도메인 계층 예외 (비즈니스 규칙 위반)."""

    pass


class ApplicationError(AppBaseError):
    """애플리케이션 계층 예외 (유스케이스 실패)."""

    pass


class InfrastructureError(AppBaseError):
    """인프라 계층 예외 (외부 시스템 장애)."""

    pass


# ─── 공통 서브클래스 ───


class NotFoundError(DomainError):
    """요청한 리소스를 찾을 수 없음."""

    def __init__(self, resource: str = "리소스", resource_id: Any = None) -> None:
        message = f"{resource}을(를) 찾을 수 없습니다."
        if resource_id is not None:
            message = f"{resource}(ID: {resource_id})을(를) 찾을 수 없습니다."
        super().__init__(message=message)


class ValidationError(DomainError):
    """입력값 검증 실패."""

    pass


# ─── 에러 응답 생성 ───


def _error_response(status_code: int, message: str, error_type: str) -> JSONResponse:
    """표준화된 에러 응답을 생성한다."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": error_type,
                "message": message,
            }
        },
    )


# ─── 전역 예외 핸들러 등록 ───


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 전역 예외 핸들러를 등록한다."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        logger.warning("리소스 미발견: %s", exc.message)
        return _error_response(404, exc.message, "not_found")

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("검증 실패: %s", exc.message)
        return _error_response(400, exc.message, "validation_error")

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning("도메인 에러: %s", exc.message)
        return _error_response(400, exc.message, "domain_error")

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.error("애플리케이션 에러: %s (상세: %s)", exc.message, exc.detail)
        return _error_response(422, exc.message, "application_error")

    @app.exception_handler(InfrastructureError)
    async def infrastructure_error_handler(request: Request, exc: InfrastructureError) -> JSONResponse:
        logger.error("인프라 에러: %s (상세: %s)", exc.message, exc.detail)
        # 보안: 내부 상세 정보는 응답에 포함하지 않음
        return _error_response(503, "서비스를 일시적으로 사용할 수 없습니다.", "infrastructure_error")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical("처리되지 않은 예외 발생: %s", str(exc), exc_info=True)
        # 보안: 내부 에러 정보 노출 금지
        return _error_response(500, "내부 서버 오류가 발생했습니다.", "internal_error")
