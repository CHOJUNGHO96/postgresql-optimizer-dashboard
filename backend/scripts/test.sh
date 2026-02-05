#!/bin/bash
# Backend 테스트 실행 스크립트

set -e

cd "$(dirname "$0")/.."

echo "🧪 Backend 테스트 시작..."

# 기본값
COVERAGE="no"
VERBOSE=""

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --cov|--coverage)
            COVERAGE="yes"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if [ "$COVERAGE" = "yes" ]; then
    echo "📊 커버리지 포함 테스트 실행..."
    pytest tests/ $VERBOSE \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-fail-under=70

    echo "📈 커버리지 리포트: htmlcov/index.html"
else
    echo "🧪 테스트 실행..."
    pytest tests/ $VERBOSE
fi

echo "✅ 테스트 완료!"
