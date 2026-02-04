"""모델별 토큰 제한 설정."""

from enum import Enum
from typing import NamedTuple


class ModelFamily(str, Enum):
    """AI 모델 패밀리."""

    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    ZHIPU = "zhipu"
    UNKNOWN = "unknown"


class ModelTokenLimits(NamedTuple):
    """모델별 토큰 제한."""

    max_input_tokens: int
    max_output_tokens: int
    safety_margin: float = 0.9
    timeout_seconds: int = 60  # 모델별 타임아웃 (초)

    @property
    def safe_input_tokens(self) -> int:
        """안전 마진을 적용한 최대 입력 토큰."""
        return int(self.max_input_tokens * self.safety_margin)

    @property
    def safe_output_tokens(self) -> int:
        """안전 마진을 적용한 최대 출력 토큰."""
        return int(self.max_output_tokens * self.safety_margin)


# 모델별 토큰 제한 설정
MODEL_TOKEN_LIMITS: dict[str, ModelTokenLimits] = {
    # Gemini models - 큰 컨텍스트 처리 능력으로 더 긴 타임아웃 필요
    "gemini-2.0-flash-exp": ModelTokenLimits(1_048_576, 8_192, 0.95, 150),
    "gemini-2.5-flash": ModelTokenLimits(1_048_576, 65_536, 0.95, 150),
    "gemini-exp-1206": ModelTokenLimits(2_097_152, 8_192, 0.95, 180),
    # Claude models - 중간 크기 컨텍스트, 빠른 응답
    "claude-3-5-sonnet-20241022": ModelTokenLimits(200_000, 8_000, 0.9, 75),
    "claude-3-5-haiku-20241022": ModelTokenLimits(200_000, 8_000, 0.9, 60),
    "claude-haiku-4.5": ModelTokenLimits(200_000, 8_000, 0.9, 50),  # 가장 빠른 모델
    # GLM models - 작은 컨텍스트, 보통 응답 속도
    "glm-4.5-flash": ModelTokenLimits(128_000, 96_000, 0.85, 120),
}

# 기본값 (가장 보수적인 설정)
DEFAULT_TOKEN_LIMITS = ModelTokenLimits(128_000, 8_000, 0.85, 90)


def get_model_limits(model_name: str) -> ModelTokenLimits:
    """모델 이름으로 토큰 제한 가져오기.

    Args:
        model_name: AI 모델 이름

    Returns:
        ModelTokenLimits: 모델별 토큰 제한
    """
    return MODEL_TOKEN_LIMITS.get(model_name, DEFAULT_TOKEN_LIMITS)


def get_model_family(model_name: str) -> ModelFamily:
    """모델 이름으로 모델 패밀리 식별.

    Args:
        model_name: AI 모델 이름

    Returns:
        ModelFamily: 모델 패밀리
    """
    model_lower = model_name.lower()

    if "claude" in model_lower:
        return ModelFamily.ANTHROPIC
    elif "gemini" in model_lower:
        return ModelFamily.GOOGLE
    elif "glm" in model_lower:
        return ModelFamily.ZHIPU

    return ModelFamily.UNKNOWN
