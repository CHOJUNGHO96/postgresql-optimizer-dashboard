"""요청 로깅 미들웨어."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답 로깅 및 X-Request-ID 부여 미들웨어."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """요청을 처리하고 로깅한다."""
        # 요청 ID 생성 또는 기존 값 사용
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        logger.info(
            "요청 시작: %s %s (request_id=%s)",
            request.method,
            request.url.path,
            request_id,
        )

        response = await call_next(request)

        # 처리 시간 계산
        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

        logger.info(
            "요청 완료: %s %s → %d (%.2fms, request_id=%s)",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
            request_id,
        )

        return response
