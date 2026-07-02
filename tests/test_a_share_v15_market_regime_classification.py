from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import REGIME_TAXONOMY, run_a_share_v15_market_regime_lab


def test_v15_market_regime_classification_and_fallback(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    regime = v15_json(paths, "v15_market_regime_classification")

    assert result["overall_passed"] is True
    assert result["market_regime_classification_generated"] is True
    assert regime["primary_regime"] == "mixed_or_uncertain"
    assert regime["regime_taxonomy"] == REGIME_TAXONOMY
    assert regime["regime_confidence_score"] == 0.52
    assert regime["regime_missing_data_warning"] is True
    assert regime["regime_transition_detection"] == "not_available_insufficient_history"
    assert result["market_regime_fabricated"] is False
