from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_bucket_assignment_and_counts_sum_to_input(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    result = build_a_share_tradable_universe(paths=paths)
    data_dir = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE
    caution = json.loads((data_dir / "caution_universe.json").read_text(encoding="utf-8"))
    unknown = json.loads((data_dir / "unknown_status_universe.json").read_text(encoding="utf-8"))
    excluded = json.loads((data_dir / "excluded_universe.json").read_text(encoding="utf-8"))
    counts = result["counts"]

    assert counts["strict_tradable_count"] + counts["caution_count"] + counts["excluded_count"] + counts["unknown_status_count"] == counts["input_symbols"]
    assert {row["symbol"] for row in caution} == {SYMBOLS["unknown_st"]}
    assert {row["symbol"] for row in unknown} == {SYMBOLS["missing_market_cap"]}
    assert SYMBOLS["st"] in {row["symbol"] for row in excluded}
    assert all(row["primary_exclusion_reason"] for row in excluded)
    assert len({row["symbol"] for row in caution + unknown + excluded}) == len(caution + unknown + excluded)

