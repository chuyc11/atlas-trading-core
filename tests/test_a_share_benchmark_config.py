from __future__ import annotations

from trading_core.equity_benchmarks.benchmark_config import BENCHMARK_IDS, INDEX_CODE_MAP, BenchmarkConfig, validate_benchmark_config


def test_benchmark_config_defaults_and_index_mapping() -> None:
    config = BenchmarkConfig()
    payload = config.to_dict()
    assert payload["as_of_date"] == "2026-06-26"
    assert payload["lookback_trading_days"] == 250
    assert payload["minimum_required_trading_days"] == 20
    assert payload["allow_placeholder_benchmarks"] is False
    assert payload["fail_on_placeholder_benchmarks"] is True
    assert payload["benchmark_ids"] == BENCHMARK_IDS
    assert INDEX_CODE_MAP["CSI300"] == ["000300.SH", "399300.SZ"]
    assert payload["cash_benchmark_daily_return"] == 0.0


def test_benchmark_config_rejects_placeholder_fail_conflict() -> None:
    issues = validate_benchmark_config(BenchmarkConfig(allow_placeholder_benchmarks=True, fail_on_placeholder_benchmarks=True))
    assert any("allow_placeholder_benchmarks" in issue for issue in issues)
