from trading_core.equity_ops_history.trend_baseline_config import build_ops_trend_baseline_config


def test_ops_trend_baseline_config_has_default_windows():
    config = build_ops_trend_baseline_config(as_of_date="2026-06-26", history_window_days=90, minimum_required_observations=5, baseline_window_observations=20)
    assert config["history_window_days"] == 90
    assert config["minimum_required_observations"] == 5
    assert config["baseline_window_observations"] == 20

