from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import briefing_json, build_briefing_package, make_briefing_paths


def test_briefing_manifest_records_read_only_boundaries_and_sources(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)

    manifest = briefing_json(paths, "briefing_manifest")

    assert manifest["manifest_id"] == "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-MANIFEST"
    assert manifest["briefing_only"] is True
    assert manifest["scores_regenerated"] is False
    assert manifest["candidates_regenerated"] is False
    assert manifest["virtual_portfolios_regenerated"] is False
    assert manifest["buy_sell_signals_generated"] is False
    assert manifest["order_preview_generated"] is False
    assert manifest["input_candidate_manifest_path"].endswith("candidate_manifest.json")
    assert manifest["input_score_manifest_path"].endswith("score_manifest.json")
    assert manifest["input_portfolio_manifest_path"].endswith("portfolio_manifest.json")
