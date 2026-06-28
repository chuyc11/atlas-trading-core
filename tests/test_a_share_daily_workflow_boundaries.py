from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths, workflow_output_dir
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow


def test_daily_workflow_boundaries_no_real_trading_surfaces(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    audit = audit_a_share_daily_research_workflow(paths=paths)

    assert audit["boundary"]["call_old_run_daily"] is False
    assert audit["boundary"]["official_forward_dry_run_status_unchanged"] is True
    assert audit["boundary"]["day2_executed"] is False
    assert audit["boundary"]["run_daily_called"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["boundary"]["real_orders_placed"] is False
    assert audit["boundary"]["buy_sell_signals_generated"] is False
    assert audit["boundary"]["order_preview_generated"] is False
    assert audit["boundary"]["model_profit_guaranteed"] is False
    assert audit["boundary"]["live_trading_ready"] is False
    assert audit["checks"]["no_old_run_daily_called"] is True
    assert audit["checks"]["broker_not_connected"] is True
    assert audit["checks"]["real_orders_not_placed"] is True


def test_daily_workflow_audit_blocks_order_preview_artifact(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    (workflow_output_dir(paths) / "ORDER_PREVIEW.md").write_text("forbidden", encoding="utf-8")

    audit = audit_a_share_daily_research_workflow(paths=paths)

    assert audit["overall_passed"] is False
    assert "no_order_preview_artifact_generated=false" in audit["blocking_reasons"]
