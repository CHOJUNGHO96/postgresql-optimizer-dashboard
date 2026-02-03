"""쿼리 최적화 프롬프트 템플릿."""

import json
from typing import Any


def build_optimization_prompt(
    original_query: str,
    explain_json: dict[str, Any],
    schema_context: str | None = None,
) -> str:
    """쿼리 최적화 프롬프트를 생성한다.

    Args:
        original_query: 원본 SQL 쿼리
        explain_json: EXPLAIN JSON 결과
        schema_context: 선택적 스키마 정보

    Returns:
        프롬프트 텍스트
    """
    schema_section = ""
    if schema_context:
        schema_section = f"""
## 데이터베이스 스키마 컨텍스트

{schema_context}
"""

    prompt = f"""당신은 PostgreSQL 쿼리 최적화 전문가입니다. 다음 SQL 쿼리와 실행 계획을 분석하고 최적화된 버전을 제공하세요.

## 원본 쿼리

```sql
{original_query}
```

## 실행 계획 (EXPLAIN JSON)

```json
{json.dumps(explain_json, indent=2)}
```
{schema_section}

## 작업

상세한 쿼리 최적화 분석과 개선된 쿼리 버전을 제공하세요. 응답은 반드시 다음 구조의 유효한 JSON 객체여야 합니다:

```json
{{
  "optimized_query": "최적화된 SQL 쿼리",
  "optimization_rationale": "최적화가 이루어진 이유에 대한 상세 설명",
  "estimated_cost_reduction": 25.5,
  "estimated_time_reduction": 30.0,
  "confidence_score": 0.85,
  "optimization_category": "index|join|subquery|aggregation|partition|other",
  "applied_techniques": ["적용된 기법1", "적용된 기법2"],
  "changes_summary": {{
    "before": "기존 접근 방식 설명",
    "after": "최적화된 접근 방식 설명",
    "key_changes": ["변경사항1", "변경사항2"]
  }},
  "risk_assessment": "low|medium|high"
}}
```

## 가이드라인

1. **optimized_query**: 완전한 최적화된 SQL 쿼리를 제공하세요
2. **optimization_rationale**: 각 최적화에 대한 근거를 설명하세요
3. **estimated_cost_reduction**: 쿼리 비용 절감 예상 백분율 (0-100)
4. **estimated_time_reduction**: 실행 시간 단축 예상 백분율 (0-100)
5. **confidence_score**: 이 최적화에 대한 확신도 (0.0-1.0)
6. **optimization_category**: 적용된 주요 최적화 카테고리
7. **applied_techniques**: 사용된 구체적인 최적화 기법 목록 (예: "인덱스 힌트 추가", "서브쿼리를 JOIN으로 재작성", "WHERE 절 필터 추가")
8. **changes_summary**: 변경사항에 대한 구조화된 요약
9. **risk_assessment**:
   - "low": 위험도가 낮은 안전한 변경사항
   - "medium": 프로덕션 적용 전 테스트가 필요한 변경사항
   - "high": 신중한 검증이 필요한 중요한 변경사항

## 중요 사항

- 쿼리의 동일한 의미를 유지하는 최적화만 제안하세요
- PostgreSQL 특화 기능과 모범 사례를 고려하세요
- 쿼리가 이미 잘 최적화되어 있다면 그렇게 명시하고 가능하다면 사소한 개선사항을 제공하세요
- 예상 개선치는 현실적으로 작성하세요
- 유효한 JSON만 응답하고 추가 텍스트는 작성하지 마세요
"""

    return prompt


def parse_optimization_response(response_text: str) -> dict[str, Any]:
    """AI 응답을 파싱한다.

    Args:
        response_text: AI 응답 텍스트

    Returns:
        파싱된 최적화 결과

    Raises:
        ValueError: JSON 파싱 실패
    """
    # Extract JSON from markdown code blocks if present
    text = response_text.strip()
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        text = text[start:end].strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}")
