"""인프라 계층 예외 정의."""

from app.core.errors import InfrastructureError


class DatabaseConnectionError(InfrastructureError):
    """데이터베이스 연결 실패."""

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(message="데이터베이스 연결에 실패했습니다.", detail=detail)


class QueryExecutionError(InfrastructureError):
    """쿼리 실행 실패."""

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(message="쿼리 실행에 실패했습니다.", detail=detail)
