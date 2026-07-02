from __future__ import annotations

import json
from pathlib import Path

from a_share_benchmark_claim_hardening_test_utils import write_claim_base_inputs
from trading_core.equity_benchmark_claim_hardening.builder import build_a_share_benchmark_claim_hardening
from trading_core.equity_benchmark_claim_hardening.audit import audit_a_share_benchmark_claim_hardening
from trading_core.equity_v11_owner_ops_platform.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v11_paths(tmp_path: Path, *, with_index: bool = False) -> ProjectPaths:
    project = tmp_path / "work" / "trading-core"
    (project / "data").mkdir(parents=True)
    (project / "outputs").mkdir(parents=True)
    (project / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    paths = ProjectPaths(tmp_path)
    write_claim_base_inputs(paths, with_index=with_index)
    build_a_share_benchmark_claim_hardening(paths=paths)
    audit_a_share_benchmark_claim_hardening(paths=paths)
    return paths


def v11_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE, dry_run: bool = False):
    bucket = "dry_run" if dry_run else "daily"
    path = paths.data_dir / "equity_v11_owner_ops_platform" / bucket / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def v11_daily_dir(paths: ProjectPaths, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> Path:
    return paths.data_dir / "equity_v11_owner_ops_platform" / "daily" / as_of_date
