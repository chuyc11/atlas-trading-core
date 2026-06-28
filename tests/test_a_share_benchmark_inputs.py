from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import make_benchmark_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_benchmarks.benchmark_inputs import load_benchmark_inputs


def test_benchmark_inputs_load_workflow_tracking_selection_and_prices(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    inputs = load_benchmark_inputs(paths=paths, as_of_date=AS_OF_DATE)
    assert inputs.workflow_artifacts["workflow_audit"]["overall_passed"] is True
    assert inputs.tracking_artifacts["portfolio_performance_snapshot"]["performance_not_yet_observed"] is True
    assert inputs.strict_tradable_symbols
    assert inputs.candidate_symbols
    assert not inputs.adjusted_prices.empty
    assert inputs.adjusted_prices["date"].max() <= AS_OF_DATE
