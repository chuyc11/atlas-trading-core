from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_benchmark_test_utils import make_benchmark_paths, remove_index_fixture
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_benchmarks.benchmark_config import BenchmarkConfig
from trading_core.equity_benchmarks.index_benchmarks import availability_from_index_prices, load_index_benchmark_prices


def test_index_benchmarks_load_local_panel_without_placeholder(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    config = BenchmarkConfig(as_of_date=AS_OF_DATE)
    frame, source = load_index_benchmark_prices(paths=paths, config=config, generated_at="2026-06-26T00:00:00Z")
    assert set(frame["benchmark_id"]) == {"CSI300", "CSI500", "CSI1000"}
    assert source["source_type"] == "local_index_price_panel"
    availability = availability_from_index_prices(frame, config=config, source_meta=source)
    assert all(row["status"] == "available" for row in availability)
    assert all(row["is_placeholder"] is False for row in availability)


def test_missing_index_benchmark_fails_by_default(tmp_path: Path, monkeypatch) -> None:
    paths = make_benchmark_paths(tmp_path)
    remove_index_fixture(paths)
    monkeypatch.setattr("trading_core.equity_benchmarks.index_benchmarks.fetch_eastmoney_index_history", lambda **_: (pd.DataFrame(), []))
    frame, source = load_index_benchmark_prices(paths=paths, config=BenchmarkConfig(as_of_date=AS_OF_DATE), generated_at="2026-06-26T00:00:00Z")
    availability = availability_from_index_prices(frame, config=BenchmarkConfig(as_of_date=AS_OF_DATE), source_meta=source)
    assert frame.empty
    assert all(row["status"] == "missing" for row in availability)
