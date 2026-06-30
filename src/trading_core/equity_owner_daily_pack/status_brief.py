"""Owner daily status brief."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_status_brief(*, paths: ProjectPaths, as_of_date: str) -> dict:
    ops_summary = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_summary.json")
    issue = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_issue_summary_refresh.json")
    action = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_action_summary_refresh.json")
    blocking_count = len(issue.get("blocking_issues", []))
    warning_count = len(issue.get("warning_issues", []))
    top_step = _first_step(paths, as_of_date)
    return {
        "brief_id": "A-SHARE-OWNER-DAILY-STATUS-BRIEF",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "overall_status": ops_summary.get("overall_status"),
        "ops_health_score": ops_summary.get("ops_health_score"),
        "ops_health_grade": ops_summary.get("ops_health_grade"),
        "blocking_count": blocking_count,
        "warning_count": warning_count,
        "safe_action_count": action.get("safe_action_count", 0),
        "automatic_action_count": action.get("automatic_action_count", 0),
        "business_output_drift_count": ops_summary.get("business_output_drift_count"),
        "protected_path_modifications_detected": ops_summary.get("protected_path_modifications_detected"),
        "top_owner_message_zh": "今日 owner 先看 build-output ops refresh、warning/issue 和 protected path 状态。",
        "top_next_step_zh": top_step,
        "research_only": True,
        "virtual_only": True,
        "not_trade_instruction": True,
    }


def _first_step(paths: ProjectPaths, as_of_date: str) -> str:
    steps = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_owner_next_steps_refresh.json")
    for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]:
        values = steps.get(key, [])
        if values:
            return values[0]
    return "无需自动操作；按每日运行手册人工复核。"

