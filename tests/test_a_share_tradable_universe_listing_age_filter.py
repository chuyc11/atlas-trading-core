from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.listing_age_filter import listing_trading_days
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe
from trading_core.equity_data_quality.common import read_frame


def test_listing_age_filter_uses_trading_days_and_excludes_new_listings(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)
    excluded = json.loads((paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "excluded_universe.json").read_text(encoding="utf-8"))
    new_listing = next(row for row in excluded if row["symbol"] == SYMBOLS["new"])
    calendar = read_frame(paths.data_dir / "equity_universe" / "trading_calendar.parquet")

    assert "new_listing_lt_120_trading_days" in new_listing["all_exclusion_reasons"]
    assert listing_trading_days("2026-06-01", "SSE", AS_OF_DATE, calendar) < 120

