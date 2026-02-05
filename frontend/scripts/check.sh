#!/bin/bash
# Frontend 코드 품질 검사 스크립트

set -e

cd "$(dirname "$0")/.."

echo "🔍 Frontend 코드 품질 검사 시작..."

MODE="${1:-check}"

if [ "$MODE" = "--fix" ] || [ "$MODE" = "-f" ]; then
    echo "🔧 자동 수정 모드"

    echo "📝 ESLint 자동 수정..."
    npm run lint -- --fix

    echo "✅ 자동 수정 완료!"
else
    echo "🔎 검사 전용 모드 (CI와 동일)"

    echo "📝 ESLint 검사..."
    npm run lint
fi

echo "🔍 TypeScript 타입 체크..."
npm run type-check

echo "🏗️ 빌드 테스트..."
npm run build

echo "✅ 모든 검사 완료!"
