from __future__ import annotations

from trading_core.equity_performance.performance_config import ALLOWED_MODES, BENCHMARK_IDS, PerformanceConfig, validate_performance_config


def test_performance_config_defaults() -> None:
    payload = PerformanceConfig().to_dict()
    assert payload["as_of_date"] == "2026-06-26"
    assert payload["tracking_start_date"] == "2026-06-26"
    assert payload["mode"] == "current_snapshot"
    assert payload["allowed_modes"] == ALLOWED_MODES
    assert payload["benchmark_ids"] == BENCHMARK_IDS
    assert payload["minimum_required_observations"] == 20
    assert payload["broker_enabled"] is False
    assert payload["real_order_enabled"] is False


def test_performance_config_rebuild_requires_explicit_allow_rebuild() -> None:
    issues = validate_performance_config(PerformanceConfig(mode="rebuild_virtual_performance_series"))
    assert any("allow_rebuild" in issue for issue in issues)
