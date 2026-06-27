from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_test_utils import make_portfolio_paths
from trading_core.equity_portfolios.portfolio_inputs import load_portfolio_inputs


def test_virtual_portfolio_inputs_load_candidate_package(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    inputs = load_portfolio_inputs(paths=paths, as_of_date=AS_OF_DATE)

    assert inputs.as_of_date == AS_OF_DATE
    assert len(inputs.long_candidates) == 2
    assert len(inputs.mid_candidates) == 2
    assert len(inputs.short_candidates) == 2
    assert inputs.strict_symbols
    assert inputs.score_manifest["manifest_id"] == "A-SHARE-SCORING-MANIFEST"


def test_virtual_portfolio_inputs_fail_closed_missing_date(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)

    with pytest.raises(ValueError, match="candidate files not found"):
        load_portfolio_inputs(paths=paths, as_of_date="2099-01-01")
