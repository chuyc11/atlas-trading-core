from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_liquidity_filter_excludes_low_amount_and_estimates_missing_amount(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)
    data_dir = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE
    excluded = json.loads((data_dir / "excluded_universe.json").read_text(encoding="utf-8"))
    tradable = json.loads((data_dir / "tradable_universe.json").read_text(encoding="utf-8"))

    low_liquidity = next(row for row in excluded if row["symbol"] == SYMBOLS["low_liquidity"])
    estimated = next(row for row in tradable if row["symbol"] == SYMBOLS["estimated_amount"])
    assert "avg_amount_20d_below_threshold" in low_liquidity["all_exclusion_reasons"]
    assert "avg_amount_60d_below_threshold" in low_liquidity["all_exclusion_reasons"]
    assert estimated["estimated_amount"] is True
    assert estimated["avg_amount_20d"] >= 50_000_000

