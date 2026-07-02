from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_factor_and_candidate_quality_diagnostics(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)

    factor = v13_json(paths, "v13_factor_quality_diagnostics")
    candidate = v13_json(paths, "v13_candidate_quality_diagnostics")

    assert factor["factor_quality_diagnostics_generated"] is True
    assert factor["information_coefficient_status"] == "not_available_without_validated_history"
    assert candidate["candidate_quality_diagnostics_generated"] is True
    assert candidate["no_buy_sell_recommendations_generated"] is True
    assert candidate["sector_concentration_warning"] is True
