from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.market_cap_filter import normalize_market_cap
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_market_cap_filter_excludes_low_cap_and_buckets_missing_cap_unknown(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)
    data_dir = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE
    excluded = json.loads((data_dir / "excluded_universe.json").read_text(encoding="utf-8"))
    unknown = json.loads((data_dir / "unknown_status_universe.json").read_text(encoding="utf-8"))
    low_cap = next(row for row in excluded if row["symbol"] == SYMBOLS["low_market_cap"])

    assert "total_mv_below_threshold" in low_cap["all_exclusion_reasons"]
    assert "circ_mv_below_threshold" in low_cap["all_exclusion_reasons"]
    assert {row["symbol"] for row in unknown} == {SYMBOLS["missing_market_cap"]}
    assert normalize_market_cap(300_000, 250_000, "tushare")[0] == 3_000_000_000
    assert normalize_market_cap(300_000, 250_000, "tushare")[2] is True

