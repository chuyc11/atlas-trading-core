from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_portfolio_risk_scorecard_generation(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    scorecard = v14_json(paths, "v14_portfolio_risk_scorecard")

    assert result["overall_passed"] is True
    assert result["portfolio_risk_scorecard_generated"] is True
    assert scorecard["checks"]["portfolio_nav_dependency_check_passed"] is True
    assert scorecard["checks"]["simulated_account_dependency_check_passed"] is True
    assert scorecard["checks"]["paper_ledger_dependency_check_passed"] is True
    assert scorecard["checks"]["simulated_leverage_forbidden"] is True
    assert result["blocking_reasons"] == []
