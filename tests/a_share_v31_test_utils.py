from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE
from trading_core.equity_v31_post_v3_verification.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v31_paths(tmp_path: Path) -> ProjectPaths:
    workspace_root = tmp_path / "workspace"
    paths = ProjectPaths(workspace_root)
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    (paths.project_root / "RELEASE_NOTES.md").write_text("# Release Notes\n", encoding="utf-8")
    _write_json(
        paths.data_dir / "equity_v30_final_closeout" / "daily" / DEFAULT_AS_OF_DATE / "v30_final_closeout_result.json",
        {
            "target_version": SOURCE_VERSION,
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            **{key: False for key in BOUNDARY_FALSE},
        },
    )
    _write_json(
        paths.data_dir / "equity_data_quality" / "a_share_v30_final_closeout_audit.json",
        {"target_version": SOURCE_VERSION, "overall_passed": True, "blocking_reasons": [], "warnings": []},
    )
    return paths


def v31_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    path = paths.data_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
