"""Add title column to query_plans table.

Revision ID: 002_add_title_column
Revises: 001_initial_schema
Create Date: 2025-01-29

쿼리 분석 시 제목을 저장할 수 있도록 title 컬럼 추가.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision: str = "002_add_title_column"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 스키마 설정
TARGET_SCHEMA = get_settings().DB_SCHEMA


def upgrade() -> None:
    """title 컬럼 추가."""
    op.add_column(
        "query_plans",
        sa.Column("title", sa.String(255), nullable=True, comment="쿼리 제목"),
        schema=TARGET_SCHEMA,
    )


def downgrade() -> None:
    """title 컬럼 삭제."""
    op.drop_column("query_plans", "title", schema=TARGET_SCHEMA)
