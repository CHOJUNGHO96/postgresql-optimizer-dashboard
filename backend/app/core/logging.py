"""구조화된 로깅 설정 모듈.

5레벨 로깅 정책(DEBUG, INFO, WARNING, ERROR, CRITICAL)을 준수한다.
"""

import logging
import logging.config
import json
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON 형식의 로그 포매터."""

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 문자열로 변환한다."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보가 있으면 추가
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 속성 포함
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO") -> None:
    """로깅 시스템을 초기화한다.

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level.upper(),
            "handlers": ["console"],
        },
        "loggers": {
            "app": {
                "level": log_level.upper(),
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
