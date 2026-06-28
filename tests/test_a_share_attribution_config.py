from __future__ import annotations

from trading_core.equity_attribution.attribution_config import ALLOWED_MODES, BENCHMARK_IDS, AttributionConfig, validate_attribution_config


def test_attribution_config_defaults() -> None:
    payload = AttributionConfig().to_dict()
    assert payload["as_of_date"] == "2026-06-26"
    assert payload["mode"] == "current_exposure_diagnostics"
    assert payload["allowed_modes"] == ALLOWED_MODES
    assert payload["benchmark_ids"] == BENCHMARK_IDS
    assert payload["limited_history"] is True
    assert payload["realized_performance_attribution_available"] is False
    assert payload["broker_enabled"] is False


def test_attribution_config_mode_validation() -> None:
    assert validate_attribution_config(AttributionConfig(mode="bad_mode"))
