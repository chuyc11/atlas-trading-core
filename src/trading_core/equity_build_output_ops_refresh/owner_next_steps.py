"""Owner next steps refresh for build-output ops."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_STEP_MARKERS = ["下单", "买入", "卖出", "broker", "实盘", "order preview"]


def build_owner_next_steps_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    original = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_owner_next_steps.json")
    payload = {
        "next_steps_id": "A-SHARE-BUILD-OUTPUT-OWNER-NEXT-STEPS-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "owner_next_steps_refresh_performed": True,
        "do_now": _filter_steps(original.get("do_now", [])),
        "review_today": _filter_steps(original.get("review_today", [])),
        "wait_for_more_history": _filter_steps(original.get("wait_for_more_history", [])),
        "developer_follow_up": _filter_steps(original.get("developer_follow_up", [])),
        "no_action_required": _filter_steps(original.get("no_action_required", [])),
        "excluded_trade_action_steps": _excluded(original),
    }
    payload["overall_passed"] = not payload["excluded_trade_action_steps"]
    payload["blocking_reasons"] = ["owner_next_steps_trade_action_present"] if payload["excluded_trade_action_steps"] else []
    return payload


def _filter_steps(steps: list[str]) -> list[str]:
    return [step for step in steps if not any(marker.lower() in step.lower() for marker in FORBIDDEN_STEP_MARKERS)]


def _excluded(original: dict) -> list[str]:
    excluded = []
    for key in ["do_now", "review_today", "wait_for_more_history", "developer_follow_up", "no_action_required"]:
        for step in original.get(key, []):
            if any(marker.lower() in step.lower() for marker in FORBIDDEN_STEP_MARKERS):
                excluded.append(step)
    return excluded

