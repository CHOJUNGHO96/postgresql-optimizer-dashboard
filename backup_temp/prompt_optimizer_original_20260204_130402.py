"""프롬프트 최적화 및 EXPLAIN JSON 압축 유틸리티."""

import json
import logging
from typing import Any
from copy import deepcopy

from .token_counter import count_tokens, count_prompt_tokens

logger = logging.getLogger(__name__)


# 고비용 노드 타입 (높은 우선순위로 보존)
EXPENSIVE_NODE_TYPES = {
    "Seq Scan",
    "Nested Loop",
    "Hash Join",
    "Merge Join",
    "Aggregate",
    "Sort",
    "Subquery Scan",
}

# 압축 시 제거할 필드 (단계별)
COMPRESSION_FIELDS = {
    "mild": [
        "Shared Hit Blocks",
        "Shared Read Blocks",
        "Shared Dirtied Blocks",
        "Shared Written Blocks",
        "Local Hit Blocks",
        "Local Read Blocks",
        "Local Dirtied Blocks",
        "Local Written Blocks",
        "Temp Read Blocks",
        "Temp Written Blocks",
        "I/O Read Time",
        "I/O Write Time",
        "Workers",
        "Workers Planned",
        "Workers Launched",
    ],
    "moderate": [
        "Output",
        "Schema",
        "Alias",
        "Subplan Name",
    ],
    "aggressive": [
        "Filter",
        "Join Type",
        "Hash Cond",
        "Merge Cond",
        "Index Cond",
        "Recheck Cond",
        "Sort Key",
        "Group Key",
    ],
}

# 절대 제거하면 안 되는 필드
PRESERVE_FIELDS = {
    "Node Type",
    "Total Cost",
    "Startup Cost",
    "Plan Rows",
    "Plan Width",
    "Actual Rows",
    "Actual Loops",
    "Actual Total Time",
    "Actual Startup Time",
    "Relation Name",  # 테이블 식별에 필수
    "Index Name",  # 인덱스 최적화에 필수
    "Plans",  # 자식 노드 (재귀 압축)
}


