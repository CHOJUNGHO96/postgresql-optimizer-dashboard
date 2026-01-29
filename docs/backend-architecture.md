# 백엔드 아키텍처 문서

## 개요

PostgreSQL Optimizer Dashboard의 백엔드는 **Clean Architecture** 패턴을 기반으로 설계되었다.
모놀리식 구조에서 계층 간 의존성 역전을 통해 유지보수성과 테스트 용이성을 확보한다.

## 기술 스택

| 항목 | 기술 |
|------|------|
| 언어 | Python 3.11+ (async 기반) |
| 웹 프레임워크 | FastAPI |
| DI | dependency_injector |
| DB | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async engine) |
| 마이그레이션 | Alembic (async) |
| 설정 관리 | pydantic-settings + `.env` |
| 테스트 | pytest + pytest-asyncio |
| 컨테이너 | Docker + docker-compose |

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py                              # FastAPI 앱 조립 (라우터, 미들웨어, 에러핸들러)
│   ├── core/
│   │   ├── config.py                        # pydantic_settings 기반 설정
│   │   ├── container.py                     # dependency_injector DI 컨테이너
│   │   ├── logging.py                       # 구조화된 JSON 로깅
│   │   ├── errors.py                        # 전역 에러 핸들러 + 예외 계층
│   │   └── database.py                      # SQLAlchemy async engine/session
│   ├── domain/
│   │   ├── exceptions.py                    # 도메인 예외
│   │   └── query_analysis/
│   │       ├── entities.py                  # QueryPlan 엔티티
│   │       ├── value_objects.py             # PlanNodeType, CostEstimate
│   │       └── repositories.py             # AbstractQueryAnalysisRepository (ABC)
│   ├── application/
│   │   ├── exceptions.py                    # 애플리케이션 예외
│   │   └── query_analysis/
│   │       ├── dtos.py                      # 입출력 DTO
│   │       └── use_cases.py                 # AnalyzeQuery, GetQueryPlan, ListQueryPlans
│   ├── infrastructure/
│   │   ├── exceptions.py                    # 인프라 예외
│   │   └── query_analysis/
│   │       ├── models.py                    # SQLAlchemy ORM 모델
│   │       └── repositories.py             # SQLAlchemy 구현체
│   └── presentation/
│       ├── middleware.py                    # 요청 로깅 + X-Request-ID
│       └── query_analysis/
│           ├── router.py                    # FastAPI APIRouter
│           └── schemas.py                   # 요청/응답 스키마
├── alembic/                                 # DB 마이그레이션
├── tests/                                   # 단위 테스트
├── scripts/
│   └── lint.sh                              # 린트 스크립트
├── pyproject.toml
├── requirements.txt / requirements-dev.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Clean Architecture 레이어

```
┌─────────────────────────────────────────────────────┐
│                   Presentation                       │
│         Router ← Schema (요청/응답 검증)              │
│         Middleware (로깅, Request-ID)                 │
├─────────────────────────────────────────────────────┤
│                   Application                        │
│         UseCase ← DTO (입출력 변환)                   │
│         비즈니스 흐름 오케스트레이션                     │
├─────────────────────────────────────────────────────┤
│                     Domain                           │
│         Entity, Value Object                         │
│         Repository Interface (ABC)                   │
│         도메인 예외                                    │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                      │
│         SQLAlchemy ORM 모델                           │
│         Repository 구현체                             │
│         외부 시스템 연동                               │
└─────────────────────────────────────────────────────┘
```

### 의존성 방향

```
Presentation → Application → Domain ← Infrastructure
```

- **Domain**: 어떤 계층에도 의존하지 않는다. 엔티티, 값 객체, 리포지토리 인터페이스(ABC) 정의.
- **Application**: Domain에만 의존한다. UseCase가 리포지토리 인터페이스를 통해 데이터에 접근.
- **Infrastructure**: Domain의 인터페이스를 구현한다. SQLAlchemy ORM, 외부 API 연동.
- **Presentation**: Application의 UseCase를 호출한다. HTTP 요청/응답 변환 담당.

