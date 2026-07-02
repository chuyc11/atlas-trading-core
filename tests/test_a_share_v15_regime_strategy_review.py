from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_strategy_regime_review_is_simulation_only(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    strategy = v15_json(paths, "v15_regime_strategy_quality_result")

    assert result["regime_strategy_quality_result_generated"] is True
    assert strategy["strategy_regime_promotion_blocker"] is True
    assert strategy["strategy_freeze_suggestion_under_adverse_regime"] is True
    assert strategy["suggestion_is_simulation_only"] is True
    assert strategy["strategy_real_trading_active_state_present"] is False
