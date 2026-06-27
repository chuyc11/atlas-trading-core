from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_build_tradable_universe_outputs_schema_and_strict_symbols(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)

    result = build_a_share_tradable_universe(paths=paths)
    tradable = json.loads((paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "tradable_universe.json").read_text(encoding="utf-8"))
    symbols = {row["symbol"] for row in tradable}

    assert result["counts"]["strict_tradable_count"] == 2
    assert SYMBOLS["strict"] in symbols
    assert SYMBOLS["estimated_amount"] in symbols
    assert SYMBOLS["st"] not in symbols
    required = {
        "as_of_date",
        "symbol",
        "industry_level_1",
        "listing_trading_days",
        "avg_amount_20d",
        "total_mv",
        "has_250d_history",
        "bucket",
        "filter_reasons",
        "created_at",
    }
    assert required.issubset(tradable[0])

