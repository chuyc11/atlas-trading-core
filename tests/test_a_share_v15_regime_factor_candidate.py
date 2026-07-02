from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_factor_candidate_regime_overlays_are_not_trade_advice(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    factor = v15_json(paths, "v15_regime_factor_quality_overlay")
    candidate = v15_json(paths, "v15_regime_candidate_quality_overlay")

    assert result["regime_factor_quality_overlay_generated"] is True
    assert factor["regime_specific_ic_fabricated"] is False
    assert factor["factor_regime_output_simulation_only"] is True
    assert result["regime_candidate_quality_overlay_generated"] is True
    assert candidate["candidate_watchlist_is_not_buy_list"] is True
    assert candidate["candidate_downgrade_is_not_sell_signal"] is True
    assert candidate["candidate_regime_report_no_real_trade_advice"] is True
