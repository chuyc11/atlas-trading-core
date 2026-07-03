from __future__ import annotations

import json
from pathlib import Path

from a_share_v20_test_utils import make_v20_paths
from trading_core.equity_v20_platform_closeout.audit import audit_a_share_v20_platform_closeout
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout
from trading_core.equity_v21_data_source_benchmark_hardening.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v21_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v20_paths(tmp_path)
    run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    audit_a_share_v20_platform_closeout(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    (paths.project_root / "RELEASE_NOTES.md").write_text(
        "# Release Notes\n\n"
        "## v2.0.0-a-share-simulation-research-platform-release-candidate-and-full-plan-closeout\n\n"
        "- full pytest: `1955 passed, 1 skipped`\n",
        encoding="utf-8",
    )
    return paths


def v21_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
