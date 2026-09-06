from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from trading_core.equity_release_chain import (
    RELEASE_SPECS,
    audit_release_artifacts,
    record_full_pytest_evidence,
    run_release_artifacts,
    spec_by_key,
)
from trading_core.equity_data_quality.common import BOUNDARY_FALSE
from trading_core.storage.file_paths import ProjectPaths

V24_TARGET_VERSION = "v2.4.0-a-share-simulation-research-maintenance-quality-and-artifact-bloat-reduction"


def make_release_paths(
    tmp_path: Path,
    target_key: str,
    *,
    include_full_pytest_evidence: bool = True,
) -> ProjectPaths:
    """Build the synthetic release lineage required by a focused unit test.

    The v2.4.0 baseline is seeded directly as data (its builder was archived
    with the equity_vXX milestone code); the same hand-seeded pattern is used
    for the v3.1.0 fixture in ``a_share_v3x_release_test_utils``.  Full-suite
    evidence is deliberately created through the same public producer used in
    production.  The subprocess result is mocked only because these temporary
    fixtures do not contain the repository's real test suite; tests that
    exercise a missing evidence path pass ``False`` explicitly.
    """

    paths = _make_v24_baseline(tmp_path)
    for spec in RELEASE_SPECS:
        if spec["key"] == target_key:
            break
        _prepare_full_pytest_evidence(paths, spec, include_full_pytest_evidence)
        run_release_artifacts(spec, paths=paths, simulation_only=True)
        audit_release_artifacts(spec=spec, paths=paths)
        (paths.project_root / "VERSION").write_text(spec["target_version"], encoding="utf-8")
    _prepare_full_pytest_evidence(paths, spec_by_key(target_key), include_full_pytest_evidence)
    return paths


def _make_v24_baseline(tmp_path: Path) -> ProjectPaths:
    """Seed the v2.4.0 baseline artifacts the v2.5.0 release step verifies."""

    workspace_root = tmp_path / "workspace"
    paths = ProjectPaths(workspace_root)
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    paths.project_root.mkdir(parents=True, exist_ok=True)
    (paths.project_root / "VERSION").write_text(V24_TARGET_VERSION, encoding="utf-8")
    _write_json(
        paths.data_dir / "equity_v24_maintenance_quality" / "daily" / "2026-07-01" / "v24_maintenance_quality_result.json",
        {
            "target_version": V24_TARGET_VERSION,
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            **dict.fromkeys(BOUNDARY_FALSE, False),
        },
    )
    _write_json(
        paths.data_dir / "equity_data_quality" / "a_share_v24_maintenance_quality_audit.json",
        {"target_version": V24_TARGET_VERSION, "overall_passed": True, "blocking_reasons": [], "warnings": []},
    )
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


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
