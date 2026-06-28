from __future__ import annotations

import json
from pathlib import Path

from a_share_benchmark_test_utils import audit_benchmark_package, build_benchmark_package, make_benchmark_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_performance.performance_audit import audit_a_share_multi_day_performance
from trading_core.equity_performance.performance_builder import build_a_share_multi_day_performance
from trading_core.equity_performance.performance_config import PERFORMANCE_FILES, PERFORMANCE_REPORTS
from trading_core.storage.file_paths import ProjectPaths


def make_performance_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    audit_benchmark_package(paths)
    return paths


def build_performance_package(paths: ProjectPaths, **kwargs):
    return build_a_share_multi_day_performance(paths=paths, as_of_date=AS_OF_DATE, **kwargs)


def audit_performance_package(paths: ProjectPaths):
    return audit_a_share_multi_day_performance(paths=paths, as_of_date=AS_OF_DATE)


def performance_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_performance" / "daily" / AS_OF_DATE


def performance_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_performance" / "daily" / AS_OF_DATE


def performance_json(paths: ProjectPaths, key: str):
    return json.loads((performance_data_dir(paths) / PERFORMANCE_FILES[key]).read_text(encoding="utf-8"))


def performance_report(paths: ProjectPaths, key: str) -> str:
    return (performance_output_dir(paths) / PERFORMANCE_REPORTS[key]).read_text(encoding="utf-8")
