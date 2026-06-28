from __future__ import annotations

import json
from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import audit_tracking_package, build_tracking_package, make_tracking_paths, tracking_data_dir, tracking_output_dir


def test_tracking_boundaries_are_false_for_real_trading_surfaces(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    audit = audit_tracking_package(paths)

    assert audit["checks"]["no_real_account_fields_present"] is True
    assert audit["checks"]["no_buy_sell_signal_artifacts_generated"] is True
    assert audit["checks"]["no_order_preview_generated"] is True
    assert audit["checks"]["no_broker_order_generated"] is True
    assert audit["checks"]["no_real_order_generated"] is True
    assert audit["checks"]["no_main_orders_trades_accounts_writes"] is True
    assert audit["boundary"]["paper_ledger_generated"] is True
    assert audit["boundary"]["real_portfolio_generated"] is False
    assert audit["boundary"]["buy_sell_signals_generated"] is False
    assert audit["boundary"]["order_preview_generated"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["boundary"]["model_profit_guaranteed"] is False
    assert audit["boundary"]["live_trading_ready"] is False


def test_tracking_audit_blocks_order_preview_artifact(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    (tracking_output_dir(paths) / "ORDER_PREVIEW.md").write_text("forbidden", encoding="utf-8")

    audit = audit_tracking_package(paths)

    assert audit["overall_passed"] is False
    assert "no_order_preview_generated=false" in audit["blocking_reasons"]


def test_tracking_audit_blocks_real_account_field(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot_path = tracking_data_dir(paths) / "long_holdings_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot["holdings"][0]["account_id"] = "REAL-ACCOUNT"
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")

    audit = audit_tracking_package(paths)

    assert audit["overall_passed"] is False
    assert "no_real_account_fields_present=false" in audit["blocking_reasons"]


def test_tracking_audit_blocks_forbidden_profit_wording(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    report_path = tracking_output_dir(paths) / "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md"
    report_path.write_text(report_path.read_text(encoding="utf-8") + "\nguaranteed profit\n", encoding="utf-8")

    audit = audit_tracking_package(paths)

    assert audit["overall_passed"] is False
    assert "no_profit_guarantee_wording=false" in audit["blocking_reasons"]
