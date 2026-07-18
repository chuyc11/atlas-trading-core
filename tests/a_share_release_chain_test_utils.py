from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from a_share_v24_test_utils import build_v24, make_v24_paths
from trading_core.equity_release_chain import (
    RELEASE_SPECS,
    audit_release_artifacts,
    record_full_pytest_evidence,
    run_release_artifacts,
    spec_by_key,
)
from trading_core.equity_v24_maintenance_quality.builder import TARGET_VERSION as V24_TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_release_paths(
    tmp_path: Path,
    target_key: str,
    *,
    include_full_pytest_evidence: bool = True,
) -> ProjectPaths:
    """Build the synthetic release lineage required by a focused unit test.

    Full-suite evidence is deliberately created through the same public
    producer used in production.  The subprocess result is mocked only because
    these temporary fixtures do not contain the repository's real test suite;
    tests that exercise a missing evidence path pass ``False`` explicitly.
    """

    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    (paths.project_root / "VERSION").write_text(V24_TARGET_VERSION, encoding="utf-8")
    for spec in RELEASE_SPECS:
        if spec["key"] == target_key:
            break
        _prepare_full_pytest_evidence(paths, spec, include_full_pytest_evidence)
        run_release_artifacts(spec, paths=paths, simulation_only=True)
        audit_release_artifacts(spec=spec, paths=paths)
        (paths.project_root / "VERSION").write_text(spec["target_version"], encoding="utf-8")
    _prepare_full_pytest_evidence(paths, spec_by_key(target_key), include_full_pytest_evidence)
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


def record_test_full_pytest_evidence(paths: ProjectPaths) -> dict:
    """Create valid evidence in a synthetic fixture without asserting a pass.

    The fixture still calls ``record_full_pytest_evidence`` so that its command,
    source binding, summary hash, and validation path remain under test.  This
    helper must not be used by production release code.
    """

    def completed_pytest(command, **_kwargs):
        assert command[1:] == ["-m", "pytest"]
        return CompletedProcess(command, 0, stdout="1 passed\n", stderr="")

    with patch("trading_core.equity_release_chain.generic.subprocess.run", side_effect=completed_pytest):
        evidence = record_full_pytest_evidence(paths=paths, timeout_seconds=60)
    assert evidence["full_pytest_run"] is True
    assert evidence["full_pytest_passed"] is True
    return evidence


def _prepare_full_pytest_evidence(
    paths: ProjectPaths,
    spec: dict,
    include_full_pytest_evidence: bool,
) -> None:
    if not include_full_pytest_evidence or not spec["full_pytest_required"]:
        return
    # Evidence is bound to the target source tree.  Baseline verification
    # permits a target version because it only requires a version at or after
    # the prior release.
    (paths.project_root / "VERSION").write_text(spec["target_version"], encoding="utf-8")
    record_test_full_pytest_evidence(paths)
