#!/bin/bash
# Backend 코드 품질 검사 스크립트

set -e

cd "$(dirname "$0")/.."

echo "🔍 Backend 코드 품질 검사 시작..."

MODE="${1:-check}"

if [ "$MODE" = "--fix" ] || [ "$MODE" = "-f" ]; then
    echo "🔧 자동 수정 모드"

    echo "📝 Black 포맷팅..."
    black .

    echo "📦 isort 임포트 정렬..."
    isort .

    echo "✅ 자동 수정 완료!"
else
    echo "🔎 검사 전용 모드 (CI와 동일)"

    echo "📝 Black 포맷 체크..."
    black --check .

    echo "📦 isort 임포트 정렬 체크..."
    isort --check-only .
fi

echo "🔍 Flake8 린트 검사..."
flake8 app/ --max-line-length=100 --extend-ignore=E203,W503

echo "🔍 MyPy 타입 체크 (선택적)..."
mypy app/ --ignore-missing-imports || echo "⚠️  타입 체크 경고 무시"

echo "✅ 모든 검사 완료!"
