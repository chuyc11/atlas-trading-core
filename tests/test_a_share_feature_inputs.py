from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE, STRICT_SYMBOLS, make_feature_paths
from trading_core.equity_features.feature_inputs import load_feature_inputs


def test_feature_inputs_load_strict_universe_and_fail_closed_without_allow_latest(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)

    inputs = load_feature_inputs(paths=paths, as_of_date=AS_OF_DATE)

    assert inputs.as_of_date == AS_OF_DATE
    assert set(inputs.strict_universe["symbol"]) == set(STRICT_SYMBOLS)
    assert inputs.excluded_symbols == {"600004.SH"}
    assert inputs.source_dates["max_price_date_used"] == AS_OF_DATE

    with pytest.raises(ValueError, match="strict tradable universe not found"):
        load_feature_inputs(paths=paths, as_of_date="2026-06-27")

    latest = load_feature_inputs(paths=paths, as_of_date="2026-06-27", allow_latest_tradable_universe=True)
    assert latest.as_of_date == AS_OF_DATE