class PromptOptimizer:
    """프롬프트 최적화 및 EXPLAIN JSON 압축."""

    @staticmethod
    def _is_expensive_node(node: dict[str, Any]) -> bool:
        """고비용 노드 여부 확인.

        Args:
            node: EXPLAIN JSON 노드

        Returns:
            bool: 고비용 노드 여부
        """
        node_type = node.get("Node Type", "")
        return node_type in EXPENSIVE_NODE_TYPES

    @staticmethod
    def _compress_node(
        node: dict[str, Any],
        level: str = "mild",
    ) -> dict[str, Any]:
        """단일 노드 압축.

        Args:
            node: EXPLAIN JSON 노드
            level: 압축 레벨 (mild, moderate, aggressive)

        Returns:
            dict: 압축된 노드
        """
        compressed = {}
        is_expensive = PromptOptimizer._is_expensive_node(node)

        # 절대 보존 필드
        for field in PRESERVE_FIELDS:
            if field in node:
                compressed[field] = node[field]

        # 압축 레벨에 따른 필드 제거
        fields_to_remove = set()
        if level in ["mild", "moderate", "aggressive"]:
            fields_to_remove.update(COMPRESSION_FIELDS["mild"])
        if level in ["moderate", "aggressive"]:
            fields_to_remove.update(COMPRESSION_FIELDS["moderate"])
        if level == "aggressive":
            fields_to_remove.update(COMPRESSION_FIELDS["aggressive"])

        # 고비용 노드는 덜 공격적으로 압축
        if is_expensive and level == "aggressive":
            # Filter, Join Cond 등은 보존
            fields_to_remove -= set(COMPRESSION_FIELDS["aggressive"])

        # 나머지 필드 추가 (제거 대상 제외)
        for key, value in node.items():
            if key not in fields_to_remove and key not in compressed:
                compressed[key] = value

        # 자식 노드 재귀 압축
        if "Plans" in compressed:
            compressed["Plans"] = [
                PromptOptimizer._compress_node(child, level)
                for child in compressed["Plans"]
            ]

        return compressed

    @staticmethod
    def compress_explain_json(
        explain_json: dict[str, Any],
        target_reduction: float,
    ) -> dict[str, Any]:
        """EXPLAIN JSON 압축.

        Args:
            explain_json: 원본 EXPLAIN JSON
            target_reduction: 목표 감소율 (0.0 ~ 1.0)

        Returns:
            dict: 압축된 EXPLAIN JSON
        """
        # 압축 레벨 결정
        if target_reduction < 0.2:
            level = "mild"
        elif target_reduction < 0.4:
            level = "moderate"
        else:
            level = "aggressive"

        logger.info(f"Compressing EXPLAIN JSON with {level} level (target: {target_reduction:.1%})")

        # Plan 배열 압축
        if isinstance(explain_json, list) and len(explain_json) > 0:
            plan = explain_json[0].get("Plan", {})
            compressed_plan = PromptOptimizer._compress_node(plan, level)
            return [{"Plan": compressed_plan}]

        # 단일 Plan 객체 압축
        if "Plan" in explain_json:
            compressed_plan = PromptOptimizer._compress_node(explain_json["Plan"], level)
            return {"Plan": compressed_plan}

        return explain_json

    @staticmethod
    def compress_to_target_tokens(
        original_query: str,
        explain_json: dict[str, Any],
        schema_context: str | None,
        target_tokens: int,
        model_family: str = "anthropic",
    ) -> tuple[dict[str, Any], str | None]:
        """목표 토큰 수에 맞춰 자동 압축.

        Args:
            original_query: 원본 SQL 쿼리
            explain_json: EXPLAIN JSON
            schema_context: 스키마 컨텍스트
            target_tokens: 목표 토큰 수
            model_family: 모델 패밀리

        Returns:
            tuple: (압축된 EXPLAIN JSON, 압축된 스키마 컨텍스트 또는 None)

        Raises:
            ValueError: 압축 후에도 목표 토큰 초과
        """
        # 현재 토큰 수
        current_tokens = count_prompt_tokens(
            original_query,
            explain_json,
            schema_context,
            model_family,
        )

        logger.info(f"Current tokens: {current_tokens:,}, Target: {target_tokens:,}")

        if current_tokens <= target_tokens:
            return explain_json, schema_context

        # 1단계: 스키마 컨텍스트 제거 시도
        if schema_context:
            tokens_without_schema = count_prompt_tokens(
                original_query,
                explain_json,
                None,
                model_family,
            )
            logger.info(f"Tokens without schema: {tokens_without_schema:,}")

            if tokens_without_schema <= target_tokens:
                logger.info("Removed schema context to meet token limit")
                return explain_json, None

        # 2단계: EXPLAIN JSON 압축 (mild)
        target_reduction = (current_tokens - target_tokens) / current_tokens
        compressed_json = PromptOptimizer.compress_explain_json(
            explain_json,
            max(0.15, target_reduction),
        )

        new_tokens = count_prompt_tokens(
            original_query,
            compressed_json,
            None,  # 스키마는 이미 제거 시도
            model_family,
        )
        logger.info(f"Tokens after mild compression: {new_tokens:,}")

        if new_tokens <= target_tokens:
            return compressed_json, None

        # 3단계: 더 공격적인 압축 (moderate)
        compressed_json = PromptOptimizer.compress_explain_json(
            explain_json,
            max(0.35, target_reduction),
        )

        new_tokens = count_prompt_tokens(
            original_query,
            compressed_json,
            None,
            model_family,
        )
        logger.info(f"Tokens after moderate compression: {new_tokens:,}")

        if new_tokens <= target_tokens:
            return compressed_json, None

        # 4단계: 최대 압축 (aggressive)
        compressed_json = PromptOptimizer.compress_explain_json(
            explain_json,
            max(0.55, target_reduction),
        )

        new_tokens = count_prompt_tokens(
            original_query,
            compressed_json,
            None,
            model_family,
        )
        logger.info(f"Tokens after aggressive compression: {new_tokens:,}")

        if new_tokens <= target_tokens:
            return compressed_json, None

        # 압축 실패
        raise ValueError(
            f"Unable to compress to target tokens. "
            f"Final: {new_tokens:,}, Target: {target_tokens:,}"
        )
