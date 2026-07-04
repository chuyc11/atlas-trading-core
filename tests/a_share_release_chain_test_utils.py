from __future__ import annotations

import json
from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths
from trading_core.equity_release_chain import RELEASE_SPECS, audit_release_artifacts, run_release_artifacts, spec_by_key
from trading_core.equity_v24_maintenance_quality.builder import TARGET_VERSION as V24_TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_release_paths(tmp_path: Path, target_key: str) -> ProjectPaths:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    (paths.project_root / "VERSION").write_text(V24_TARGET_VERSION, encoding="utf-8")
    for spec in RELEASE_SPECS:
        if spec["key"] == target_key:
            break
        run_release_artifacts(spec, paths=paths, simulation_only=True)
        audit_release_artifacts(spec=spec, paths=paths)
        (paths.project_root / "VERSION").write_text(spec["target_version"], encoding="utf-8")
    return paths


def build_release(paths: ProjectPaths, target_key: str):
    spec = spec_by_key(target_key)
    result = run_release_artifacts(spec, paths=paths, simulation_only=True)
    audit = audit_release_artifacts(spec=spec, paths=paths)
    return spec, result, audit


def release_json(paths: ProjectPaths, target_key: str, name: str, *, as_of_date: str = "2026-07-01"):
    spec = spec_by_key(target_key)
    path = paths.data_dir / spec["package_dir"] / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
