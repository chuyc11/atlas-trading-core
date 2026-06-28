from __future__ import annotations

from pathlib import Path

import pytest

from a_share_daily_stock_selection_briefing_test_utils import build_briefing_package, make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_tracking_test_utils import make_tracking_paths
from trading_core.equity_portfolio_tracking.tracking_inputs import load_tracking_inputs


def test_tracking_inputs_load_required_upstream_artifacts(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)

    inputs = load_tracking_inputs(paths=paths, as_of_date=AS_OF_DATE)

    assert inputs.as_of_date == AS_OF_DATE
    assert len(inputs.portfolios["long"]) == 2
    assert len(inputs.portfolios["mid"]) == 2
    assert len(inputs.portfolios["short"]) == 2
    assert not inputs.daily_prices.empty
    assert not inputs.adjusted_prices.empty
    assert not inputs.trading_calendar.empty
    assert inputs.candidate_manifest_path.exists()
    assert inputs.score_manifest_path.exists()
    assert inputs.briefing_manifest_path.exists()


def test_tracking_inputs_fail_closed_when_core_input_missing(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)

    with pytest.raises(ValueError, match="tracking inputs missing"):
        load_tracking_inputs(paths=paths, as_of_date=AS_OF_DATE)
