"""Add optimization_tasks table for async processing

Revision ID: 004
Revises: 003
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004_add_optimization_tasks"
down_revision = "003_add_optimized_queries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add optimization_tasks table."""
    op.create_table(
        "optimization_tasks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            comment="작업 식별자",
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="원본 쿼리 계획 참조",
        ),
        sa.Column(
            "ai_model", sa.String(100), nullable=False, comment="사용할 AI 모델명"
        ),
        sa.Column(
            "validate_optimization",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="최적화 검증 여부",
        ),
        sa.Column(
            "include_schema_context",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="스키마 컨텍스트 포함 여부",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
            comment="작업 상태",
        ),
        sa.Column(
            "optimization_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="완료된 최적화 참조",
        ),
        sa.Column("error_message", sa.Text(), nullable=True, comment="에러 메시지"),
        sa.Column("error_type", sa.String(50), nullable=True, comment="에러 타입"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment="생성 시각",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="시작 시각",
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="완료 시각",
        ),
        sa.Column(
            "estimated_duration_seconds",
            sa.Integer(),
            nullable=True,
            comment="예상 소요 시간(초)",
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["pgs_analysis.query_plans.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["optimization_id"],
            ["pgs_analysis.optimized_queries.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="optimization_tasks_status_check",
        ),
        schema="pgs_analysis",
        comment="백그라운드 최적화 작업 추적 테이블",
    )

    # Create indexes
    op.create_index(
        "idx_optimization_tasks_plan_id",
        "optimization_tasks",
        ["plan_id"],
        schema="pgs_analysis",
    )
    op.create_index(
        "idx_optimization_tasks_status",
        "optimization_tasks",
        ["status"],
        schema="pgs_analysis",
    )
    op.create_index(
        "idx_optimization_tasks_status_created",
        "optimization_tasks",
        ["status", "created_at"],
        schema="pgs_analysis",
    )


def downgrade() -> None:
    """Remove optimization_tasks table."""
    op.drop_index(
        "idx_optimization_tasks_status_created",
        table_name="optimization_tasks",
        schema="pgs_analysis",
    )
    op.drop_index(
        "idx_optimization_tasks_status",
        table_name="optimization_tasks",
        schema="pgs_analysis",
    )
    op.drop_index(
        "idx_optimization_tasks_plan_id",
        table_name="optimization_tasks",
        schema="pgs_analysis",
    )
    op.drop_table("optimization_tasks", schema="pgs_analysis")
