from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v16_pit_backtest_market_rules.audit import audit_a_share_v16_pit_backtest_market_rules
from trading_core.equity_v16_pit_backtest_market_rules.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v16_pit_backtest_market_rules


def test_v16_safety_boundary_and_audit(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    audit = audit_a_share_v16_pit_backtest_market_rules(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["artifact_checks"]["json_count"] == len(JSON_NAMES)
    assert audit["artifact_checks"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["real_orders_placed"] is False
    assert result["real_order_preview_generated"] is False
    assert result["buy_sell_signals_generated"] is False
