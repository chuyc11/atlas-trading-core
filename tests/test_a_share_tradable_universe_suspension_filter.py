from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_suspension_and_history_filters_exclude_missing_price_and_short_history(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)
    excluded = json.loads((paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "excluded_universe.json").read_text(encoding="utf-8"))

    missing_price = next(row for row in excluded if row["symbol"] == SYMBOLS["missing_price"])
    short_history = next(row for row in excluded if row["symbol"] == SYMBOLS["short_history"])
    assert "missing_price_on_as_of_date" in missing_price["all_exclusion_reasons"]
    assert "possible_suspension" in missing_price["all_exclusion_reasons"]
    assert "insufficient_250d_history" in short_history["all_exclusion_reasons"]

