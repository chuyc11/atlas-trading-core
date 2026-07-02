from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_walkforward_oos_keeps_claims_blocked(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    walkforward = v13_json(paths, "v13_backtest_walkforward_oos_result")

    assert result["backtest_walkforward_oos_result_generated"] is True
    assert walkforward["transaction_cost_adjusted"] is True
    assert walkforward["real_performance_claim_allowed"] is False
    assert walkforward["metrics"]["annualized_return"] is None
    assert result["real_performance_claim_allowed"] is False
