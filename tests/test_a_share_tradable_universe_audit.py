from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, make_tradable_universe_paths
from trading_core.equity_selection.tradable_universe_audit import audit_a_share_tradable_universe
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_tradable_universe_audit_passes_and_fails_closed_for_missing_excluded_reasons(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    build_a_share_tradable_universe(paths=paths)

    result = audit_a_share_tradable_universe(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["recommended_next_version"] == "v0.7.3-a-share-multi-horizon-feature-engineering"

    excluded_path = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "excluded_universe.json"
    excluded = json.loads(excluded_path.read_text(encoding="utf-8"))
    excluded[0]["all_exclusion_reasons"] = []
    excluded_path.write_text(json.dumps(excluded), encoding="utf-8")
    failed = audit_a_share_tradable_universe(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert failed["overall_passed"] is False
    assert "filter_reasons_present_for_all_excluded_symbols=false" in failed["blocking_reasons"]

