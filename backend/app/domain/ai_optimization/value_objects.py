"""AI 최적화 도메인 값 객체."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AIModel(str, Enum):
    """지원되는 AI 모델."""

    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    GLM_4_5_FLASH = "glm-4.5-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"


class RiskLevel(str, Enum):
    """최적화 위험도 수준."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConfidenceScore(BaseModel):
    """AI 신뢰도 점수 값 객체."""

    value: float = Field(ge=0.0, le=1.0, description="신뢰도 점수 (0.0-1.0)")

    @field_validator("value")
    @classmethod
    def validate_range(cls, v: float) -> float:
        """신뢰도 점수 범위 검증."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v


class OptimizationMetrics(BaseModel):
    """최적화 성능 메트릭 값 객체."""

    estimated_cost_reduction: float | None = Field(
        default=None, description="예상 비용 절감률 (%)"
    )
    estimated_time_reduction: float | None = Field(
        default=None, description="예상 시간 단축률 (%)"
    )
    optimized_total_cost: float | None = Field(
        default=None, description="최적화 쿼리 예상 총 비용"
    )
    optimized_execution_time_ms: float | None = Field(
        default=None, description="최적화 쿼리 실제 실행 시간 (ms)"
    )
