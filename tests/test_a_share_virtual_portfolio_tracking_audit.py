from __future__ import annotations

import json
from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import audit_tracking_package, build_tracking_package, make_tracking_paths, tracking_data_dir


def test_tracking_audit_passes_clean_package(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)

    audit = audit_tracking_package(paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["counts"] == {
        "long_holdings": 2,
        "long_ledger_records": 2,
        "mid_holdings": 2,
        "mid_ledger_records": 2,
        "short_holdings": 2,
        "short_ledger_records": 2,
    }
    assert audit["nav_checks"]["long_nav"] == 1_000_000.0
    assert audit["boundary"]["virtual_tracking_only"] is True
    assert audit["boundary"]["real_orders_placed"] is False


def test_tracking_audit_blocks_forbidden_record_type(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    ledger_path = tracking_data_dir(paths) / "long_paper_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger[0]["record_type"] = "buy_order"
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")

    audit = audit_tracking_package(paths)

    assert audit["overall_passed"] is False
    assert "ledger_record_types_allowed=false" in audit["blocking_reasons"]
