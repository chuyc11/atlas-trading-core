from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json
from trading_core.equity_portfolio_tracking.tracking_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def test_tracking_manifest_and_source_trace_complete(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)

    manifest = tracking_json(paths, "tracking_manifest")
    source_trace = tracking_json(paths, "tracking_source_trace")

    assert manifest["manifest_id"] == "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-MANIFEST"
    assert manifest["target_version"] == TARGET_VERSION
    assert manifest["virtual_tracking_generated"] is True
    assert manifest["paper_ledger_generated"] is True
    assert manifest["real_portfolio_generated"] is False
    assert manifest["buy_sell_signals_generated"] is False
    assert manifest["order_preview_generated"] is False
    assert manifest["recommended_next_version"] == RECOMMENDED_NEXT_VERSION
    assert set(manifest["paper_ledgers"]) == {"long", "mid", "short"}
    assert set(manifest["holdings_snapshots"]) == {"long", "mid", "short"}

    assert source_trace["source_trace_complete"] is True
    assert source_trace["virtual_portfolio_source_paths"]
    assert source_trace["candidate_manifest_source_path"].endswith("candidate_manifest.json")
    assert source_trace["score_manifest_source_path"].endswith("score_manifest.json")
    assert source_trace["briefing_manifest_source_path"].endswith("briefing_manifest.json")
    assert source_trace["price_source_path"]["adjusted_price_history"].endswith("adjusted_price_history_panel.parquet")
    assert source_trace["valuation_price_policy"] == "adjusted_close_then_close"
    assert source_trace["audit_source_path"].endswith("a_share_virtual_portfolio_tracking_audit.json")