---

## DI 컨테이너 설계

`dependency_injector`의 `DeclarativeContainer`를 사용하여 전체 의존성 그래프를 관리한다.

```python
Container
├── config (Singleton)         → Settings
├── db_engine (Singleton)      → 내부 DB 엔진
├── db_session_factory          → 내부 DB 세션 팩토리
├── target_db_engine (Singleton)→ 분석 대상 DB 엔진
├── target_db_session_factory   → 대상 DB 세션 팩토리
├── query_analysis_repository   → SQLAlchemyQueryAnalysisRepository
├── analyze_query_use_case      → AnalyzeQueryUseCase
├── get_query_plan_use_case     → GetQueryPlanUseCase
└── list_query_plans_use_case   → ListQueryPlansUseCase
```

### 핵심 설계 원칙

- **wiring_config**: `presentation` 모듈에만 주입하여 계층 분리를 유지한다.
- **이중 DB 엔진**: 내부 DB(결과 저장)와 대상 DB(EXPLAIN 실행)를 분리한다.
- **Factory vs Singleton**: 엔진/세션팩토리는 Singleton, 리포지토리/유스케이스는 Factory로 요청마다 생성.

---

## 도메인 모델 (query_analysis)

### 엔티티: QueryPlan

```python
class QueryPlan(BaseModel):
    id: UUID                    # 고유 식별자
    query: str                  # 분석 대상 SQL 쿼리
    plan_raw: dict[str, Any]    # EXPLAIN JSON 원본 결과
    node_type: PlanNodeType     # 최상위 노드 유형 (Seq Scan, Index Scan 등)
    cost_estimate: CostEstimate # 비용 추정치
    execution_time_ms: float?   # 실제 실행 시간(ms)
    created_at: datetime        # 생성 시각
```

### 값 객체

| 클래스 | 설명 |
|--------|------|
| `PlanNodeType` | EXPLAIN 노드 유형 Enum (Seq Scan, Index Scan, Hash Join 등 21종) |
| `CostEstimate` | 비용 추정치 (startup_cost, total_cost, plan_rows, plan_width) |

### 리포지토리 인터페이스

```python
class AbstractQueryAnalysisRepository(ABC):
    async def save(query_plan) -> QueryPlan           # 결과 저장 (내부 DB)
    async def find_by_id(plan_id) -> QueryPlan | None # ID 조회
    async def find_all(limit, offset) -> list          # 목록 조회
    async def analyze_query(query) -> dict             # EXPLAIN 실행 (대상 DB)
```

---

## 유스케이스

| UseCase | 설명 | 주요 로직 |
|---------|------|-----------|
| `AnalyzeQueryUseCase` | 쿼리 분석 및 저장 | SELECT 검증 → EXPLAIN 실행 → 엔티티 구성 → 저장 |
| `GetQueryPlanUseCase` | ID로 조회 | 리포지토리 조회 → NotFound 처리 |
| `ListQueryPlansUseCase` | 목록 조회 | 페이지네이션 지원 조회 |

---

## API 엔드포인트

| Method | Path | 설명 | 상태코드 |
|--------|------|------|----------|
| `GET` | `/api/v1/health` | 헬스체크 | 200 |
| `POST` | `/api/v1/query-analysis/analyze` | 쿼리 분석 | 201 |
| `GET` | `/api/v1/query-analysis/{plan_id}` | 분석 결과 조회 | 200 |
| `GET` | `/api/v1/query-analysis/` | 분석 결과 목록 | 200 |

### 요청 흐름 (POST /analyze)

```
Client
  → Router (AnalyzeQueryRequest 스키마 검증)
    → UseCase (SELECT 검증 + 비즈니스 로직)
      → Repository.analyze_query() [대상 DB: EXPLAIN ANALYZE]
      → Repository.save() [내부 DB: 결과 저장]
    → DTO 변환
  → QueryPlanResponse
Client ←
```

