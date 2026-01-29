"""Initial schema - 5 tables for query analysis.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2025-01-29

테이블 구성:
- analysis_sessions: 분석 세션
- query_plans: 쿼리 실행 계획
- query_plan_nodes: 실행 계획 노드 (계층 구조)
- optimization_suggestions: 최적화 제안
- query_statistics: 쿼리 통계 집계
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 스키마 설정
TARGET_SCHEMA = get_settings().DB_SCHEMA


def upgrade() -> None:
    """스키마 업그레이드: 5개 테이블 및 인덱스 생성."""
    # PostgreSQL 13+는 gen_random_uuid()가 내장되어 있음 (uuid-ossp 확장 불필요)

    # 1. analysis_sessions 테이블 생성
    op.create_table(
        "analysis_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), comment="세션 식별자"),
        sa.Column("name", sa.String(255), nullable=False, comment="세션 이름"),
        sa.Column("description", sa.Text, nullable=True, comment="세션 설명"),
        sa.Column("target_database", sa.String(255), nullable=True, comment="분석 대상 DB명"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", comment="상태 (active/completed/archived)"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="생성 시각"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="수정 시각"),
        comment="분석 세션 테이블",
        schema=TARGET_SCHEMA,
    )

    op.create_index("ix_sessions_status", "analysis_sessions", ["status"], schema=TARGET_SCHEMA)
    op.create_index("ix_sessions_created_at", "analysis_sessions", ["created_at"], schema=TARGET_SCHEMA)

    # 2. query_plans 테이블 생성
    op.create_table(
        "query_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), comment="고유 식별자"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey(f"{TARGET_SCHEMA}.analysis_sessions.id", ondelete="SET NULL"), nullable=True, comment="분석 세션 참조"),
        sa.Column("query_hash", sa.String(64), nullable=False, comment="쿼리 해시 (SHA-256)"),
        sa.Column("query", sa.Text, nullable=False, comment="분석 대상 SQL"),
        sa.Column("plan_raw", postgresql.JSONB, nullable=False, comment="EXPLAIN JSON 원본"),
        sa.Column("node_type", sa.String(50), nullable=False, comment="최상위 노드 유형"),
        sa.Column("startup_cost", sa.Float, nullable=False, server_default="0.0", comment="시작 비용"),
        sa.Column("total_cost", sa.Float, nullable=False, server_default="0.0", comment="총 비용"),
        sa.Column("plan_rows", sa.Integer, nullable=False, server_default="0", comment="예상 행 수"),
        sa.Column("plan_width", sa.Integer, nullable=False, server_default="0", comment="예상 행 폭"),
        sa.Column("actual_time_ms", sa.Float, nullable=True, comment="실제 실행 시간 (ms)"),
        sa.Column("planning_time_ms", sa.Float, nullable=True, comment="계획 수립 시간 (ms)"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="생성 시각"),
        comment="쿼리 실행 계획 테이블",
        schema=TARGET_SCHEMA,
    )

    op.create_index("ix_query_plans_session_id", "query_plans", ["session_id"], schema=TARGET_SCHEMA)
    op.create_index("ix_query_plans_query_hash", "query_plans", ["query_hash"], schema=TARGET_SCHEMA)
    op.create_index("ix_query_plans_created_at", "query_plans", ["created_at"], schema=TARGET_SCHEMA)
    op.create_index("ix_query_plans_node_type", "query_plans", ["node_type"], schema=TARGET_SCHEMA)
    op.create_index("ix_query_plans_total_cost", "query_plans", ["total_cost"], schema=TARGET_SCHEMA)

    # 3. query_plan_nodes 테이블 생성 (self-reference)
    op.create_table(
        "query_plan_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), comment="노드 식별자"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey(f"{TARGET_SCHEMA}.query_plans.id", ondelete="CASCADE"), nullable=False, comment="상위 계획 참조"),
        sa.Column("parent_node_id", postgresql.UUID(as_uuid=True), nullable=True, comment="부모 노드 (self-reference)"),
        sa.Column("depth", sa.Integer, nullable=False, server_default="0", comment="트리 깊이"),
        sa.Column("node_order", sa.Integer, nullable=False, server_default="0", comment="동일 깊이 내 순서"),
        sa.Column("node_type", sa.String(50), nullable=False, comment="노드 유형"),
        sa.Column("relation_name", sa.String(255), nullable=True, comment="대상 테이블/인덱스명"),
        sa.Column("startup_cost", sa.Float, nullable=False, server_default="0.0", comment="노드 시작 비용"),
        sa.Column("total_cost", sa.Float, nullable=False, server_default="0.0", comment="노드 총 비용"),
        sa.Column("plan_rows", sa.Integer, nullable=False, server_default="0", comment="예상 행 수"),
        sa.Column("actual_rows", sa.Integer, nullable=True, comment="실제 행 수"),
        sa.Column("loops", sa.Integer, nullable=False, server_default="1", comment="반복 횟수"),
        sa.Column("node_data", postgresql.JSONB, nullable=True, comment="노드 추가 데이터"),
        comment="실행 계획 노드 테이블",
        schema=TARGET_SCHEMA,
    )

    # Self-reference 외래키는 테이블 생성 후 추가
    op.create_foreign_key(
        "fk_plan_nodes_parent",
        "query_plan_nodes",
        "query_plan_nodes",
        ["parent_node_id"],
        ["id"],
        ondelete="CASCADE",
        source_schema=TARGET_SCHEMA,
        referent_schema=TARGET_SCHEMA,
    )

    op.create_index("ix_plan_nodes_plan_id", "query_plan_nodes", ["plan_id"], schema=TARGET_SCHEMA)
    op.create_index("ix_plan_nodes_parent_node_id", "query_plan_nodes", ["parent_node_id"], schema=TARGET_SCHEMA)
    op.create_index("ix_plan_nodes_node_type", "query_plan_nodes", ["node_type"], schema=TARGET_SCHEMA)

    # 4. optimization_suggestions 테이블 생성
    op.create_table(
        "optimization_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), comment="제안 식별자"),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey(f"{TARGET_SCHEMA}.query_plans.id", ondelete="CASCADE"), nullable=False, comment="관련 계획"),
        sa.Column("suggestion_type", sa.String(50), nullable=False, comment="제안 유형"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info", comment="심각도 (info/warning/critical)"),
        sa.Column("title", sa.String(255), nullable=False, comment="제안 제목"),
        sa.Column("description", sa.Text, nullable=False, comment="상세 설명"),
        sa.Column("recommendation", sa.Text, nullable=True, comment="권장 조치"),
        sa.Column("estimated_improvement", sa.Float, nullable=True, comment="예상 개선율 (%)"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="생성 시각"),
        comment="최적화 제안 테이블",
        schema=TARGET_SCHEMA,
    )

    op.create_index("ix_suggestions_plan_id", "optimization_suggestions", ["plan_id"], schema=TARGET_SCHEMA)
    op.create_index("ix_suggestions_severity", "optimization_suggestions", ["severity"], schema=TARGET_SCHEMA)

    # 5. query_statistics 테이블 생성
    op.create_table(
        "query_statistics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), comment="통계 식별자"),
        sa.Column("query_hash", sa.String(64), nullable=False, unique=True, comment="쿼리 해시"),
        sa.Column("call_count", sa.Integer, nullable=False, server_default="1", comment="호출 횟수"),
        sa.Column("total_time_ms", sa.Float, nullable=False, server_default="0.0", comment="총 실행 시간 (ms)"),
        sa.Column("min_time_ms", sa.Float, nullable=False, server_default="0.0", comment="최소 실행 시간 (ms)"),
        sa.Column("max_time_ms", sa.Float, nullable=False, server_default="0.0", comment="최대 실행 시간 (ms)"),
        sa.Column("avg_time_ms", sa.Float, nullable=False, server_default="0.0", comment="평균 실행 시간 (ms)"),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="최초 발견 시각"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()"), comment="최근 발견 시각"),
        comment="쿼리 통계 집계 테이블",
        schema=TARGET_SCHEMA,
    )

    op.create_index("ix_statistics_query_hash", "query_statistics", ["query_hash"], unique=True, schema=TARGET_SCHEMA)
    op.create_index("ix_statistics_avg_time_ms", "query_statistics", ["avg_time_ms"], schema=TARGET_SCHEMA)


def downgrade() -> None:
    """스키마 다운그레이드: 5개 테이블 삭제."""
    # 테이블 삭제 (외래키 의존성 역순)
    op.drop_table("query_statistics", schema=TARGET_SCHEMA)
    op.drop_table("optimization_suggestions", schema=TARGET_SCHEMA)
    op.drop_table("query_plan_nodes", schema=TARGET_SCHEMA)
    op.drop_table("query_plans", schema=TARGET_SCHEMA)
    op.drop_table("analysis_sessions", schema=TARGET_SCHEMA)

    # UUID 확장은 다른 곳에서 사용할 수 있으므로 삭제하지 않음
