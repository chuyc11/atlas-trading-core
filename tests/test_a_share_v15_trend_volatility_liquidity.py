from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_trend_volatility_liquidity_record_missing_data_honestly(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    trend = v15_json(paths, "v15_trend_diagnostics")
    volatility = v15_json(paths, "v15_volatility_diagnostics")
    liquidity = v15_json(paths, "v15_liquidity_regime_result")

    assert result["trend_diagnostics_generated"] is True
    assert trend["trend_unavailable_warning"] is True
    assert trend["future_data_used"] is False
    assert trend["data_coverage"]["index_history"] == "not_available"
    assert result["volatility_diagnostics_generated"] is True
    assert volatility["volatility_fabricated"] is False
    assert volatility["real_world_prediction_claimed"] is False
    assert result["liquidity_regime_result_generated"] is True
    assert liquidity["liquidity_fabricated"] is False
    assert liquidity["real_capacity_claimed"] is False
