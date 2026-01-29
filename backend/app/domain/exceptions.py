"""도메인 계층 예외 정의."""

from app.core.errors import DomainError, NotFoundError, ValidationError


class QueryNotFoundError(NotFoundError):
    """쿼리 분석 결과를 찾을 수 없음."""

    def __init__(self, plan_id: str | None = None) -> None:
        super().__init__(resource="쿼리 분석 결과", resource_id=plan_id)


class InvalidQueryError(ValidationError):
    """유효하지 않은 SQL 쿼리."""

    def __init__(self, reason: str = "유효하지 않은 SQL 쿼리입니다.") -> None:
        super().__init__(message=reason)