---

## 에러 처리

### 예외 계층

```
Exception
└── AppBaseError
    ├── DomainError (→ 400)
    │   ├── NotFoundError (→ 404)
    │   ├── ValidationError (→ 400)
    │   ├── QueryNotFoundError (→ 404)
    │   └── InvalidQueryError (→ 400)
    ├── ApplicationError (→ 422)
    │   └── QueryAnalysisFailedError
    └── InfrastructureError (→ 503)
        ├── DatabaseConnectionError
        └── QueryExecutionError
```

### HTTP 매핑 규칙

| 예외 계층 | HTTP 상태코드 | 설명 |
|-----------|--------------|------|
| `NotFoundError` | 404 | 리소스 미발견 |
| `ValidationError` / `DomainError` | 400 | 비즈니스 규칙 위반 |
| `ApplicationError` | 422 | 유스케이스 실패 |
| `InfrastructureError` | 503 | 외부 시스템 장애 |
| 기타 `Exception` | 500 | 처리되지 않은 오류 |

### 보안 원칙

- `InfrastructureError`와 미처리 예외는 내부 상세 정보를 응답에 **노출하지 않는다.**
- `detail` 필드는 내부 로깅에만 사용한다.

### 에러 응답 형식

```json
{
  "error": {
    "type": "not_found",
    "message": "쿼리 분석 결과(ID: ...)을(를) 찾을 수 없습니다."
  }
}
```

---

## 로깅 정책

JSON 구조화 로깅을 사용하며, 5단계 로그 레벨 정책을 준수한다.

| 레벨 | 용도 | 예시 |
|------|------|------|
| `DEBUG` | 개발/디버깅 상세 | 함수 호출 흐름, 변수 값, SQL 쿼리 |
| `INFO` | 정상 동작 기록 | API 요청/응답 완료, 작업 성공 |
| `WARNING` | 비정상이지만 처리 가능 | 재시도, 느린 응답 |
| `ERROR` | 처리된 에러 | 예외 발생, DB/외부 시스템 실패 |
| `CRITICAL` | 즉시 대응 필요 | DB 커넥션 풀 고갈, 필수 서비스 장애 |

### 로그 출력 예시

```json
{
  "timestamp": "2025-01-28T08:26:12.358Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "FastAPI 앱 초기화 완료 (env=development)",
  "module": "main",
  "function": "create_app",
  "line": 65
}
```

### 미들웨어 로깅

`RequestLoggingMiddleware`가 모든 요청에 대해 다음을 수행한다:

- `X-Request-ID` 헤더 자동 생성 (없으면 UUID 부여)
- 요청 시작/완료 로그 (메서드, 경로, 상태코드, 처리 시간)
- 응답 헤더에 `X-Request-ID`, `X-Process-Time` 포함

---

## 데이터베이스 설계

### 이중 DB 구조

```
┌──────────────┐     EXPLAIN ANALYZE     ┌──────────────┐
│   내부 DB     │ ←─ 결과 저장 ──────────  │   대상 DB     │
│ (optimizer_   │                         │ (target_db)   │
│  dashboard)   │                         │               │
│              │   ← EXPLAIN 실행 ──────→ │               │
└──────────────┘                         └──────────────┘
```

- **내부 DB** (`DATABASE_URL`): 분석 결과를 저장하는 애플리케이션 DB
- **대상 DB** (`TARGET_DATABASE_URL`): EXPLAIN을 실행하여 쿼리를 분석하는 대상 PostgreSQL

### ORM 모델 ↔ 엔티티 변환

```
QueryPlanModel (ORM)  ←→  QueryPlan (Entity)
    to_entity()       →   도메인 엔티티로 변환
    from_entity()     ←   ORM 모델로 변환
```

