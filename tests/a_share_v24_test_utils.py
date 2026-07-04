from __future__ import annotations

import json
from pathlib import Path

from a_share_v23_test_utils import make_v23_paths
from trading_core.equity_v23_operator_ux_journal.audit import audit_a_share_v23_operator_ux_journal
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal
from trading_core.equity_v24_maintenance_quality.audit import audit_a_share_v24_maintenance_quality
from trading_core.equity_v24_maintenance_quality.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION, run_a_share_v24_maintenance_quality
from trading_core.storage.file_paths import ProjectPaths


def make_v24_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v23_paths(tmp_path)
    run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    audit_a_share_v23_operator_ux_journal(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    return paths


def build_v24(paths: ProjectPaths):
    result = run_a_share_v24_maintenance_quality(paths=paths, simulation_only=True)
    audit = audit_a_share_v24_maintenance_quality(paths=paths)
    return result, audit


def v24_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v24_maintenance_quality" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
