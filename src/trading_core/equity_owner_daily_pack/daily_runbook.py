"""Owner daily runbook."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION


def build_daily_runbook(*, as_of_date: str) -> dict:
    sections = [
        "打开每日状态简报",
        "检查 build-output dashboard",
        "检查 monitoring / remediation / ops refresh",
        "检查 warning / issue / safe action",
        "检查 protected path 状态",
        "检查 source trace 和 boundary",
        "阅读 research output digest",
        "记录 owner notes",
        "判断是否需要 developer follow-up",
        "确认不执行任何交易动作",
    ]
    commands = [
        f"python -m trading_core.cli audit-a-share-build-output-owner-dashboard --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-build-output-ops-refresh --as-of-date {as_of_date}",
        f"python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date {as_of_date}",
    ]
    return {
        "runbook_id": "A-SHARE-OWNER-DAILY-RUNBOOK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "sections": sections,
        "safe_audit_only_commands": commands,
        "manual_review_checklist": [
            "确认所有 audit 仍为 passed",
            "确认 warning / issue 已分类",
            "确认 safe action 均为人工复核",
            "确认 protected path 无修改",
            "确认 boundary clean",
        ],
        "known_non_blocking_items": ["metadata_hash_drift_non_blocking", "timestamp_only_drift_non_blocking"],
        "developer_escalation_conditions": ["blocking_count > 0", "source_trace incomplete", "boundary not clean"],
        "what_not_to_do": [
            "do not connect broker",
            "do not read real account",
            "do not place real orders",
            "do not generate order preview",
            "do not call old run-daily",
        ],
        "commands_executed": [],
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
    }

