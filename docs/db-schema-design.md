# PostgreSQL Optimizer Dashboard DB 스키마 설계

## 개요

PostgreSQL Optimizer Dashboard의 데이터베이스 스키마 설계 문서.
Clean Architecture 원칙에 따라 도메인 엔티티와 ORM 모델을 분리하여 설계한다.

## 설계 원칙

### 1. 정규화 수준
- 3NF(제3정규형) 준수
- 중복 데이터 최소화
- 참조 무결성 보장

### 2. 성능 고려사항
- **JSONB vs JSON**: 쿼리 가능한 데이터는 JSONB 사용 (인덱싱 가능)
- **UUID vs BIGSERIAL**: UUID 사용 (분산 환경 대비, 외부 노출 시 보안)
- **인덱스 전략**: 자주 조회되는 컬럼에 B-tree 인덱스
- **파티셔닝 준비**: `created_at` 컬럼으로 향후 시간 기반 파티셔닝 가능

### 3. 확장성
- 향후 인증 테이블 추가 가능 구조
- 세션 기반 분석으로 사용자별 분리 준비

---

## 테이블 구조 (5개 테이블)

### ERD 개요

```
┌─────────────────────┐
│  analysis_sessions  │
│  (분석 세션)        │
└─────────┬───────────┘
          │ 1:N
          ▼
┌─────────────────────┐       ┌──────────────────────────┐
│    query_plans      │──────▶│  optimization_suggestions │
│  (쿼리 실행 계획)   │  1:N  │  (최적화 제안)           │
└─────────┬───────────┘       └──────────────────────────┘
          │ 1:N
          ▼
┌─────────────────────┐
│  query_plan_nodes   │ (self-reference)
│  (실행 계획 노드)   │
└─────────────────────┘

┌─────────────────────┐
│  query_statistics   │ (독립 테이블)
│  (쿼리 통계 집계)   │
└─────────────────────┘
```

---

## 1. analysis_sessions (분석 세션)

쿼리 분석 작업을 논리적으로 그룹화하는 세션 테이블.

### 컬럼 정의

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| id | UUID | NO | uuid_generate_v4() | 세션 식별자 (PK) |
| name | VARCHAR(255) | NO | - | 세션 이름 |
| description | TEXT | YES | NULL | 세션 설명 |
| target_database | VARCHAR(255) | YES | NULL | 분석 대상 DB명 |
| status | VARCHAR(20) | NO | 'active' | 상태 (active/completed/archived) |
| created_at | TIMESTAMPTZ | NO | NOW() | 생성 시각 |
| updated_at | TIMESTAMPTZ | NO | NOW() | 수정 시각 |

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 용도 |
|----------|------|------|------|
| ix_sessions_status | status | B-tree | 상태별 필터링 |
| ix_sessions_created_at | created_at | B-tree | 시간순 조회 |

### 상태 값

- `active`: 진행 중인 분석 세션
- `completed`: 완료된 세션
- `archived`: 보관된 세션

---

## 2. query_plans (쿼리 실행 계획)

PostgreSQL EXPLAIN 결과를 저장하는 핵심 테이블.

### 컬럼 정의

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| id | UUID | NO | uuid_generate_v4() | 고유 식별자 (PK) |
| session_id | UUID | YES | NULL | 분석 세션 참조 (FK) |
| query_hash | VARCHAR(64) | NO | - | 쿼리 해시 (SHA-256, 중복 검색용) |
| query | TEXT | NO | - | 분석 대상 SQL |
| plan_raw | JSONB | NO | - | EXPLAIN JSON 원본 |
| node_type | VARCHAR(50) | NO | - | 최상위 노드 유형 |
| startup_cost | FLOAT | NO | 0.0 | 시작 비용 |
| total_cost | FLOAT | NO | 0.0 | 총 비용 |
| plan_rows | INTEGER | NO | 0 | 예상 행 수 |
| plan_width | INTEGER | NO | 0 | 예상 행 폭 (바이트) |
| actual_time_ms | FLOAT | YES | NULL | 실제 실행 시간 (ms) |
| planning_time_ms | FLOAT | YES | NULL | 계획 수립 시간 (ms) |
| created_at | TIMESTAMPTZ | NO | NOW() | 생성 시각 |

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 용도 |
|----------|------|------|------|
| ix_query_plans_session_id | session_id | B-tree | 세션별 조회 |
| ix_query_plans_query_hash | query_hash | B-tree | 중복 쿼리 검색 |
| ix_query_plans_created_at | created_at | B-tree | 시간순 조회, 파티셔닝 준비 |
| ix_query_plans_node_type | node_type | B-tree | 노드 유형별 필터링 |
| ix_query_plans_total_cost | total_cost | B-tree | 비용순 정렬 |

### 외래키

- `session_id` → `analysis_sessions.id` (ON DELETE SET NULL)

### query_hash 생성 규칙

