from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_local_schedule_policy_and_templates(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    policy = v12_json(paths, "v12_local_schedule_policy")
    templates = v12_json(paths, "v12_scheduler_template_plan")

    assert result["local_schedule_policy_generated"] is True
    assert policy["default_run_time"] == "15:45"
    assert policy["timezone"] == "Asia/Shanghai"
    assert policy["calendar_unavailable_behavior"] == "fail_closed"
    assert templates["manual_cron_template"]
    assert templates["manual_windows_task_scheduler_template"]
    assert templates["silent_cron_installation"] is False
    assert templates["silent_windows_task_scheduler_installation"] is False
    assert result["silent_scheduler_installation"] is False


def test_v12_trading_day_plan_and_non_trading_safe_skip(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    run_a_share_v12_continuous_ops(paths=paths, as_of_date="2026-07-04", simulation_only=True)
    plan = v12_json(paths, "v12_trading_day_run_plan", as_of_date="2026-07-04")

    assert plan["trading_day_run_plan_generated"] is True
    assert plan["is_trading_day"] is False
    assert plan["safe_skip"] is True
    assert plan["safe_skip_reason"] == "non_trading_day_or_holiday"
    assert plan["next_eligible_run_date"] == "2026-07-06"


def test_v12_schedule_dry_run_and_missed_duplicate_detection(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True, dry_run=True)
    dry = v12_json(paths, "v12_schedule_dry_run_result", dry_run=True)
    lock = v12_json(paths, "v12_run_lock_and_idempotency_result", dry_run=True)

    assert result["schedule_dry_run_passed"] is True
    assert dry["would_run"] is True
    assert lock["missed_run_detection"] is True
    assert lock["duplicate_run_prevention"] is True
    assert lock["stale_lock_detection"] is True
