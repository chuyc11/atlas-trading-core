"""Owner readiness score gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_owner_readiness_score_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, score: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    threshold = policy["minimum_owner_readiness_score"]
    actual = score.get("score")
    valid = isinstance(actual, int) and 0 <= actual <= 100
    passed = valid and actual >= threshold and score.get("owner_readiness_used_as_trade_instruction") is False
    blocking: list[str] = []
    if not valid:
        blocking.append("owner_readiness_score_invalid")
    elif actual < threshold:
        blocking.append("owner_readiness_score_below_threshold")
    if score.get("owner_readiness_used_as_trade_instruction") is not False:
        blocking.append("owner_readiness_used_as_trade_instruction")
    return {
        "gate_id": "A-SHARE-OWNER-READINESS-SCORE-GATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "threshold": threshold,
        "actual_value": actual,
        "actual_grade": score.get("grade"),
        "passed": passed,
        "blocking_reasons": blocking,
        "warnings": [],
        "source_artifacts": ["owner_readiness_score.json"],
        "interpretation_zh": "Owner readiness score 必须达到最低运维查看质量阈值；该分数不是交易评分。",
    }
