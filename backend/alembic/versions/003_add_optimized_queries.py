"""Add optimized_queries table for AI-based query optimization.

Revision ID: 003_add_optimized_queries
Revises: 002_add_title_column
Create Date: 2025-01-30

새 테이블:
- optimized_queries: AI 모델을 사용한 쿼리 최적화 결과 저장
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision: str = "003_add_optimized_queries"
down_revision: Union[str, None] = "002_add_title_column"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 스키마 설정
TARGET_SCHEMA = get_settings().DB_SCHEMA


def upgrade() -> None:
    """스키마 업그레이드: optimized_queries 테이블 생성."""
    op.create_table(
        "optimized_queries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            comment="최적화 식별자",
        ),
        sa.Column(
            "original_plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(f"{TARGET_SCHEMA}.query_plans.id", ondelete="CASCADE"),
            nullable=False,
            comment="원본 쿼리 계획 참조",
        ),
        sa.Column("ai_model", sa.String(100), nullable=False, comment="사용된 AI 모델명"),
        sa.Column("model_version", sa.String(50), nullable=True, comment="모델 버전"),
        sa.Column("optimized_query", sa.Text, nullable=False, comment="최적화된 SQL 쿼리"),
        sa.Column("optimization_rationale", sa.Text, nullable=False, comment="최적화 근거 설명"),
        sa.Column(
            "estimated_cost_reduction",
            sa.Float,
            nullable=True,
            comment="예상 비용 절감률 (%)",
        ),
        sa.Column(
            "estimated_time_reduction",
            sa.Float,
            nullable=True,
            comment="예상 시간 단축률 (%)",
        ),
        sa.Column(
            "optimized_total_cost",
            sa.Float,
            nullable=True,
            comment="최적화 쿼리 예상 총 비용",
        ),
        sa.Column(
            "optimized_execution_time_ms",
            sa.Float,
            nullable=True,
            comment="최적화 쿼리 실제 실행 시간 (ms)",
        ),
        sa.Column(
            "optimization_category",
            sa.String(50),
            nullable=True,
            comment="최적화 카테고리 (index/join/subquery 등)",
        ),
        sa.Column(
            "confidence_score",
            sa.Float,
            nullable=False,
            server_default="0.0",
            comment="AI 신뢰도 점수 (0.0-1.0)",
        ),
        sa.Column(
            "applied_techniques",
            postgresql.JSONB,
            nullable=True,
            comment="적용된 최적화 기법 목록",
        ),
        sa.Column(
            "changes_summary",
            postgresql.JSONB,
            nullable=True,
            comment="변경사항 요약 (before/after)",
        ),
        sa.Column(
            "risk_assessment",
            sa.String(20),
            nullable=False,
            server_default="medium",
            comment="위험도 평가 (low/medium/high)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            comment="생성 시각",
        ),
        comment="AI 기반 쿼리 최적화 결과 테이블",
        schema=TARGET_SCHEMA,
    )

    # 인덱스 생성
    op.create_index(
        "ix_optimized_queries_original_plan_id",
        "optimized_queries",
        ["original_plan_id"],
        schema=TARGET_SCHEMA,
    )
    op.create_index(
        "ix_optimized_queries_ai_model",
        "optimized_queries",
        ["ai_model"],
        schema=TARGET_SCHEMA,
    )
    op.create_index(
        "ix_optimized_queries_created_at",
        "optimized_queries",
        ["created_at"],
        schema=TARGET_SCHEMA,
    )
    op.create_index(
        "ix_optimized_queries_confidence_score",
        "optimized_queries",
        ["confidence_score"],
        schema=TARGET_SCHEMA,
    )


def downgrade() -> None:
    """스키마 다운그레이드: optimized_queries 테이블 삭제."""
    op.drop_table("optimized_queries", schema=TARGET_SCHEMA)
