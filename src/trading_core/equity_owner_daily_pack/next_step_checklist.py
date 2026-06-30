"""Owner next-step checklist."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_STEP_MARKERS = ["下单", "买入", "卖出", "broker", "实盘", "order preview", "调仓"]


def build_next_step_checklist(*, paths: ProjectPaths, as_of_date: str) -> dict:
    source = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_owner_next_steps_refresh.json")
    result = {
        "checklist_id": "A-SHARE-OWNER-NEXT-STEP-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "do_now": _filter(source.get("do_now", [])),
        "review_today": _filter(source.get("review_today", [])),
        "wait_for_more_history": _filter(source.get("wait_for_more_history", [])),
        "developer_follow_up": _filter(source.get("developer_follow_up", [])),
        "no_action_required": _filter(source.get("no_action_required", [])),
        "excluded_trade_action_steps": _excluded(source),
        "automatic_action_count": 0,
        "not_trade_instruction": True,
    }
    result["overall_passed"] = not result["excluded_trade_action_steps"]
    result["blocking_reasons"] = ["owner_next_step_trade_action_present"] if result["excluded_trade_action_steps"] else []
    return result


def _filter(steps: list[str]) -> list[str]:
    return [step for step in steps if not any(marker.lower() in step.lower() for marker in FORBIDDEN_STEP_MARKERS)]


def _excluded(source: dict) -> list[str]:
    excluded = []
    for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]:
        for step in source.get(key, []):
            if any(marker.lower() in step.lower() for marker in FORBIDDEN_STEP_MARKERS):
                excluded.append(step)
    return excluded

