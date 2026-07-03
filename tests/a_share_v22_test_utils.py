from __future__ import annotations

import json
from pathlib import Path

from a_share_v21_test_utils import make_v21_paths
from trading_core.equity_v21_data_source_benchmark_hardening.audit import audit_a_share_v21_data_source_benchmark_hardening
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening
from trading_core.equity_v22_ensemble_meta_strategy.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v22_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v21_paths(tmp_path)
    run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    audit_a_share_v21_data_source_benchmark_hardening(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    (paths.project_root / "RELEASE_NOTES.md").write_text(
        "# Release Notes\n\n"
        "## v2.1.0-a-share-production-quality-data-source-depth-and-benchmark-hardening\n\n"
        "- full pytest: `1967 passed, 1 skipped`\n",
        encoding="utf-8",
    )
    return paths


def v22_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
