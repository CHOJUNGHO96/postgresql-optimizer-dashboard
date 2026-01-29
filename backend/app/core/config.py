"""애플리케이션 설정 모듈.

pydantic_settings 기반으로 환경 변수를 로드하고 검증한다.
"""

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 전역 설정."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 내부 DB (쿼리 분석 결과 저장용)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "optimizer_dashboard"
    DB_SCHEMA: str = "public"

    # 분석 대상 PostgreSQL DB
    TARGET_DB_HOST: str = "localhost"
    TARGET_DB_PORT: int = 5432
    TARGET_DB_USER: str = "postgres"
    TARGET_DB_PASSWORD: str = "postgres"
    TARGET_DB_NAME: str = "target_db"
    TARGET_DB_SCHEMA: str = "public"

    # Redis (캐싱용)
    REDIS_URL: str = "redis://localhost:6379/0"

    # 보안
    SECRET_KEY: str = "change-me-in-production"

    # 로깅
    LOG_LEVEL: str = "INFO"

    # 환경
    APP_ENV: str = "development"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """내부 DB 연결 URL을 조합한다."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    @property
    def TARGET_DATABASE_URL(self) -> str:
        """대상 DB 연결 URL을 조합한다."""
        return (
            f"postgresql+asyncpg://{self.TARGET_DB_USER}:{self.TARGET_DB_PASSWORD}"
            f"@{self.TARGET_DB_HOST}:{self.TARGET_DB_PORT}/{self.TARGET_DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤을 반환한다."""
    return Settings()
