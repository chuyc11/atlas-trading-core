from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import briefing_data_dir, briefing_output_dir, build_briefing_package, make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_data_quality.common import sha256_file


def test_briefing_builder_writes_json_markdown_and_does_not_regenerate_upstream(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    watched = [
        paths.data_dir / "equity_scores" / "daily" / AS_OF_DATE / "score_manifest.json",
        paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "candidate_manifest.json",
        paths.data_dir / "equity_portfolios" / "daily" / AS_OF_DATE / "portfolio_manifest.json",
    ]
    before = {path: sha256_file(path) for path in watched}

    result = build_briefing_package(paths)

    assert result["briefing_id"] == "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING"
    assert len(result["long_candidates_top10"]) == 2
    assert len(result["mid_candidates_top10"]) == 2
    assert len(result["short_candidates_top10"]) == 2
    assert (briefing_data_dir(paths) / "daily_stock_selection_briefing.json").exists()
    assert (briefing_output_dir(paths) / "DAILY_STOCK_SELECTION_BRIEFING.md").exists()
    assert {path: sha256_file(path) for path in watched} == before
    assert result["boundary"]["scores_regenerated"] is False
    assert result["boundary"]["candidates_regenerated"] is False
    assert result["boundary"]["virtual_portfolios_regenerated"] is False
