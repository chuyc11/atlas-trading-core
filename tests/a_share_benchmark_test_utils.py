from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_benchmarks.benchmark_audit import audit_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_builder import build_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_config import BENCHMARK_FILES, BENCHMARK_REPORTS
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow
from trading_core.storage.file_paths import ProjectPaths


def make_benchmark_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    audit_a_share_daily_research_workflow(paths=paths, as_of_date=AS_OF_DATE)
    write_index_fixture(paths)
    return paths


def write_index_fixture(paths: ProjectPaths, *, days: int = 30) -> None:
    dates = [day.date().isoformat() for day in pd.bdate_range(end=AS_OF_DATE, periods=days)]
    rows = []
    for offset, benchmark_id in enumerate(["CSI300", "CSI500", "CSI1000"], start=1):
        for idx, day in enumerate(dates):
            close = 1000.0 * offset + idx * (1.0 + offset / 10)
            rows.append(
                {
                    "date": day,
                    "benchmark_id": benchmark_id,
                    "symbol_or_index_code": {"CSI300": "000300.SH", "CSI500": "000905.SH", "CSI1000": "000852.SH"}[benchmark_id],
                    "open": close - 1.0,
                    "high": close + 2.0,
                    "low": close - 2.0,
                    "close": close,
                    "volume": 1000 + idx,
                    "amount": close * 1000,
                    "source_type": "local_index_price_panel",
                    "source_path": "data/equity_benchmarks/history/index_price_history_panel.parquet",
                    "source_timestamp": "2026-06-26T15:00:00Z",
                    "is_placeholder": False,
                }
            )
    path = paths.data_dir / "equity_benchmarks" / "history" / "index_price_history_panel.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def remove_index_fixture(paths: ProjectPaths) -> None:
    path = paths.data_dir / "equity_benchmarks" / "history" / "index_price_history_panel.parquet"
    if path.exists():
        path.unlink()


def build_benchmark_package(paths: ProjectPaths) -> dict:
    return build_a_share_benchmark_comparison(paths=paths, as_of_date=AS_OF_DATE)


def audit_benchmark_package(paths: ProjectPaths) -> dict:
    return audit_a_share_benchmark_comparison(paths=paths, as_of_date=AS_OF_DATE)


def benchmark_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_benchmarks" / "daily" / AS_OF_DATE


def benchmark_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_benchmarks" / "daily" / AS_OF_DATE


def benchmark_json(paths: ProjectPaths, key: str):
    return json.loads((benchmark_data_dir(paths) / BENCHMARK_FILES[key]).read_text(encoding="utf-8"))


def benchmark_report(paths: ProjectPaths, key: str) -> str:
    return (benchmark_output_dir(paths) / BENCHMARK_REPORTS[key]).read_text(encoding="utf-8")
