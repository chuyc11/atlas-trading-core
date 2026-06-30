"""Threshold failure explanation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_threshold_failure_explanation(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    failures = [row for row in classification.get("classifications", []) if row["severity"] in {"blocking", "developer_follow_up_required"}]
    return {
        "explanation_id": "A-SHARE-THRESHOLD-FAILURE-EXPLANATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": intake.get("source_gate_decision"),
        "blocked_gate_decision_preserved": intake.get("blocked_state_preserved"),
        "failed_threshold_count": len(failures),
        "failed_thresholds": failures,
        "plain_language_summary_zh": "当前 daily pack 被阻塞，因为 owner readiness score 低于最低运维查看阈值；audit 通过只表示阻塞状态被正确记录。",
        "not_investment_exception": True,
        "not_trade_instruction": True,
    }
