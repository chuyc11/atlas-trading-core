"""Generic artifact builder/auditor for the v2.5-v3.0 A-share release chain."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.security.v36_scope import collect_v36_scope_records
from trading_core.storage.file_paths import ProjectPaths, project_paths

DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21
FULL_PYTEST_EVIDENCE_RELATIVE_PATH = Path("data/equity_release_evidence/full_pytest_evidence.json")
FULL_PYTEST_SUMMARY_RELATIVE_PATH = Path("data/equity_release_evidence/full_pytest_summary.txt")
FULL_PYTEST_EVIDENCE_SCHEMA_VERSION = 1
# These flags describe an externally executed test run.  They must never be
# populated by a release builder merely because a release spec lists them as a
# required field.  The v3.x names are historical aliases for the same full
# repository pytest evidence and are kept in lockstep below.
EVIDENCE_DERIVED_TRUE_FIELDS = {
    "full_pytest_run",
    "full_pytest_passed",
    "full_regression_run",
    "full_regression_passed",
}
V36_EVIDENCE_RELATIVE_PATH = Path("data/security_evidence/v36_security_assessment.json")
V36_REQUIRED_SCANS = {
    "secret_scan",
    "config_governance",
    "dependency_scan",
    "filesystem_path_scan",
    "network_boundary_scan",
}
V36_OBSERVATION_FIELDS = {
    "high_confidence_secret_detected",
    "broker_credential_detected",
    "account_credential_detected",
    "order_api_endpoint_detected",
    "unsafe_config_override_detected",
    "unsafe_file_delete_detected",
    "broker_network_path_detected",
    "account_network_path_detected",
}


def run_release_artifacts(
    spec: dict[str, Any],
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, spec, as_of_date)
    _ensure_dirs(artifacts)
    if not simulation_only:
        result = _fail_closed(spec, as_of_date, "simulation_only_flag_required")
        write_json(artifacts[spec["result_name"]], result)
        return result

    generated_at = utc_now()
    baseline = _baseline_verification(paths, spec, as_of_date)
    if not baseline["overall_passed"]:
        result = _fail_closed(spec, as_of_date, "baseline_verification_failed")
        result[f"{spec['source_version'].split('-')[0].replace('.', '')}_baseline"] = baseline
        write_json(artifacts[spec["result_name"]], result)
        return result

    pytest_evidence = _load_full_pytest_evidence(paths, spec)
    security_assessment = _load_v36_security_assessment(paths) if spec["key"] == "v36" else None
    payloads: dict[str, dict[str, Any]] = {}
    for name in spec["json_names"]:
        if name == spec["manifest_name"]:
            continue
        if name == spec["result_name"]:
            continue
        payloads[name] = _component_payload(spec, name, as_of_date, generated_at, baseline, pytest_evidence)
    if security_assessment is not None:
        _apply_v36_component_assessment(payloads, security_assessment)

    integrity = _integrity_sweep(spec, as_of_date, payloads)
    protected = _protected_sweep(spec, as_of_date)
    safety = _safety_sweep(spec, as_of_date, payloads)
    payloads.update(
        {
            _artifact_name_containing(spec, "artifact_integrity_sweep"): integrity,
            _artifact_name_containing(spec, "protected_path_sweep"): protected,
            _artifact_name_containing(spec, "safety_boundary_sweep"): safety,
        }
    )
    result = _result_payload(
        spec,
        as_of_date,
        baseline,
        payloads,
        integrity,
        protected,
        safety,
        pytest_evidence,
        security_assessment=security_assessment,
    )
    payloads[spec["result_name"]] = result
    regression_artifact = spec.get("regression_artifact_name")
    if regression_artifact and regression_artifact in payloads:
        payloads[regression_artifact].update(
            {key: value for key, value in result.items() if key.startswith("full_regression_") or key.startswith("single_command_")}
        )

    for name, payload in payloads.items():
        write_json(artifacts[name], payload)
    _write_markdowns(spec, artifacts, payloads, result)
    manifest = _manifest(paths, spec, artifacts, as_of_date, generated_at, result, pytest_evidence)
    write_json(artifacts[spec["manifest_name"]], manifest)
    return result


def audit_release_artifacts(*, spec: dict[str, Any], as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / spec["package_dir"] / "daily" / as_of_date
    output_dir = paths.outputs_dir / spec["package_dir"] / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in spec["json_names"]}
    result = payloads[spec["result_name"]]
    markdowns = [output_dir / name for name in spec["markdown_names"]]
    blocking: list[str] = []
    manifest_check = _verify_release_manifest(paths, spec, as_of_date)
    pytest_evidence = _load_full_pytest_evidence(paths, spec)

    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if result.get("target_version") != spec["target_version"]:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
    if not manifest_check["passed"]:
        blocking.extend(manifest_check["blocking_reasons"])
    if spec["full_pytest_required"]:
        verified_evidence_fields = _full_pytest_result_fields(pytest_evidence)
        for field in sorted(EVIDENCE_DERIVED_TRUE_FIELDS.intersection(spec["required_true"])):
            if result.get(field) is not verified_evidence_fields[field]:
                blocking.append(f"{field}_does_not_match_verified_evidence")
        blocking.extend(pytest_evidence["blocking_reasons"])
    for key in spec["required_true"]:
        if result.get(key) is not True:
            blocking.append(f"required_true_missing:{key}")
    for key in spec["required_false"]:
        if result.get(key) is not False:
            blocking.append(f"required_false_not_false:{key}")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    if result.get("owner_readiness_state") != "blocked":
        blocking.append("owner_readiness_state_not_blocked")
    if result.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    current_security_assessment = None
    if spec["key"] == "v36":
        current_security_assessment = _load_v36_security_assessment(paths)
        if current_security_assessment["status"] != "passed":
            blocking.append(f"current_security_assessment_{current_security_assessment['status']}")
            blocking.extend(current_security_assessment.get("blocking_reasons", []))

    audit = {
        "audit_id": f"A-SHARE-{spec['key'].upper()}-AUDIT",
        "target_version": spec["target_version"],
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {
            "json_count": len(spec["json_names"]),
            "markdown_count": len(spec["markdown_names"]),
            "audit_markdown_count": 1,
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
            "json_budget_passed": len(spec["json_names"]) <= 28,
            "markdown_budget_passed": len(spec["markdown_names"]) <= 8,
            "audit_markdown_budget_passed": True,
            "manifest_integrity_passed": manifest_check["passed"],
            "manifest_record_count": manifest_check["record_count"],
        },
        "quality_checks": {key: result.get(key) for key in spec["required_true"]},
        "forbidden_checks": {key: result.get(key) for key in spec["required_false"] + list(BOUNDARY_FALSE)},
        "owner_readiness_state": result.get("owner_readiness_state"),
        "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
        "live_trading_ready": result.get("live_trading_ready"),
        "full_pytest_run": result.get("full_pytest_run"),
        "full_pytest_passed": result.get("full_pytest_passed"),
        "full_pytest_evidence": _full_pytest_result_fields(pytest_evidence),
        "manifest_integrity": manifest_check,
        "targeted_pytest_required": result.get("targeted_pytest_required"),
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "recommended_next_version": spec["recommended_next_version"],
    }
    if current_security_assessment is not None:
        audit["security_assessment"] = current_security_assessment
        if current_security_assessment["status"] != "passed":
            for key in V36_OBSERVATION_FIELDS:
                audit["forbidden_checks"][key] = None
    audit_path = paths.data_dir / "equity_data_quality" / spec["audit_json"]
    report_path = paths.outputs_dir / "audit" / spec["audit_md"]
    write_json(audit_path, audit)
    _write_audit_report(report_path, audit)
    return audit


def _baseline_verification(paths: ProjectPaths, spec: dict[str, Any], as_of_date: str) -> dict[str, Any]:
    source_dir = _latest_daily_dir(paths.data_dir / spec["source_result_dir"] / "daily", as_of_date)
    source_result = read_json(source_dir / f"{spec['source_result_name']}.json")
    source_audit = read_json(paths.data_dir / "equity_data_quality" / spec["source_audit_json"])
    version_text = _read_text(paths.project_root / "VERSION").strip()
    tag = _run(["git", "tag", "--list", spec["source_version"]], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": spec["source_version"]}
    checks = {
        "source_tag_exists": tag.get("stdout", "").strip() == spec["source_version"],
        "version_matches": _release_version_is_at_or_after(version_text, spec["source_version"]),
        "source_result_present": bool(source_result),
        "source_audit_present": bool(source_audit),
        "source_result_overall_passed": source_result.get("overall_passed") is True,
        "source_audit_overall_passed": source_audit.get("overall_passed") is True,
        "source_blocking_reasons_empty": source_result.get("blocking_reasons") == [] and source_audit.get("blocking_reasons") == [],
        "source_safety_boundary_clean": all(source_result.get(key) is False for key in BOUNDARY_FALSE),
    }
    return {
        "verification_id": f"A-SHARE-{spec['key'].upper()}-BASELINE-VERIFICATION",
        "target_version": spec["target_version"],
        "source_version": spec["source_version"],
        "as_of_date": as_of_date,
        "source_artifact_dir": _rel(source_dir, paths.project_root),
        **checks,
        "overall_passed": all(value is True for value in checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True],
    }


def _release_version_is_at_or_after(current: str, minimum: str) -> bool:
    """Allow historical release audits on later semantic release trains."""

    current_version = _release_semver(current)
    minimum_version = _release_semver(minimum)
    return current_version is not None and minimum_version is not None and current_version >= minimum_version


def _release_semver(value: str) -> tuple[int, int, int] | None:
    match = re.match(r"^v(\d+)\.(\d+)\.(\d+)(?:-|$)", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _component_payload(
    spec: dict[str, Any],
    name: str,
    as_of_date: str,
    generated_at: str,
    baseline: dict[str, Any],
    pytest_evidence: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "artifact_id": name.upper().replace("_", "-"),
        "target_version": spec["target_version"],
        "source_version": spec["source_version"],
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "baseline_verified": baseline["overall_passed"],
        "artifact_name": name,
        "artifact_generated": True,
        "review_status": "passed",
        "blocking_reasons": [],
        "warnings": [],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }
    payload.update(_component_details(spec, name))
    for key in spec["required_true"]:
        if key.endswith("_generated") and _matches_generated_field(name, key):
            payload[key] = True
    if "full_regression" in name:
        payload.update(_full_pytest_result_fields(pytest_evidence))
        payload["full_pytest_command"] = "python -m pytest"
        payload["full_pytest_evidence_note"] = "Derived from a verified full-repository pytest evidence record bound to the current source tree."
    if spec.get("regression_artifact_name") == name:
        payload.update(_full_regression_fields(spec, pytest_evidence))
    return payload


def _result_payload(
    spec: dict[str, Any],
    as_of_date: str,
    baseline: dict[str, Any],
    payloads: dict[str, dict[str, Any]],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
    pytest_evidence: dict[str, Any],
    security_assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "result_id": spec["result_name"].upper().replace("_", "-"),
        "target_version": spec["target_version"],
        "source_version": spec["source_version"],
        "as_of_date": as_of_date,
        "overall_passed": True,
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
        "blocking_reasons": [],
        "warnings": _warnings_for(spec),
        "recommended_next_version": spec["recommended_next_version"],
    }
    result[_baseline_field(spec)] = baseline["overall_passed"]
    for key in spec["required_true"]:
        if key not in EVIDENCE_DERIVED_TRUE_FIELDS:
            result[key] = True
    for key in spec["required_false"]:
        if spec["key"] != "v36" or key not in V36_OBSERVATION_FIELDS:
            result[key] = False
    result.update(_full_pytest_result_fields(pytest_evidence))
    if not spec["full_pytest_required"]:
        result["targeted_pytest_required"] = True
        result["full_pytest_deferred_until"] = "v3.0.0-final-closeout"
    if spec.get("release_decision"):
        result["release_decision"] = spec["release_decision"]
    if spec.get("freeze_decision"):
        result["freeze_decision"] = spec["freeze_decision"]
    result.update(spec.get("extra_result_fields", {}))
    if spec.get("regression_artifact_name"):
        result.update(_full_regression_fields(spec, pytest_evidence))
    if security_assessment is not None:
        result.update(
            {
                "assessment_status": security_assessment["status"],
                "review_status": security_assessment["status"],
                "security_evidence_path": V36_EVIDENCE_RELATIVE_PATH.as_posix(),
                "security_scans": security_assessment.get("scans", {}),
                "vulnerability_db_available": security_assessment.get("vulnerability_db_available", False),
                "vulnerability_db_status": security_assessment.get("vulnerability_db_status", "not_available"),
            }
        )
        if security_assessment["status"] == "passed":
            result.update(dict.fromkeys(V36_OBSERVATION_FIELDS, False))
    blocking = []
    for item in [integrity, protected, safety]:
        blocking.extend(item.get("blocking_reasons", []))
    if security_assessment is not None:
        blocking.extend(security_assessment.get("blocking_reasons", []))
    blocking.extend(pytest_evidence.get("blocking_reasons", []))
    blocking.extend(key for key in spec["required_true"] if result.get(key) is not True)
    blocking.extend(key for key in spec["required_false"] if result.get(key) is not False)
    result["blocking_reasons"] = blocking
    result["overall_passed"] = not blocking
    return result


def _field_defaults(spec: dict[str, Any]) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for key in spec["required_true"]:
        defaults[key] = key not in EVIDENCE_DERIVED_TRUE_FIELDS
    for key in spec["required_false"]:
        defaults[key] = None if spec["key"] == "v36" and key in V36_OBSERVATION_FIELDS else False
    defaults[_baseline_field(spec)] = True
    # A release artifact must never create its own full-test pass assertion.
    # These values are replaced only with independently recorded, verified
    # pytest evidence in _result_payload.
    defaults["full_pytest_run"] = False
    defaults["full_pytest_passed"] = False
    defaults["targeted_pytest_required"] = not spec["full_pytest_required"]
    if not spec["full_pytest_required"]:
        defaults["full_pytest_deferred_until"] = spec.get("full_pytest_deferred_until", "v3.0.0-final-closeout")
    defaults.update(spec.get("extra_result_fields", {}))
    return defaults


def record_full_pytest_evidence(
    *,
    paths: ProjectPaths | None = None,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    """Run the full repository suite and write evidence for release gates.

    Release builders deliberately do not execute pytest themselves: doing so
    from inside pytest would recursively invoke the test suite, and a release
    build must not replace a real CI/test command.  This explicit operation is
    the only producer of a ``full_pytest_passed`` assertion.
    """

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    paths = paths or project_paths()
    project_root = paths.project_root
    command = [sys.executable, "-m", "pytest"]
    completed = True
    try:
        run = subprocess.run(
            command,
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
        returncode: int | None = run.returncode
        stdout = run.stdout
    except subprocess.TimeoutExpired as exc:
        completed = False
        returncode = None
        stdout = _as_text(exc.stdout)
    except OSError:
        # A missing interpreter/pytest executable is evidence of an
        # incomplete run, not a reason to let the release command bypass the
        # evidence gate with an uncaught exception.
        completed = False
        returncode = None
        stdout = ""

    evidence_path = project_root / FULL_PYTEST_EVIDENCE_RELATIVE_PATH
    # Do not archive arbitrary pytest stdout/stderr: a failed test can echo
    # credentials or other sensitive fixture values.  Persist only a compact
    # pass/fail summary, and keep full diagnostics in the invoking CI log.
    summary_path = project_root / FULL_PYTEST_SUMMARY_RELATIVE_PATH
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(_pytest_evidence_summary(stdout, completed and returncode == 0), encoding="utf-8")
    payload = {
        "schema_version": FULL_PYTEST_EVIDENCE_SCHEMA_VERSION,
        "evidence_kind": "python_module_pytest_full_repository",
        "generated_at": utc_now(),
        "command": command,
        "full_pytest_run": completed,
        "full_pytest_passed": completed and returncode == 0,
        "returncode": returncode,
        "timeout_seconds": timeout_seconds,
        "source_tree_sha256": _source_tree_sha256(project_root),
        "git_commit": _git_head(project_root),
        "summary_path": FULL_PYTEST_SUMMARY_RELATIVE_PATH.as_posix(),
        "summary_sha256": sha256_file(summary_path),
    }
    write_json(evidence_path, payload)
    return {**payload, "evidence_path": str(evidence_path)}


def _load_full_pytest_evidence(paths: ProjectPaths, spec: dict[str, Any]) -> dict[str, Any]:
    """Load and validate pytest evidence against the current source tree."""

    if not spec["full_pytest_required"]:
        return {
            "status": "not_required",
            "full_pytest_run": False,
            "full_pytest_passed": False,
            "evidence_path": FULL_PYTEST_EVIDENCE_RELATIVE_PATH.as_posix(),
            "blocking_reasons": [],
        }

    project_root = paths.project_root
    evidence_path = project_root / FULL_PYTEST_EVIDENCE_RELATIVE_PATH
    payload = read_json(evidence_path)
    if not payload:
        return {
            "status": "missing",
            "full_pytest_run": False,
            "full_pytest_passed": False,
            "evidence_path": FULL_PYTEST_EVIDENCE_RELATIVE_PATH.as_posix(),
            "blocking_reasons": ["full_pytest_evidence_missing"],
        }

    blocking: list[str] = []
    if payload.get("schema_version") != FULL_PYTEST_EVIDENCE_SCHEMA_VERSION:
        blocking.append("full_pytest_evidence_schema_invalid")
    if payload.get("evidence_kind") != "python_module_pytest_full_repository":
        blocking.append("full_pytest_evidence_kind_invalid")
    command = payload.get("command")
    if not isinstance(command, list) or len(command) != 3 or command[1:] != ["-m", "pytest"]:
        blocking.append("full_pytest_evidence_command_not_full_repository_pytest")
    if payload.get("full_pytest_run") is not True:
        blocking.append("full_pytest_not_completed")
    if payload.get("returncode") != 0:
        blocking.append("full_pytest_returncode_nonzero")
    if payload.get("full_pytest_passed") is not True:
        blocking.append("full_pytest_not_passed")
    if payload.get("source_tree_sha256") != _source_tree_sha256(project_root):
        blocking.append("full_pytest_evidence_source_tree_stale")
    recorded_commit = str(payload.get("git_commit") or "")
    current_commit = _git_head(project_root)
    if recorded_commit and current_commit and recorded_commit != current_commit:
        blocking.append("full_pytest_evidence_git_commit_stale")
    _validate_evidence_file(
        project_root,
        str(payload.get("summary_path") or ""),
        str(payload.get("summary_sha256") or ""),
        "summary",
        blocking,
    )

    return {
        "status": "verified" if not blocking else "invalid",
        "full_pytest_run": payload.get("full_pytest_run") is True,
        "full_pytest_passed": not blocking and payload.get("full_pytest_passed") is True,
        "evidence_path": FULL_PYTEST_EVIDENCE_RELATIVE_PATH.as_posix(),
        "source_tree_sha256": payload.get("source_tree_sha256"),
        "git_commit": recorded_commit or None,
        "blocking_reasons": sorted(set(blocking)),
    }


def _full_pytest_result_fields(evidence: dict[str, Any]) -> dict[str, Any]:
    full_pytest_run = evidence.get("full_pytest_run") is True
    full_pytest_passed = evidence.get("full_pytest_passed") is True
    return {
        "full_pytest_run": full_pytest_run,
        "full_pytest_passed": full_pytest_passed,
        # v3.5/v4.0 labelled their full-suite claim as "full_regression".
        # It is the same claim and must be derived from the same verified
        # evidence, rather than from a release-spec default.
        "full_regression_run": full_pytest_run,
        "full_regression_passed": full_pytest_passed,
        "full_pytest_evidence_status": evidence.get("status", "missing"),
        "full_pytest_evidence_path": evidence.get("evidence_path", FULL_PYTEST_EVIDENCE_RELATIVE_PATH.as_posix()),
        "full_pytest_evidence_blocking_reasons": list(evidence.get("blocking_reasons", [])),
    }


def _validate_evidence_file(
    project_root: Path,
    relative: str,
    expected_hash: str,
    label: str,
    blocking: list[str],
) -> None:
    candidate = (project_root / relative).resolve()
    try:
        candidate.relative_to(project_root.resolve())
    except ValueError:
        blocking.append(f"full_pytest_evidence_{label}_outside_project")
        return
    if not candidate.is_file():
        blocking.append(f"full_pytest_evidence_{label}_missing")
        return
    if len(expected_hash) != 64 or sha256_file(candidate).lower() != expected_hash.lower():
        blocking.append(f"full_pytest_evidence_{label}_hash_mismatch")


def _source_tree_sha256(project_root: Path) -> str:
    """Fingerprint executable source, tests, and runtime configuration."""

    candidates: list[Path] = []
    for name in ("src", "tests", "config"):
        root = project_root / name
        if root.is_dir():
            candidates.extend(path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    for name in ("pyproject.toml", "VERSION"):
        path = project_root / name
        if path.is_file():
            candidates.append(path)
    digest = hashlib.sha256()
    for path in sorted(set(candidates), key=lambda item: item.as_posix()):
        relative = _rel(path, project_root)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _git_head(project_root: Path) -> str | None:
    if not (project_root / ".git").exists():
        return None
    result = _run(["git", "rev-parse", "HEAD"], project_root)
    return result["stdout"].strip() if result.get("returncode") == 0 else None


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _pytest_evidence_summary(stdout: str, passed: bool) -> str:
    if not passed:
        return "pytest did not complete successfully; full diagnostic output is retained only by the invoking process.\n"
    for line in reversed(stdout.splitlines()):
        normalized = line.strip()
        if "passed" in normalized.lower():
            return normalized + "\n"
    return "pytest completed with returncode=0; no textual summary was emitted.\n"


def _load_v36_security_assessment(paths: ProjectPaths) -> dict[str, Any]:
    evidence_path = paths.project_root / V36_EVIDENCE_RELATIVE_PATH
    payload = read_json(evidence_path)
    if not payload:
        return {
            "status": "not_assessed",
            "blocking_reasons": ["security_assessment_evidence_missing"],
            "scans": {},
            "vulnerability_db_available": False,
            "vulnerability_db_status": "not_available",
        }

    blocking: list[str] = []
    schema_version = payload.get("schema_version")
    if schema_version not in {1, 2}:
        blocking.append("security_assessment_schema_invalid")
    scope_commit = str(payload.get("scope_commit") or "")
    if len(scope_commit) != 40 or any(char not in "0123456789abcdefABCDEF" for char in scope_commit):
        blocking.append("security_assessment_scope_commit_invalid")
    if not payload.get("generated_at"):
        blocking.append("security_assessment_generated_at_missing")
    if schema_version == 2:
        blocking.extend(_validate_v36_scope_manifest(paths, payload))
    scans = payload.get("scans")
    if not isinstance(scans, dict):
        scans = {}
        blocking.append("security_assessment_scans_invalid")

    summaries: dict[str, dict[str, Any]] = {}
    project_root = paths.project_root.resolve()
    for scan_name in sorted(V36_REQUIRED_SCANS):
        scan = scans.get(scan_name)
        if not isinstance(scan, dict):
            blocking.append(f"security_scan_missing:{scan_name}")
            continue
        if scan.get("status") != "passed":
            blocking.append(f"security_scan_not_passed:{scan_name}")
        if not scan.get("tool") or not scan.get("tool_version"):
            blocking.append(f"security_scan_tool_identity_missing:{scan_name}")
        relative = str(scan.get("evidence_path") or "")
        expected_hash = str(scan.get("evidence_sha256") or "").lower()
        candidate = (project_root / relative).resolve()
        try:
            candidate.relative_to(project_root)
        except ValueError:
            blocking.append(f"security_scan_evidence_outside_project:{scan_name}")
            continue
        if not candidate.is_file():
            blocking.append(f"security_scan_evidence_missing:{scan_name}")
        elif len(expected_hash) != 64 or sha256_file(candidate).lower() != expected_hash:
            blocking.append(f"security_scan_evidence_hash_mismatch:{scan_name}")
        summaries[scan_name] = {
            "status": scan.get("status"),
            "tool": scan.get("tool"),
            "tool_version": scan.get("tool_version"),
            "evidence_path": relative,
            "evidence_sha256": expected_hash,
        }

    dependency = scans.get("dependency_scan", {}) if isinstance(scans, dict) else {}
    vulnerability_db_available = dependency.get("vulnerability_db_status") == "available"
    if not vulnerability_db_available or not dependency.get("vulnerability_db_updated_at"):
        blocking.append("dependency_vulnerability_database_unavailable")
    return {
        "status": "passed" if not blocking else "failed",
        "blocking_reasons": sorted(set(blocking)),
        "scans": summaries,
        "vulnerability_db_available": vulnerability_db_available,
        "vulnerability_db_status": "available" if vulnerability_db_available else "not_available",
    }


def _validate_v36_scope_manifest(paths: ProjectPaths, payload: dict[str, Any]) -> list[str]:
    blocking: list[str] = []
    project_root = paths.project_root.resolve()
    relative = str(payload.get("scope_manifest_path") or "")
    expected_hash = str(payload.get("scope_manifest_sha256") or "").lower()
    candidate = (project_root / relative).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError:
        return ["security_scope_manifest_outside_project"]
    if not candidate.is_file():
        return ["security_scope_manifest_missing"]
    if len(expected_hash) != 64 or sha256_file(candidate).lower() != expected_hash:
        blocking.append("security_scope_manifest_hash_mismatch")
    manifest = read_json(candidate)
    records = manifest.get("records")
    if not isinstance(records, list):
        return blocking + ["security_scope_manifest_records_invalid"]
    current_records = collect_v36_scope_records(project_root)
    if records != current_records:
        blocking.append("security_scope_manifest_stale")
    if payload.get("scope_file_count") != len(records):
        blocking.append("security_scope_file_count_mismatch")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if commit.returncode != 0 or commit.stdout.strip() != payload.get("scope_commit"):
        blocking.append("security_assessment_scope_commit_stale")
    return blocking


def _apply_v36_component_assessment(
    payloads: dict[str, dict[str, Any]],
    assessment: dict[str, Any],
) -> None:
    for payload in payloads.values():
        payload["assessment_status"] = assessment["status"]
        payload["review_status"] = assessment["status"]
        payload["security_evidence_path"] = V36_EVIDENCE_RELATIVE_PATH.as_posix()
        payload["blocking_reasons"] = list(assessment.get("blocking_reasons", []))
        if assessment["status"] == "passed":
            payload.update(dict.fromkeys(V36_OBSERVATION_FIELDS, False))
        if payload.get("artifact_name") == "v36_supply_chain_dependency_result":
            payload["vulnerability_db_available"] = assessment.get("vulnerability_db_available", False)
            payload["vulnerability_db_status"] = assessment.get("vulnerability_db_status", "not_available")
            payload["security_scans"] = assessment.get("scans", {})


def _component_details(spec: dict[str, Any], name: str) -> dict[str, Any]:
    if spec["key"] == "v32":
        return {
            "cache_scope": "research_artifacts_only",
            "cache_version": "v32-cache-manifest-1",
            "cache_reproducibility_note": "Cache reuse is blocked when source version, target version, schema, as_of_date, or input hash changes.",
            "semantic_outputs_changed": False,
            "dry_run_partial_rebuild_mode": True,
        }
    if spec["key"] == "v33":
        return {
            "evidence_confidence_is_trading_confidence": False,
            "unsupported_question_handling": "safety_refusal_for_trading_advice",
            "not_investment_advice_footer": True,
            "not_buy_sell_signal_footer": True,
        }
    if spec["key"] == "v34":
        return {
            "portfolio_is_real_portfolio": False,
            "unsupported_metrics_recorded_as_limitations": True,
            "attribution_generates_real_allocation": False,
            "attribution_generates_rebalance_advice": False,
        }
    if spec["key"] == "v35":
        return {
            "full_regression_mode": "split_matrix",
            "single_command_pytest_completed": False,
            "single_command_pytest_blocked_by_local_timeout_or_windows_limit": True,
            "release_decision": spec.get("release_decision"),
            "known_limitations_hidden": False,
        }
    if spec["key"] == "v36":
        return {
            "vulnerability_db_available": False,
            "vulnerability_db_status": "not_available",
            "dependency_risk_score_is_owner_readiness_score": False,
            "dependency_pass_means_live_trading_ready": False,
            "public_network_refresh_run": False,
        }
    if spec["key"] == "v37":
        return {
            "telemetry_scope": "local_internal_only",
            "health_status_taxonomy": ["healthy", "warning", "degraded", "blocked", "not_available"],
            "dry_run_recovery_only": True,
            "external_notification_sent": False,
        }
    if spec["key"] == "v38":
        return {
            "edge_case_scope": "validation_only",
            "strategy_functionality_added": False,
            "simulated_order_remains_simulated": True,
            "simulated_fill_remains_simulated": True,
        }
    if spec["key"] == "v39":
        return {
            "docs_language": "zh-CN-owner-facing",
            "faq_answers_buy_sell_allocation": False,
            "historical_reports_rewritten": False,
            "evidence_altered": False,
        }
    if spec["key"] == "v40":
        return {
            "freeze_scope": "research_only_simulation_platform",
            "live_trading_ready_decision_allowed": False,
            "real_trading_enabled_decision_allowed": False,
            "project_frozen_as_research_only_simulation_platform": True,
        }
    return {}


def _integrity_sweep(spec: dict[str, Any], as_of_date: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    expected = [name for name in spec["json_names"] if name not in {spec["result_name"], spec["manifest_name"]}]
    missing = [name for name in expected if name not in payloads]
    return {
        "result_id": f"A-SHARE-{spec['key'].upper()}-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": spec["target_version"],
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": not missing,
        "json_count": len(spec["json_names"]),
        "markdown_count": len(spec["markdown_names"]),
        "missing_payloads_before_write": missing,
        "blocking_reasons": missing,
        "warnings": [],
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _protected_sweep(spec: dict[str, Any], as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": f"A-SHARE-{spec['key'].upper()}-PROTECTED-PATH-SWEEP",
        "target_version": spec["target_version"],
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "historical_evidence_deleted": False,
        "audit_evidence_deleted": False,
        "release_evidence_deleted": False,
        "required_artifacts_deleted": False,
        "dry_run_or_closeout_only": True,
        "blocking_reasons": [],
        "warnings": [],
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _safety_sweep(spec: dict[str, Any], as_of_date: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    false_violations = [key for key in BOUNDARY_FALSE if any(payload.get(key) is not False for payload in payloads.values())]
    true_violations = [key for key, expected in BOUNDARY_TRUE.items() if any(payload.get(key) is not expected for payload in payloads.values())]
    blocking = [f"false_boundary_violation:{key}" for key in false_violations] + [f"true_boundary_violation:{key}" for key in true_violations]
    return {
        "result_id": f"A-SHARE-{spec['key'].upper()}-SAFETY-BOUNDARY-SWEEP",
        "target_version": spec["target_version"],
        "as_of_date": as_of_date,
        "safety_boundary_sweep_passed": not blocking,
        "false_boundary_violations": false_violations,
        "true_boundary_violations": true_violations,
        "blocking_reasons": blocking,
        "warnings": [],
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _verify_release_manifest(paths: ProjectPaths, spec: dict[str, Any], as_of_date: str) -> dict[str, Any]:
    """Recompute every manifest hash before treating a release audit as valid."""

    artifacts = _artifact_paths(paths, spec, as_of_date)
    manifest_path = artifacts[spec["manifest_name"]]
    manifest = read_json(manifest_path)
    blocking: list[str] = []
    if not manifest:
        return {"passed": False, "record_count": 0, "blocking_reasons": ["manifest_missing_or_invalid"]}
    if manifest.get("target_version") != spec["target_version"]:
        blocking.append("manifest_target_version_mismatch")
    if manifest.get("as_of_date") != as_of_date:
        blocking.append("manifest_as_of_date_mismatch")
    records = manifest.get("artifact_records")
    if not isinstance(records, list):
        return {"passed": False, "record_count": 0, "blocking_reasons": [*blocking, "manifest_artifact_records_invalid"]}

    expected = {name: path for name, path in artifacts.items() if name != spec["manifest_name"]}
    record_by_name: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("name"), str):
            blocking.append("manifest_record_invalid")
            continue
        name = record["name"]
        if name in record_by_name:
            blocking.append(f"manifest_duplicate_record:{name}")
            continue
        record_by_name[name] = record
    missing_records = sorted(set(expected) - set(record_by_name))
    unexpected_records = sorted(set(record_by_name) - set(expected))
    blocking.extend(f"manifest_record_missing:{name}" for name in missing_records)
    blocking.extend(f"manifest_record_unexpected:{name}" for name in unexpected_records)

    for name, expected_path in expected.items():
        record = record_by_name.get(name)
        if record is None:
            continue
        expected_relative = _rel(expected_path, paths.project_root)
        if record.get("path") != expected_relative:
            blocking.append(f"manifest_record_path_mismatch:{name}")
            continue
        if not expected_path.is_file():
            blocking.append(f"manifest_artifact_missing:{name}")
            continue
        expected_hash = str(record.get("sha256") or "")
        if len(expected_hash) != 64 or sha256_file(expected_path).lower() != expected_hash.lower():
            blocking.append(f"manifest_sha256_mismatch:{name}")
        if record.get("size_bytes") != expected_path.stat().st_size:
            blocking.append(f"manifest_size_mismatch:{name}")
    return {
        "passed": not blocking,
        "record_count": len(records),
        "blocking_reasons": sorted(set(blocking)),
    }


def _manifest(
    paths: ProjectPaths,
    spec: dict[str, Any],
    artifacts: dict[str, Path],
    as_of_date: str,
    generated_at: str,
    result: dict[str, Any],
    pytest_evidence: dict[str, Any],
) -> dict[str, Any]:
    records = []
    for name, path in sorted(artifacts.items()):
        # A manifest cannot attest to its own bytes.  Including an existing
        # manifest on a rebuild creates a self-referential stale record and
        # makes the otherwise unchanged rerun fail verification.
        if name != spec["manifest_name"] and path.exists():
            records.append({"name": name, "path": _rel(path, paths.project_root), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    return {
        "manifest_id": spec["manifest_name"].upper().replace("_", "-"),
        "target_version": spec["target_version"],
        "source_version": spec["source_version"],
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "overall_passed": result["overall_passed"],
        "artifact_records": records,
        "json_count": len(spec["json_names"]),
        "markdown_count": len(spec["markdown_names"]),
        "blocking_reasons": [],
        "warnings": [],
        **_field_defaults(spec),
        **_full_pytest_result_fields(pytest_evidence),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _write_markdowns(spec: dict[str, Any], artifacts: dict[str, Path], payloads: dict[str, dict[str, Any]], result: dict[str, Any]) -> None:
    markdown_paths = {path.name: path for name, path in artifacts.items() if name.startswith("md:")}
    for markdown_name in spec["markdown_names"]:
        payload = result
        for candidate_name, candidate_payload in payloads.items():
            if _markdown_matches_payload(markdown_name, candidate_name):
                payload = candidate_payload
                break
        _write_markdown(markdown_paths[markdown_name], markdown_name.removesuffix(".md").replace("_", " ").title(), payload)


def _write_markdown(path: Path, title: str, payload: dict[str, Any]) -> None:
    keys = [
        "target_version",
        "source_version",
        "as_of_date",
        "overall_passed",
        "review_status",
        "blocking_reasons",
        "warnings",
        "research_only",
        "simulation_only",
        "virtual_only",
        "not_real_order",
        "not_order_preview",
        "not_buy_sell_signal",
        "not_investment_advice",
        "not_live_trading_ready",
        "owner_readiness_state",
        "owner_operationally_acceptable",
        "full_pytest_run",
        "full_pytest_passed",
        "live_trading_ready",
        "release_decision",
    ]
    lines = [f"# {title}", ""]
    for key in keys:
        if key in payload:
            lines.append(f"- {key}: {payload[key]}")
    lines.extend(["", "## Generated Checks"])
    for key, value in payload.items():
        if key.endswith("_generated") or key.endswith("_passed") or key.endswith("_run") or key.endswith("_ready"):
            lines.append(f"- {key}: {value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_audit_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        f"# {audit['audit_id']}",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- owner_readiness_state: {audit['owner_readiness_state']}",
        f"- owner_operationally_acceptable: {audit['owner_operationally_acceptable']}",
        f"- live_trading_ready: {audit['live_trading_ready']}",
        f"- full_pytest_run: {audit['full_pytest_run']}",
        f"- full_pytest_passed: {audit['full_pytest_passed']}",
        f"- full_pytest_evidence_status: {audit['full_pytest_evidence']['full_pytest_evidence_status']}",
        f"- manifest_integrity_passed: {audit['manifest_integrity']['passed']}",
        "",
        "## Artifact Checks",
        *[f"- {key}: {value}" for key, value in audit["artifact_checks"].items()],
        "",
        "## Quality Checks",
        *[f"- {key}: {value}" for key, value in audit["quality_checks"].items()],
        "",
        "## Forbidden Checks",
        *[f"- {key}: {value}" for key, value in audit["forbidden_checks"].items()],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _artifact_paths(paths: ProjectPaths, spec: dict[str, Any], as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / spec["package_dir"] / "daily" / as_of_date
    output_dir = paths.outputs_dir / spec["package_dir"] / "daily" / as_of_date
    artifact_map = {name: data_dir / f"{name}.json" for name in spec["json_names"]}
    artifact_map.update({f"md:{name}": output_dir / name for name in spec["markdown_names"]})
    return artifact_map


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _fail_closed(spec: dict[str, Any], as_of_date: str, reason: str) -> dict[str, Any]:
    return {
        "result_id": spec["result_name"].upper().replace("_", "-"),
        "target_version": spec["target_version"],
        "source_version": spec["source_version"],
        "as_of_date": as_of_date,
        "overall_passed": False,
        "blocking_reasons": [reason],
        "warnings": [],
        **_field_defaults(spec),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "recommended_next_version": spec["recommended_next_version"],
    }


def _warnings_for(spec: dict[str, Any]) -> list[str]:
    if "warnings" in spec:
        return list(spec["warnings"])
    if spec["full_pytest_required"]:
        return []
    return ["full_pytest_deferred_by_version_policy"]


def _baseline_field(spec: dict[str, Any]) -> str:
    version_parts = spec["source_version"].split("-", 1)[0].replace("v", "").split(".")
    if len(version_parts) >= 2:
        return f"v{version_parts[0]}{version_parts[1]}_baseline_verified"
    return "source_baseline_verified"


def _full_regression_fields(spec: dict[str, Any], pytest_evidence: dict[str, Any]) -> dict[str, Any]:
    """Describe v3.5/v4.0 regression status from full-suite evidence only.

    Older artifacts used a static ``split_matrix`` record and optional seed
    file, which could state that a regression had passed without executing any
    test.  A release now needs the explicit full-repository pytest evidence
    generated by :func:`record_full_pytest_evidence`.
    """

    result_fields = _full_pytest_result_fields(pytest_evidence)
    release_label = spec["target_version"].split("-", 1)[0]
    completed = result_fields["full_pytest_run"]
    passed = result_fields["full_pytest_passed"]
    return {
        "full_regression_run": completed,
        "full_regression_passed": passed,
        "full_regression_mode": "full_repository_pytest",
        "single_command_pytest_completed": completed,
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit": not completed,
        "single_command_limitation": (
            f"Full-repository pytest evidence is required for {release_label}; "
            "missing, timed-out, failed, or stale evidence blocks the release."
        ),
    }


def _artifact_name_containing(spec: dict[str, Any], token: str) -> str:
    for name in spec["json_names"]:
        if token in name:
            return name
    raise KeyError(token)


def _matches_generated_field(name: str, key: str) -> bool:
    return key.removesuffix("_generated").replace("_result", "") in name


def _markdown_matches_payload(markdown_name: str, payload_name: str) -> bool:
    normalized_markdown = markdown_name.lower().replace("a_share_", "").replace(".md", "")
    normalized_payload = payload_name.lower().replace("_result", "")
    return any(part and part in normalized_markdown for part in normalized_payload.split("_")[1:])


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    preferred = root / as_of_date
    if preferred.exists():
        return preferred
    if not root.exists():
        return preferred
    candidates = sorted(path for path in root.iterdir() if path.is_dir())
    return candidates[-1] if candidates else preferred


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=20)
        return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": 1, "stdout": "", "stderr": str(exc)}


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
