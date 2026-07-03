from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_diversity_redundancy_no_fabricated_correlation(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    diversity = v22_json(paths, "v22_diversity_redundancy_diagnostics")

    assert result["diversity_redundancy_diagnostics_generated"] is True
    assert diversity["highly_correlated_component_warning"] is True
    assert diversity["correlation_covariance_fabricated"] is False
    assert diversity["owner_report_displays_limitation"] is True
    assert result["ensemble_correlation_fabricated"] is False
