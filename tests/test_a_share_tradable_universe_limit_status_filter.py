from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, SYMBOLS, make_tradable_universe_paths
from trading_core.equity_selection.limit_status_filter import estimated_limit_pct
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_limit_status_filter_excludes_one_word_limit_risk(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)
    excluded = json.loads((paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "excluded_universe.json").read_text(encoding="utf-8"))
    limit_up = next(row for row in excluded if row["symbol"] == SYMBOLS["limit_up"])

    assert "one_word_limit_up_risk" in limit_up["all_exclusion_reasons"]
    assert estimated_limit_pct("SSE_MAIN", "SSE", False) == 10.0
    assert estimated_limit_pct("STAR", "SSE", False) == 20.0
    assert estimated_limit_pct("SSE_MAIN", "SSE", True) == 5.0

