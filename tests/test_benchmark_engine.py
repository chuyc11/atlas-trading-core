from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.storage.file_paths import project_paths


def test_benchmark_json_generates(sample_workspace) -> None:
    portfolio = {"account_id": "CHINA_PAPER", "daily_return": 0.01}
    prices = {
        "510300.SH": {"change_pct": 1.0},
        "000300.SH": {"change_pct": 0.5},
    }
    benchmark = build_benchmark("2026-06-23", portfolio, prices, paths=project_paths(sample_workspace))
    assert benchmark["benchmarks"]["CASH"]["return"] == 0.0
    assert "EQUAL_ETF" in benchmark["benchmarks"]


def test_change_pct_is_treated_as_percent_units(sample_workspace) -> None:
    portfolio = {"account_id": "CHINA_PAPER", "daily_return": 0.01}
    prices = {"000300.SH": {"change_pct": 0.63}}
    benchmark = build_benchmark("2026-06-23", portfolio, prices, paths=project_paths(sample_workspace))
    assert benchmark["benchmarks"]["CSI300"]["return"] == 0.0063
