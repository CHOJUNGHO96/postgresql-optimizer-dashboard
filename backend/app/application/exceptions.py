"""애플리케이션 계층 예외 정의."""

from app.core.errors import ApplicationError


class QueryAnalysisFailedError(ApplicationError):
    """쿼리 분석 실패."""

    def __init__(self, reason: str = "쿼리 분석에 실패했습니다.", detail: str | None = None) -> None:
        super().__init__(message=reason, detail=detail)
