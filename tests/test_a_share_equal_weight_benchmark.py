from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import make_benchmark_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_benchmarks.benchmark_config import BenchmarkConfig
from trading_core.equity_benchmarks.benchmark_inputs import load_benchmark_inputs
from trading_core.equity_benchmarks.equal_weight_benchmark import build_equal_weight_benchmark


def test_equal_weight_strict_and_candidate_benchmarks_use_adjusted_prices(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    inputs = load_benchmark_inputs(paths=paths, as_of_date=AS_OF_DATE)
    config = BenchmarkConfig(as_of_date=AS_OF_DATE, minimum_required_trading_days=20)
    strict_records, strict_availability, strict_exclusions = build_equal_weight_benchmark(
        benchmark_id="EQUAL_WEIGHT_STRICT_TRADABLE",
        symbols=inputs.strict_tradable_symbols,
        adjusted_prices=inputs.adjusted_prices,
        daily_prices=inputs.daily_prices,
        config=config,
    )
    candidate_records, candidate_availability, _ = build_equal_weight_benchmark(
        benchmark_id="EQUAL_WEIGHT_CANDIDATE_POOL",
        symbols=inputs.candidate_symbols,
        adjusted_prices=inputs.adjusted_prices,
        daily_prices=inputs.daily_prices,
        config=config,
    )
    assert strict_availability["status"] == "available"
    assert candidate_availability["status"] == "available"
    assert strict_records[-1]["date"] == AS_OF_DATE
    assert strict_exclusions["excluded_constituent_count"] == 0
