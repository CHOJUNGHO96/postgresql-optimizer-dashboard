# Alembic 마이그레이션 가이드

PostgreSQL Optimizer Dashboard의 데이터베이스 마이그레이션 관리 가이드.

## 개요

Alembic은 SQLAlchemy를 위한 데이터베이스 마이그레이션 도구이다.
본 프로젝트는 비동기(async) 엔진을 사용하며, 모든 마이그레이션은 버전 관리된다.

## 디렉토리 구조

```
backend/
├── alembic/
│   ├── env.py              # 마이그레이션 환경 설정 (async 지원)
│   ├── script.py.mako      # 마이그레이션 스크립트 템플릿
│   ├── versions/           # 마이그레이션 파일들
│   │   ├── .gitkeep
│   │   └── 001_initial_schema.py
│   └── README.md           # 이 문서
└── alembic.ini             # Alembic 설정 파일
```

## 사전 요구사항

1. PostgreSQL 데이터베이스 실행 중
2. `.env` 파일에 `DATABASE_URL` 설정
3. Python 가상환경 활성화

```bash
# 환경 변수 예시
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/optimizer_dashboard
```

## 자주 사용하는 명령어

### 현재 마이그레이션 상태 확인

```bash
cd backend
alembic current
```

### 마이그레이션 히스토리 조회

```bash
alembic history --verbose
```

### 마이그레이션 실행 (업그레이드)

```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade 001_initial_schema

# 한 단계 업그레이드
alembic upgrade +1
```

### 마이그레이션 롤백 (다운그레이드)

```bash
# 한 단계 롤백
alembic downgrade -1

# 특정 버전으로 롤백
alembic downgrade 001_initial_schema

# 초기 상태로 롤백 (모든 테이블 삭제)
alembic downgrade base
```

### 새 마이그레이션 생성

```bash
# 자동 생성 (ORM 모델 변경 감지)
alembic revision --autogenerate -m "Add user_id column to query_plans"

# 빈 마이그레이션 파일 생성
alembic revision -m "Custom migration description"
```

## 마이그레이션 파일 작성 가이드

### 파일 명명 규칙

- 형식: `{순번}_{설명}.py`
- 예시: `001_initial_schema.py`, `002_add_user_id.py`

### 기본 구조

```python
"""마이그레이션 설명.

Revision ID: 002_add_user_id
Revises: 001_initial_schema
Create Date: 2025-01-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_add_user_id"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """스키마 업그레이드."""
    op.add_column("query_plans", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_query_plans_user_id", "query_plans", ["user_id"])


def downgrade() -> None:
    """스키마 다운그레이드."""
    op.drop_index("ix_query_plans_user_id", table_name="query_plans")
    op.drop_column("query_plans", "user_id")
```

### 주요 작업 패턴

#### 테이블 생성

```python
op.create_table(
    "table_name",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    comment="테이블 설명",
)
```

#### 컬럼 추가/삭제

```python
# 추가
op.add_column("table_name", sa.Column("new_column", sa.String(100)))

# 삭제
op.drop_column("table_name", "column_name")
```

#### 인덱스 생성/삭제

```python
# 생성
op.create_index("ix_table_column", "table_name", ["column_name"])

# 유니크 인덱스
op.create_index("ix_table_column", "table_name", ["column_name"], unique=True)

# 삭제
op.drop_index("ix_table_column", table_name="table_name")
```

#### 외래키 생성/삭제

```python
# 생성
op.create_foreign_key(
    "fk_table_ref",
    "source_table",
    "target_table",
    ["source_column"],
    ["target_column"],
    ondelete="CASCADE",
)

# 삭제
op.drop_constraint("fk_table_ref", "source_table", type_="foreignkey")
```

#### 데이터 마이그레이션

```python
from sqlalchemy.sql import table, column

# 테이블 참조 정의
my_table = table("my_table", column("status", sa.String))

# 데이터 업데이트
op.execute(my_table.update().where(my_table.c.status == "old").values(status="new"))
```

## 주의사항

### 1. 롤백 가능성 확보

모든 `upgrade()`에는 대응하는 `downgrade()`가 필요하다.
데이터 손실이 발생할 수 있는 작업(컬럼 삭제 등)은 특히 주의.

### 2. 대용량 테이블 변경

프로덕션에서 대용량 테이블 변경 시:
- 테이블 락 최소화
- 배치 처리 고려
- 다운타임 계획

```python
# 대용량 테이블에 인덱스 추가 시 CONCURRENTLY 사용
op.execute("CREATE INDEX CONCURRENTLY ix_large_table_col ON large_table (col)")
```

### 3. 트랜잭션 관리

Alembic은 기본적으로 각 마이그레이션을 트랜잭션으로 감싼다.
DDL과 DML을 혼합할 때 주의.

```python
# 트랜잭션 분리가 필요한 경우
def upgrade() -> None:
    # DDL 작업
    op.add_column(...)

    # 커밋 후 새 트랜잭션 시작
    op.execute("COMMIT")

    # DML 작업
    op.execute("UPDATE ...")
```

### 4. ORM 모델과 동기화

마이그레이션 후 ORM 모델도 반드시 업데이트해야 한다.
`--autogenerate` 사용 시 모델 변경 먼저 수행.

## 트러블슈팅

### 마이그레이션 상태 불일치

```bash
# alembic_version 테이블 직접 확인
psql -d optimizer_dashboard -c "SELECT * FROM alembic_version;"

# 강제로 버전 설정 (주의: 실제 스키마와 불일치 가능)
alembic stamp head
```

### 연결 오류

1. PostgreSQL 서비스 실행 확인
2. `DATABASE_URL` 환경 변수 확인
3. 방화벽/네트워크 설정 확인

### 마이그레이션 충돌

여러 개발자가 동시에 마이그레이션 생성 시:

```bash
# 충돌 해결 후 병합
alembic merge -m "Merge migrations" rev1 rev2
```

## 참고 자료

- [Alembic 공식 문서](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL DDL 가이드](https://www.postgresql.org/docs/current/ddl.html)
