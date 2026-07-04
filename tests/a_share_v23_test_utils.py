from __future__ import annotations

import json
from pathlib import Path

from a_share_v22_test_utils import make_v22_paths
from trading_core.equity_v22_ensemble_meta_strategy.audit import audit_a_share_v22_ensemble_meta_strategy
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy
from trading_core.equity_v23_operator_ux_journal.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v23_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v22_paths(tmp_path)
    run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    audit_a_share_v22_ensemble_meta_strategy(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    return paths


def v23_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v23_operator_ux_journal" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
