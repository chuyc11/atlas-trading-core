from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_breadth_and_risk_appetite_are_interpretation_only(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    breadth = v15_json(paths, "v15_market_breadth_diagnostics")
    appetite = v15_json(paths, "v15_risk_appetite_diagnostics")

    assert result["market_breadth_diagnostics_generated"] is True
    assert breadth["insufficient_breadth_data_warning"] is True
    assert breadth["breadth_fabricated"] is False
    assert breadth["breadth_generates_buy_sell_signal"] is False
    assert result["risk_appetite_diagnostics_generated"] is True
    assert appetite["research_interpretation_only"] is True
    assert appetite["macro_prediction_claimed"] is False
