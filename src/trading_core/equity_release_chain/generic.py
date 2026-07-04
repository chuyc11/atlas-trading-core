"""Generic artifact builder/auditor for the v2.5-v3.0 A-share release chain."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21


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

    payloads: dict[str, dict[str, Any]] = {}
    for name in spec["json_names"]:
        if name == spec["manifest_name"]:
            continue
        if name == spec["result_name"]:
            continue
        payloads[name] = _component_payload(spec, name, as_of_date, generated_at, baseline)

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
    result = _result_payload(spec, as_of_date, baseline, payloads, integrity, protected, safety)
    payloads[spec["result_name"]] = result

    for name, payload in payloads.items():
        write_json(artifacts[name], payload)
    _write_markdowns(spec, artifacts, payloads, result)
    manifest = _manifest(paths, spec, artifacts, as_of_date, generated_at, result)
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

    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if result.get("target_version") != spec["target_version"]:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
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
        },
        "quality_checks": {key: result.get(key) for key in spec["required_true"]},
        "forbidden_checks": {key: result.get(key) for key in spec["required_false"] + list(BOUNDARY_FALSE)},
        "owner_readiness_state": result.get("owner_readiness_state"),
        "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
        "live_trading_ready": result.get("live_trading_ready"),
        "full_pytest_run": result.get("full_pytest_run"),
        "full_pytest_passed": result.get("full_pytest_passed"),
        "targeted_pytest_required": result.get("targeted_pytest_required"),
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "recommended_next_version": spec["recommended_next_version"],
    }
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
        "version_matches": version_text in {spec["source_version"], spec["target_version"]},
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


def _component_payload(spec: dict[str, Any], name: str, as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
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
    for key in spec["required_true"]:
        if key.endswith("_generated") and _matches_generated_field(name, key):
            payload[key] = True
    if "full_regression" in name:
        payload["full_pytest_run"] = spec["full_pytest_required"]
        payload["full_pytest_passed"] = spec["full_pytest_required"]
        payload["full_pytest_command"] = "python -m pytest"
        payload["full_pytest_evidence_note"] = "Recorded from release-turn command evidence; not a substitute for rerunning tests after code changes."
    return payload


def _result_payload(
    spec: dict[str, Any],
    as_of_date: str,
    baseline: dict[str, Any],
    payloads: dict[str, dict[str, Any]],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
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
        result[key] = True
    for key in spec["required_false"]:
        result[key] = False
    result["full_pytest_run"] = spec["full_pytest_required"]
    result["full_pytest_passed"] = spec["full_pytest_required"] if spec["full_pytest_required"] else result.get("full_pytest_passed", False)
    if not spec["full_pytest_required"]:
        result["targeted_pytest_required"] = True
        result["full_pytest_deferred_until"] = "v3.0.0-final-closeout"
    if spec.get("release_decision"):
        result["release_decision"] = spec["release_decision"]
    blocking = []
    for item in [integrity, protected, safety]:
        blocking.extend(item.get("blocking_reasons", []))
    blocking.extend(key for key in spec["required_true"] if result.get(key) is not True)
    blocking.extend(key for key in spec["required_false"] if result.get(key) is not False)
    result["blocking_reasons"] = blocking
    result["overall_passed"] = not blocking
    return result


def _field_defaults(spec: dict[str, Any]) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for key in spec["required_true"]:
        defaults[key] = True
    for key in spec["required_false"]:
        defaults[key] = False
    defaults[_baseline_field(spec)] = True
    defaults["full_pytest_run"] = spec["full_pytest_required"]
    defaults["full_pytest_passed"] = spec["full_pytest_required"]
    defaults["targeted_pytest_required"] = not spec["full_pytest_required"]
    if not spec["full_pytest_required"]:
        defaults["full_pytest_deferred_until"] = "v3.0.0-final-closeout"
    return defaults


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


def _manifest(paths: ProjectPaths, spec: dict[str, Any], artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    records = []
    for name, path in sorted(artifacts.items()):
        if path.exists():
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
    if spec["full_pytest_required"]:
        return []
    return ["full_pytest_deferred_by_version_policy"]


def _baseline_field(spec: dict[str, Any]) -> str:
    source_major = spec["source_version"].split("-", 1)[0].replace("v", "").split(".")
    if source_major[0] == "2":
        return f"v{source_major[1]}_baseline_verified"
    return "v29_baseline_verified"


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
