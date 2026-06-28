from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths


def test_daily_workflow_boundary_check_is_research_only(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    result = build_workflow_package(paths)
    boundary = result["workflow_boundary_check"]

    assert boundary["overall_passed"] is True
    assert boundary["workflow_orchestration_only"] is True
    assert boundary["call_old_run_daily"] is False
    assert boundary["official_forward_dry_run_status_unchanged"] is True
    assert boundary["day2_executed"] is False
    assert boundary["run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["model_profit_guaranteed"] is False
    assert boundary["live_trading_ready"] is False
    assert boundary["forbidden_artifacts_present"] == []