도메인 엔티티(Pydantic)와 ORM 모델(SQLAlchemy)을 분리하여, 도메인 계층이 ORM에 의존하지 않는다.

### query_plans 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (PK) | 고유 식별자 |
| `query` | TEXT | 분석 대상 SQL 쿼리 |
| `plan_raw` | JSON | EXPLAIN 원본 결과 |
| `node_type` | VARCHAR(50) | 최상위 노드 유형 |
| `startup_cost` | FLOAT | 시작 비용 |
| `total_cost` | FLOAT | 총 비용 |
| `plan_rows` | INTEGER | 예상 행 수 |
| `plan_width` | INTEGER | 예상 행 폭(바이트) |
| `execution_time_ms` | FLOAT (nullable) | 실제 실행 시간 |
| `created_at` | DATETIME | 생성 시각 |

---

## 설정 관리

`pydantic-settings` 기반으로 `.env` 파일에서 환경 변수를 로드한다.

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DATABASE_URL` | 내부 DB 연결 URL | `postgresql+asyncpg://...` |
| `TARGET_DATABASE_URL` | 대상 DB 연결 URL | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis 연결 URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | 비밀 키 | `change-me-in-production` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |
| `APP_ENV` | 실행 환경 | `development` |

---

## 테스트 전략

- **외부 의존성 없이** 실행 가능 (실제 DB 접근 금지)
- Repository는 `AsyncMock`으로 대체
- UseCase 중심 단위 테스트

### 테스트 항목 (6개)

| 테스트 | 대상 | 검증 내용 |
|--------|------|-----------|
| `test_성공적인_쿼리_분석` | AnalyzeQueryUseCase | SELECT 쿼리 분석 → 저장 성공 |
| `test_SELECT가_아닌_쿼리는_거부` | AnalyzeQueryUseCase | DELETE 등 비SELECT → InvalidQueryError |
| `test_분석_실패시_예외_발생` | AnalyzeQueryUseCase | DB 장애 → QueryAnalysisFailedError |
| `test_존재하는_계획_조회` | GetQueryPlanUseCase | 유효 ID → 결과 반환 |
| `test_존재하지_않는_계획_조회` | GetQueryPlanUseCase | 무효 ID → QueryNotFoundError |
| `test_목록_조회` | ListQueryPlansUseCase | 페이지네이션 목록 반환 |

### 실행 명령

```bash
cd backend
set PYTHONPATH=.
pytest tests/ -v
```

---

## 실행 방법

### 로컬 실행

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # 환경 변수 편집
set PYTHONPATH=.
uvicorn app.main:app --reload --port 8000
```

### Docker 실행

```bash
cd backend
docker-compose up -d
```

- PostgreSQL 16 + FastAPI 앱이 함께 실행된다.
- 헬스체크: `curl http://localhost:8000/api/v1/health`

### 린트 실행

```bash
cd backend

# 검사만 (CI용)
bash scripts/lint.sh

# 자동 수정
bash scripts/lint.sh --fix
```

도구: `black` (120자) + `isort` (black 프로필) + `flake8` + `toml-sort`

---

## 주요 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| DI 와이어링 범위 | presentation 모듈에만 주입 | 계층 분리 원칙 유지 |
| Session 관리 | Repository 메서드마다 생성/종료 | 트랜잭션 격리, 단순성 |
| Entity vs ORM | Pydantic 엔티티 + SQLAlchemy 모델 분리 | 도메인의 ORM 비의존 |
| DB 연결 | 내부 DB + 대상 DB 이중 엔진 | 분석 결과 저장과 EXPLAIN 실행 분리 |
| 에러 매핑 | 계층별 HTTP 코드 분리 | 예외 원인을 정확히 전달 |
| 주석 언어 | 한글 | 설계 문서 요구사항 |
| async 전면 적용 | 모든 I/O 작업 async/await | FastAPI 성능 최적화 |
