from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from a_share_release_chain_test_utils import make_release_paths
from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_release_chain import audit_release_artifacts, run_release_artifacts, spec_by_key
from trading_core.equity_release_chain import generic


def test_release_chain_fails_closed_without_verified_full_pytest_evidence(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v25", include_full_pytest_evidence=False)
    spec = spec_by_key("v25")

    result = run_release_artifacts(spec, paths=paths, simulation_only=True)
    audit = audit_release_artifacts(spec=spec, paths=paths)

    assert result["full_pytest_run"] is False
    assert result["full_pytest_passed"] is False
    assert result["full_pytest_evidence_status"] == "missing"
    assert "full_pytest_evidence_missing" in result["blocking_reasons"]
    assert result["overall_passed"] is False
    assert audit["overall_passed"] is False
    assert "full_pytest_evidence_missing" in audit["blocking_reasons"]


def test_v3x_full_regression_flags_fail_closed_without_pytest_evidence(tmp_path: Path) -> None:
    from a_share_v3x_release_test_utils import build_through, make_v3x_paths

    paths = make_v3x_paths(tmp_path)
    # Build the v3.4 baseline without entering the v3.5 evidence-producing
    # helper.  The next release must not invent its full-regression result.
    build_through(paths, "v34")
    spec = spec_by_key("v35")

    result = run_release_artifacts(spec, paths=paths, simulation_only=True)
    audit = audit_release_artifacts(spec=spec, paths=paths)

    assert result["full_regression_run"] is False
    assert result["full_regression_passed"] is False
    assert result["overall_passed"] is False
    assert "full_pytest_evidence_missing" in result["blocking_reasons"]
    assert audit["overall_passed"] is False
    assert "full_pytest_evidence_missing" in audit["blocking_reasons"]


def test_release_audit_recomputes_manifest_hashes(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v25")
    spec = spec_by_key("v25")
    run_release_artifacts(spec, paths=paths, simulation_only=True)
    artifact_name = next(
        name for name in spec["json_names"] if name not in {spec["manifest_name"], spec["result_name"]}
    )
    artifact_path = paths.data_dir / spec["package_dir"] / "daily" / "2026-07-01" / f"{artifact_name}.json"
    payload = read_json(artifact_path)
    payload["tampered_after_manifest"] = True
    write_json(artifact_path, payload)

    audit = audit_release_artifacts(spec=spec, paths=paths)

    assert audit["manifest_integrity"]["passed"] is False
    assert f"manifest_sha256_mismatch:{artifact_name}" in audit["blocking_reasons"]


def test_release_manifest_excludes_itself_and_survives_a_rerun(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v25")
    spec = spec_by_key("v25")

    run_release_artifacts(spec, paths=paths, simulation_only=True)
    first_audit = audit_release_artifacts(spec=spec, paths=paths)
    run_release_artifacts(spec, paths=paths, simulation_only=True)
    second_audit = audit_release_artifacts(spec=spec, paths=paths)

    assert first_audit["overall_passed"] is True
    assert second_audit["overall_passed"] is True
    assert second_audit["manifest_integrity"]["passed"] is True
    assert second_audit["manifest_integrity"]["record_count"] == len(spec["json_names"]) - 1 + len(spec["markdown_names"])


def test_recorded_pytest_evidence_is_bound_to_command_output_and_source_tree(
    tmp_path: Path,
    monkeypatch,
) -> None:
    paths = make_release_paths(tmp_path, "v25")
    observed: dict[str, object] = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="3 passed\n", stderr="")

    monkeypatch.setattr(generic.subprocess, "run", fake_run)
    evidence = generic.record_full_pytest_evidence(paths=paths, timeout_seconds=60)
    verification = generic._load_full_pytest_evidence(paths, spec_by_key("v25"))

    assert observed["command"][1:] == ["-m", "pytest"]
    assert verification["full_pytest_run"] is True
    assert verification["full_pytest_passed"] is True
    assert evidence["summary_sha256"]

    source_path = paths.project_root / "src" / "trading_core" / "changed_after_evidence.py"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("VALUE = 1\n", encoding="utf-8")
    stale = generic._load_full_pytest_evidence(paths, spec_by_key("v25"))

    assert stale["full_pytest_passed"] is False
    assert "full_pytest_evidence_source_tree_stale" in stale["blocking_reasons"]


def test_unavailable_pytest_runner_writes_blocking_evidence(tmp_path: Path, monkeypatch) -> None:
    paths = make_release_paths(tmp_path, "v25", include_full_pytest_evidence=False)

    def missing_runner(*_args, **_kwargs):
        raise OSError("pytest executable unavailable")

    monkeypatch.setattr(generic.subprocess, "run", missing_runner)
    evidence = generic.record_full_pytest_evidence(paths=paths, timeout_seconds=60)
    verification = generic._load_full_pytest_evidence(paths, spec_by_key("v25"))

    assert evidence["full_pytest_run"] is False
    assert evidence["full_pytest_passed"] is False
    assert verification["full_pytest_passed"] is False
    assert "full_pytest_not_completed" in verification["blocking_reasons"]
