from __future__ import annotations

from pathlib import Path

import pytest

from a_share_daily_stock_selection_briefing_test_utils import make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_briefings.briefing_inputs import load_briefing_inputs


def test_briefing_inputs_read_existing_candidate_score_and_portfolio_artifacts(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)

    inputs = load_briefing_inputs(paths=paths, as_of_date=AS_OF_DATE)

    assert inputs.as_of_date == AS_OF_DATE
    assert inputs.candidate_manifest["target_version"] == "v0.7.5-a-share-candidate-generation-system"
    assert inputs.score_manifest["target_version"] == "v0.7.4-a-share-long-mid-short-scoring-system"
    assert inputs.portfolio_manifest["target_version"] == "v0.7.6-a-share-virtual-portfolio-construction"
    assert len(inputs.long_candidates) == 2
    assert len(inputs.long_virtual_portfolio) == 2


def test_briefing_inputs_fail_closed_unless_latest_artifact_date_allowed(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)

    with pytest.raises(ValueError):
        load_briefing_inputs(paths=paths, as_of_date="2026-06-27")

    inputs = load_briefing_inputs(paths=paths, as_of_date="2026-06-27", allow_latest_artifact_date=True)
    assert inputs.as_of_date == AS_OF_DATE
    assert inputs.requested_as_of_date == "2026-06-27"