```python
import hashlib

def compute_query_hash(query: str) -> str:
    """쿼리 텍스트를 정규화하고 SHA-256 해시를 생성한다."""
    normalized = " ".join(query.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()
```

---

## 3. query_plan_nodes (실행 계획 노드)

쿼리 실행 계획의 계층적 노드 구조를 저장하는 테이블.
Self-referencing으로 부모-자식 관계를 표현한다.

### 컬럼 정의

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| id | UUID | NO | uuid_generate_v4() | 노드 식별자 (PK) |
| plan_id | UUID | NO | - | 상위 계획 참조 (FK) |
| parent_node_id | UUID | YES | NULL | 부모 노드 (FK, self-reference) |
| depth | INTEGER | NO | 0 | 트리 깊이 (0부터 시작) |
| node_order | INTEGER | NO | 0 | 동일 깊이 내 순서 |
| node_type | VARCHAR(50) | NO | - | 노드 유형 |
| relation_name | VARCHAR(255) | YES | NULL | 대상 테이블/인덱스명 |
| startup_cost | FLOAT | NO | 0.0 | 노드 시작 비용 |
| total_cost | FLOAT | NO | 0.0 | 노드 총 비용 |
| plan_rows | INTEGER | NO | 0 | 예상 행 수 |
| actual_rows | INTEGER | YES | NULL | 실제 행 수 (ANALYZE 실행 시) |
| loops | INTEGER | NO | 1 | 반복 횟수 |
| node_data | JSONB | YES | NULL | 노드 추가 데이터 (Filter, Join Cond 등) |

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 용도 |
|----------|------|------|------|
| ix_plan_nodes_plan_id | plan_id | B-tree | 계획별 노드 조회 |
| ix_plan_nodes_parent_node_id | parent_node_id | B-tree | 자식 노드 조회 |
| ix_plan_nodes_node_type | node_type | B-tree | 노드 유형별 분석 |

### 외래키

- `plan_id` → `query_plans.id` (ON DELETE CASCADE)
- `parent_node_id` → `query_plan_nodes.id` (ON DELETE CASCADE)

### 노드 유형 (PlanNodeType)

PostgreSQL EXPLAIN에서 반환하는 주요 노드 유형:

| 유형 | 설명 |
|------|------|
| Seq Scan | 순차 스캔 |
| Index Scan | 인덱스 스캔 |
| Index Only Scan | 인덱스 전용 스캔 |
| Bitmap Heap Scan | 비트맵 힙 스캔 |
| Bitmap Index Scan | 비트맵 인덱스 스캔 |
| Nested Loop | 중첩 루프 조인 |
| Hash Join | 해시 조인 |
| Merge Join | 병합 조인 |
| Hash | 해시 연산 |
| Sort | 정렬 |
| Aggregate | 집계 |
| Group | 그룹화 |
| Limit | 제한 |
| Result | 결과 |
| Append | 추가 |
| Materialize | 구체화 |
| Unique | 중복 제거 |
| CTE Scan | CTE 스캔 |
| Subquery Scan | 서브쿼리 스캔 |
| Function Scan | 함수 스캔 |
| Other | 기타 |

---

## 4. optimization_suggestions (최적화 제안)

쿼리 실행 계획 분석 결과로 생성된 최적화 제안을 저장.

### 컬럼 정의

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| id | UUID | NO | uuid_generate_v4() | 제안 식별자 (PK) |
| plan_id | UUID | NO | - | 관련 계획 (FK) |
| suggestion_type | VARCHAR(50) | NO | - | 제안 유형 |
| severity | VARCHAR(20) | NO | 'info' | 심각도 (info/warning/critical) |
| title | VARCHAR(255) | NO | - | 제안 제목 |
| description | TEXT | NO | - | 상세 설명 |
| recommendation | TEXT | YES | NULL | 권장 조치 |
| estimated_improvement | FLOAT | YES | NULL | 예상 개선율 (%) |
| created_at | TIMESTAMPTZ | NO | NOW() | 생성 시각 |

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 용도 |
|----------|------|------|------|
| ix_suggestions_plan_id | plan_id | B-tree | 계획별 제안 조회 |
| ix_suggestions_severity | severity | B-tree | 심각도별 필터링 |

### 외래키

- `plan_id` → `query_plans.id` (ON DELETE CASCADE)

### 제안 유형 (suggestion_type)

| 유형 | 설명 |
|------|------|
| missing_index | 인덱스 누락 |
| seq_scan_warning | 순차 스캔 경고 |
| join_optimization | 조인 최적화 |
| statistics_outdated | 통계 갱신 필요 |
| query_rewrite | 쿼리 재작성 권장 |
| partition_suggestion | 파티셔닝 권장 |
| memory_config | 메모리 설정 조정 |

### 심각도 수준 (severity)

| 심각도 | 설명 |
|--------|------|
| info | 참고 정보 |
| warning | 주의 필요 |
| critical | 즉시 조치 필요 |

---

## 5. query_statistics (쿼리 통계 집계)

동일 쿼리의 실행 통계를 집계하여 저장하는 테이블.

