from __future__ import annotations

import json
from pathlib import Path

from a_share_v11_test_utils import make_v11_paths
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform
from trading_core.equity_v11_owner_ops_platform.audit import audit_a_share_v11_owner_ops_platform
from trading_core.equity_v12_continuous_ops.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v12_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v11_paths(tmp_path)
    run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    audit_a_share_v11_owner_ops_platform(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    return paths


def v12_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE, dry_run: bool = False):
    bucket = "dry_run" if dry_run else "daily"
    path = paths.data_dir / "equity_v12_continuous_ops" / bucket / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def v12_daily_dir(paths: ProjectPaths, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> Path:
    return paths.data_dir / "equity_v12_continuous_ops" / "daily" / as_of_date
