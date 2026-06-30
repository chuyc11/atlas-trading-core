"""Blocked daily pack owner notice."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_blocked_daily_pack_owner_notice(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any]) -> dict[str, Any]:
    return {
        "notice_id": "A-SHARE-BLOCKED-DAILY-PACK-OWNER-NOTICE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "daily_pack_owner_operationally_acceptable": False,
        "source_gate_decision": intake.get("source_gate_decision"),
        "message_zh": "当前 daily pack 未达到 owner-operationally-acceptable。audit passed 代表阻塞状态被正确表达，不代表 gate 放行。",
        "score_statement": f"score {intake.get('actual_owner_readiness_score')} is below threshold {intake.get('minimum_owner_readiness_score')}",
        "blocked_does_not_mean_trading_issue": True,
        "blocked_does_not_mean_broker_or_order_activity_occurred": True,
        "owner_should_review_exception_workflow": True,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "not_live_trading_ready": True,
    }
