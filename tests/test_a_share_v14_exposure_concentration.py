from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_exposure_concentration_and_leverage_boundary(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    exposure = v14_json(paths, "v14_exposure_concentration_result")

    assert result["exposure_concentration_result_generated"] is True
    assert exposure["sector_exposure_summary"]["industrial"] == 0.12
    assert exposure["single_name_concentration_summary"]["limit_warning"] is True
    assert exposure["top_5_concentration"] == exposure["top_10_concentration"]
    assert exposure["gross_exposure"] == exposure["net_exposure"]
    assert exposure["simulated_leverage_forbidden"] is True
    assert exposure["real_leverage_allowed"] is False
    assert exposure["concentration_risk_score"] == 71
