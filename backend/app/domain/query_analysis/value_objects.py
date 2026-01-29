"""쿼리 분석 도메인 값 객체."""

from enum import Enum

from pydantic import BaseModel, Field


class PlanNodeType(str, Enum):
    """실행 계획 노드 유형."""

    SEQ_SCAN = "Seq Scan"
    INDEX_SCAN = "Index Scan"
    INDEX_ONLY_SCAN = "Index Only Scan"
    BITMAP_INDEX_SCAN = "Bitmap Index Scan"
    BITMAP_HEAP_SCAN = "Bitmap Heap Scan"
    NESTED_LOOP = "Nested Loop"
    HASH_JOIN = "Hash Join"
    MERGE_JOIN = "Merge Join"
    SORT = "Sort"
    HASH = "Hash"
    AGGREGATE = "Aggregate"
    GROUP_AGGREGATE = "Group Aggregate"
    HASH_AGGREGATE = "HashAggregate"
    LIMIT = "Limit"
    APPEND = "Append"
    MATERIALIZE = "Materialize"
    SUBQUERY_SCAN = "Subquery Scan"
    CTE_SCAN = "CTE Scan"
    RESULT = "Result"
    GATHER = "Gather"
    GATHER_MERGE = "Gather Merge"
    OTHER = "Other"


class CostEstimate(BaseModel):
    """실행 계획 비용 추정치."""

    startup_cost: float = Field(ge=0, description="시작 비용")
    total_cost: float = Field(ge=0, description="총 비용")
    plan_rows: int = Field(ge=0, description="예상 행 수")
    plan_width: int = Field(ge=0, description="예상 행 폭(바이트)")
