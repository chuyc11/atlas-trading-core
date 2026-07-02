from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_leakage_lookahead_survivorship_guard(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    guard = v16_json(paths, "v16_leakage_lookahead_survivorship_guard")

    assert result["leakage_lookahead_survivorship_guard_generated"] is True
    assert result["lookahead_bias_guard_passed"] is True
    assert result["future_data_usage_detected"] is False
    assert result["leakage_blocker_count"] == 0
    assert result["survivorship_bias_warning_recorded"] is True
    assert guard["publication_lag_guard_passed"] is True