### 컬럼 정의

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| id | UUID | NO | uuid_generate_v4() | 통계 식별자 (PK) |
| query_hash | VARCHAR(64) | NO | - | 쿼리 해시 (UNIQUE) |
| call_count | INTEGER | NO | 1 | 호출 횟수 |
| total_time_ms | FLOAT | NO | 0.0 | 총 실행 시간 (ms) |
| min_time_ms | FLOAT | NO | 0.0 | 최소 실행 시간 (ms) |
| max_time_ms | FLOAT | NO | 0.0 | 최대 실행 시간 (ms) |
| avg_time_ms | FLOAT | NO | 0.0 | 평균 실행 시간 (ms) |
| first_seen | TIMESTAMPTZ | NO | NOW() | 최초 발견 시각 |
| last_seen | TIMESTAMPTZ | NO | NOW() | 최근 발견 시각 |

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 용도 |
|----------|------|------|------|
| ix_statistics_query_hash | query_hash | UNIQUE | 해시별 조회 (유일성 보장) |
| ix_statistics_avg_time_ms | avg_time_ms DESC | B-tree | 성능 순위 조회 |

### 통계 업데이트 로직

```sql
INSERT INTO query_statistics (id, query_hash, call_count, total_time_ms, min_time_ms, max_time_ms, avg_time_ms, first_seen, last_seen)
VALUES (gen_random_uuid(), :hash, 1, :time, :time, :time, :time, NOW(), NOW())
ON CONFLICT (query_hash) DO UPDATE SET
    call_count = query_statistics.call_count + 1,
    total_time_ms = query_statistics.total_time_ms + :time,
    min_time_ms = LEAST(query_statistics.min_time_ms, :time),
    max_time_ms = GREATEST(query_statistics.max_time_ms, :time),
    avg_time_ms = (query_statistics.total_time_ms + :time) / (query_statistics.call_count + 1),
    last_seen = NOW();
```

---

## 데이터 흐름

### 쿼리 분석 흐름

```
1. 사용자가 SQL 쿼리 제출
   ↓
2. 쿼리 해시 계산 (SHA-256)
   ↓
3. EXPLAIN ANALYZE 실행 (대상 DB)
   ↓
4. query_plans 테이블에 저장
   ↓
5. 실행 계획 노드 파싱
   ↓
6. query_plan_nodes 테이블에 계층 구조 저장
   ↓
7. 최적화 분석 실행
   ↓
8. optimization_suggestions 테이블에 제안 저장
   ↓
9. query_statistics 테이블 업데이트
```

---

## 마이그레이션 전략

### 버전 관리

- Alembic을 사용한 버전 관리
- 각 마이그레이션은 단일 논리적 변경 단위
- 롤백 가능한 down 마이그레이션 필수

### 초기 마이그레이션 순서

1. `uuid-ossp` 확장 활성화 (UUID 생성)
2. `analysis_sessions` 테이블 생성
3. `query_plans` 테이블 생성 (기존 테이블 확장)
4. `query_plan_nodes` 테이블 생성
5. `optimization_suggestions` 테이블 생성
6. `query_statistics` 테이블 생성
7. 인덱스 생성
8. 외래키 제약조건 추가

---

## 성능 최적화 가이드

### 쿼리 패턴별 인덱스 활용

| 쿼리 패턴 | 사용 인덱스 |
|-----------|-------------|
| 세션별 쿼리 조회 | ix_query_plans_session_id |
| 시간순 목록 조회 | ix_query_plans_created_at |
| 중복 쿼리 검색 | ix_query_plans_query_hash |
| 노드 유형 분석 | ix_query_plans_node_type |
| 고비용 쿼리 조회 | ix_query_plans_total_cost |

### JSONB 컬럼 인덱싱

필요 시 JSONB 컬럼에 GIN 인덱스 추가:

```sql
-- plan_raw 내 특정 키 검색이 빈번한 경우
CREATE INDEX ix_query_plans_plan_raw_gin ON query_plans USING GIN (plan_raw);

-- node_data 검색용
CREATE INDEX ix_plan_nodes_node_data_gin ON query_plan_nodes USING GIN (node_data);
```

### 파티셔닝 (향후 확장)

데이터가 대량으로 쌓이면 시간 기반 파티셔닝 적용:

```sql
-- 월별 파티셔닝 예시
CREATE TABLE query_plans (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE query_plans_2025_01 PARTITION OF query_plans
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## 참고 사항

### PostgreSQL 버전 요구사항

- PostgreSQL 14 이상 권장
- JSONB 연산자 및 인덱싱 기능 활용
- `uuid-ossp` 확장 필요

### 문자셋 및 콜레이션

- 문자셋: UTF-8
- 콜레이션: ko_KR.UTF-8 (한글 정렬) 또는 C (바이너리 정렬)

### 타임존

- 모든 TIMESTAMP 컬럼은 TIMESTAMPTZ 사용
- 애플리케이션에서 UTC로 통일
