#!/bin/bash
# 린트 실행 스크립트
# 사용법: bash scripts/lint.sh [--fix]

set -e

cd "$(dirname "$0")/.."

if [ "$1" = "--fix" ]; then
    echo "=== 자동 수정 모드 ==="
    echo "--- black 포매팅 ---"
    black app/ tests/

    echo "--- isort 정렬 ---"
    isort app/ tests/

    echo "--- toml-sort 정렬 ---"
    toml-sort --in-place pyproject.toml

    echo "--- flake8 검사 ---"
    flake8 app/ tests/ || true

    echo "=== 완료 ==="
else
    echo "=== 검사 모드 (수정 없음) ==="
    echo "--- black 검사 ---"
    black --check app/ tests/

    echo "--- isort 검사 ---"
    isort --check-only app/ tests/

    echo "--- toml-sort 검사 ---"
    toml-sort --check pyproject.toml

    echo "--- flake8 검사 ---"
    flake8 app/ tests/

    echo "=== 모든 검사 통과 ==="
fi
