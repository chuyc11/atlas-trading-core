from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import make_history_paths
from trading_core.equity_data_quality.history_manifest import build_a_share_historical_backfill_plan


def test_a_share_historical_backfill_plan_generated_with_boundaries(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    result = build_a_share_historical_backfill_plan(paths=paths)
    assert result["plan_id"] == "A-SHARE-HISTORICAL-BACKFILL-PLAN"
    assert result["baseline_version"] == "v0.7.1-a-share-full-market-data-ingestion"
    assert result["data_backfill_only"] is True
    assert result["scores_generated"] is False
    assert result["candidates_generated"] is False
    assert result["virtual_portfolio_generated"] is False
    assert (paths.data_dir / "equity_data_quality" / "a_share_historical_backfill_plan.json").exists()
