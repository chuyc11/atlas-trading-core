from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_performance_test_utils import audit_performance_package, build_performance_package, make_performance_paths
from trading_core.equity_attribution.attribution_audit import audit_a_share_performance_attribution
from trading_core.equity_attribution.attribution_builder import build_a_share_performance_attribution
from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FILES, ATTRIBUTION_REPORTS
from trading_core.storage.file_paths import ProjectPaths


def make_attribution_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_performance_paths(tmp_path)
    build_performance_package(paths)
    audit_performance_package(paths)
    return paths


def build_attribution_package(paths: ProjectPaths, **kwargs):
    return build_a_share_performance_attribution(paths=paths, as_of_date=AS_OF_DATE, **kwargs)


def audit_attribution_package(paths: ProjectPaths):
    return audit_a_share_performance_attribution(paths=paths, as_of_date=AS_OF_DATE)


def attribution_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_attribution" / "daily" / AS_OF_DATE


def attribution_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_attribution" / "daily" / AS_OF_DATE


def attribution_json(paths: ProjectPaths, key: str):
    return json.loads((attribution_data_dir(paths) / ATTRIBUTION_FILES[key]).read_text(encoding="utf-8"))


def attribution_report(paths: ProjectPaths, key: str) -> str:
    return (attribution_output_dir(paths) / ATTRIBUTION_REPORTS[key]).read_text(encoding="utf-8")
