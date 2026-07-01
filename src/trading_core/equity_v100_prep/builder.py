"""Build v1.0.0-prep closeout artifacts for the A-share simulation platform."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout"
SOURCE_VERSION = "v0.9.8-a-share-v09-autonomous-research-and-simulation-platform-completion"
RECOMMENDED_NEXT_VERSION = "v1.0.0-a-share-autonomous-simulation-platform-release"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

V09_JSON_NAMES = [
    "v09_platform_request",
    "v09_daily_workflow_result",
    "v09_simulated_account_state",
    "v09_virtual_broker_execution_report",
    "v09_paper_ledger_snapshot",
    "v09_benchmark_attribution_result",
    "v09_owner_dashboard_result",
    "v09_monitoring_alerts_result",
    "v09_evidence_auto_accumulation_result",
    "v09_experiment_registry",
    "v09_strategy_registry",
    "v09_llm_research_proposal_register",
    "v09_automated_experiment_result",
    "v09_rl_simulated_strategy_lab_result",
    "v09_shadow_canary_promotion_result",
    "v09_platform_boundary_check",
    "v09_platform_manifest",
]
V09_MARKDOWN_NAMES = [
    "A_SHARE_V09_DAILY_RESEARCH_PLATFORM_REPORT.md",
    "A_SHARE_V09_SIMULATED_ACCOUNT_AND_VIRTUAL_BROKER_REPORT.md",
    "A_SHARE_V09_BENCHMARK_ATTRIBUTION_REPORT.md",
    "A_SHARE_V09_AUTONOMOUS_RESEARCH_AND_SIMULATION_REPORT.md",
    "A_SHARE_V09_OWNER_COMMAND_CENTER.md",
]
V100_JSON_NAMES = [
    "v100_prep_request",
    "v098_platform_verification",
    "v098_warning_classification",
    "v100_full_regression_result",
    "v100_cli_surface_verification",
    "v100_artifact_integrity_check",
    "v100_safety_boundary_sweep",
    "v100_release_readiness_decision",
    "v100_prep_manifest",
]
V100_MARKDOWN_NAMES = [
    "A_SHARE_V100_PREP_RELEASE_READINESS_REPORT.md",
    "A_SHARE_V100_PREP_FULL_REGRESSION_RESULT.md",
    "A_SHARE_V100_PREP_SAFETY_BOUNDARY_SWEEP.md",
]
V09_CLI_COMMANDS = [
    "owner-daily-status",
    "run-a-share-v09-daily-platform",
    "audit-a-share-v09-platform",
    "run-and-audit-a-share-v09-platform",
    "build-a-share-experiment-registry",
    "run-a-share-automated-experiments",
    "run-a-share-rl-simulated-strategy-lab",
    "evaluate-a-share-simulated-strategy-promotion",
]


def build_a_share_v100_prep(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    v09_payloads = _load_v09_payloads(paths, as_of_date)
    owner_status = _owner_daily_status(paths, as_of_date)
    request = _prep_request(as_of_date)
    platform = _verify_v098_platform(paths, as_of_date, v09_payloads, owner_status)
    warnings = _classify_warnings(as_of_date, v09_payloads)
    full_regression = _load_or_run_full_pytest(paths, as_of_date)
    cli_surface = _verify_cli_surface(paths, as_of_date, v09_payloads, owner_status)
    integrity = _artifact_integrity(paths, as_of_date)
    boundary = _safety_boundary_sweep(as_of_date, v09_payloads, owner_status)
    decision = _release_readiness_decision(as_of_date, platform, warnings, full_regression, cli_surface, integrity, boundary)

    payloads = {
        "v100_prep_request": request,
        "v098_platform_verification": platform,
        "v098_warning_classification": warnings,
        "v100_full_regression_result": full_regression,
        "v100_cli_surface_verification": cli_surface,
        "v100_artifact_integrity_check": integrity,
        "v100_safety_boundary_sweep": boundary,
        "v100_release_readiness_decision": decision,
    }
    manifest = _manifest(paths, as_of_date, payloads, decision)
    payloads["v100_prep_manifest"] = manifest
    artifacts = _artifact_paths(paths, as_of_date)
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, decision, warnings, full_regression, boundary)
    return _summary(decision, warnings, full_regression, cli_surface, integrity, boundary)


def _prep_request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V100-PREP-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "scope": [
            "v098_platform_verification",
            "warning_classification",
            "full_regression",
            "cli_surface_verification",
            "artifact_integrity_check",
            "safety_boundary_sweep",
            "release_readiness_decision",
        ],
        "no_new_product_features": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _verify_v098_platform(paths: ProjectPaths, as_of_date: str, payloads: dict[str, dict[str, Any]], owner_status: dict[str, Any]) -> dict[str, Any]:
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v09_platform_completion_audit.json")
    workflow = payloads["v09_daily_workflow_result"]
    boundary = payloads["v09_platform_boundary_check"]
    automated = payloads["v09_automated_experiment_result"]
    rl_lab = payloads["v09_rl_simulated_strategy_lab_result"]
    promotion = payloads["v09_shadow_canary_promotion_result"]
    version_text = (paths.project_root / "VERSION").read_text(encoding="utf-8").strip()
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root)
    tag_check = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root)
    blocking = []
    if tag_check["stdout"].strip() != SOURCE_VERSION:
        blocking.append("v098_tag_missing")
    if version_text != SOURCE_VERSION:
        blocking.append("version_not_v098_before_release_update")
    if "trading-core 0.9.8" not in cli_version["stdout"]:
        blocking.append("cli_version_not_098_before_release_update")
    if not audit.get("overall_passed"):
        blocking.append("v098_audit_not_passed")
    if audit.get("blocking_reasons"):
        blocking.append("v098_audit_has_blocking_reasons")
    required = {
        "daily_platform_run_passed": workflow.get("run_status") == "passed",
        "automated_experiment_run_passed": automated.get("status") == "passed",
        "rl_simulated_lab_passed": rl_lab.get("status") == "passed",
        "shadow_canary_status_verified": promotion.get("promotion_status") == "simulated_canary_watch",
        "v098_boundary_passed": boundary.get("overall_passed") is True,
        "owner_daily_status_works": bool(owner_status),
    }
    blocking.extend(key for key, value in required.items() if not value)
    return {
        "verification_id": "A-SHARE-V098-PLATFORM-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "v098_tag_exists": tag_check["stdout"].strip() == SOURCE_VERSION,
        "version_before_update": version_text,
        "cli_version_before_update": cli_version["stdout"].strip(),
        "v098_audit_passed": bool(audit.get("overall_passed")),
        "v098_audit_warning_count": len(audit.get("warnings", [])),
        "v098_required_json_count": len(V09_JSON_NAMES),
        "v098_required_markdown_count": len(V09_MARKDOWN_NAMES),
        **required,
        "v098_platform_verified": not blocking,
        "blocking_reasons": blocking,
        "warnings": list(audit.get("warnings", [])),
    }


def _classify_warnings(as_of_date: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    audit_warnings = payloads["v09_benchmark_attribution_result"].get("warnings", [])
    classifications = []
    for warning in audit_warnings:
        if warning == "benchmark_data_missing_recorded_without_fabrication":
            classifications.append(
                {
                    "warning_id": warning,
                    "source_artifact": "data/equity_v09_platform/daily/2026-07-01/v09_benchmark_attribution_result.json",
                    "description": "Benchmark index source data was unavailable, so excess return, tracking error, and relative drawdown were left null instead of fabricated.",
                    "severity": "medium",
                    "blocking_for_v100": False,
                    "recommended_resolution": "Backfill benchmark index history and rerun attribution before making benchmark-relative performance claims.",
                }
            )
        elif warning == "attribution_source_missing_using_simulated_summary":
            classifications.append(
                {
                    "warning_id": warning,
                    "source_artifact": "data/equity_v09_platform/daily/2026-07-01/v09_benchmark_attribution_result.json",
                    "description": "Dedicated attribution source artifacts were unavailable, so the report used the simulation-only account summary and marked attribution status as warning.",
                    "severity": "medium",
                    "blocking_for_v100": False,
                    "recommended_resolution": "Generate a dedicated attribution source package before promoting benchmark attribution from warning to passed.",
                }
            )
        else:
            classifications.append(
                {
                    "warning_id": str(warning),
                    "source_artifact": "data/equity_v09_platform/daily/2026-07-01/v09_platform_completion_audit.json",
                    "description": "Unrecognized v0.9.8 warning; fail closed until manually triaged.",
                    "severity": "high",
                    "blocking_for_v100": True,
                    "recommended_resolution": "Classify this warning explicitly before v1.0.0 release.",
                }
            )
    blocking_count = sum(1 for item in classifications if item["blocking_for_v100"])
    return {
        "classification_id": "A-SHARE-V098-WARNING-CLASSIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "warning_count": len(classifications),
        "blocking_warning_count": blocking_count,
        "warnings_classified": len(classifications) == len(audit_warnings),
        "classifications": classifications,
        "benchmark_attribution_warning_non_blocking": blocking_count == 0,
        "blocking_reasons": [] if blocking_count == 0 else ["blocking_v098_warning_found"],
    }


def _load_or_run_full_pytest(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    path = _artifact_paths(paths, as_of_date)["v100_full_regression_result"]
    existing = read_json(path)
    if existing.get("target_version") == TARGET_VERSION and existing.get("full_regression_passed") is True:
        return {**existing, "reused_existing_result": True}
    started = time.perf_counter()
    result = _run([sys.executable, "-m", "pytest"], paths.project_root, timeout=1_200)
    duration = round(time.perf_counter() - started, 3)
    combined = "\n".join([result["stdout"], result["stderr"]])
    passed = _count(combined, "passed")
    skipped = _count(combined, "skipped")
    failed = _count(combined, "failed")
    errors = _count(combined, "error")
    payload = {
        "result_id": "A-SHARE-V100-FULL-REGRESSION-RESULT",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "command": "python -m pytest",
        "returncode": result["returncode"],
        "full_pytest_run": True,
        "full_regression_passed": result["returncode"] == 0,
        "total_passed": passed,
        "total_skipped": skipped,
        "total_failed": failed,
        "total_errors": errors,
        "duration_seconds": duration,
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
        "reused_existing_result": False,
        "blocking_reasons": [] if result["returncode"] == 0 else ["full_regression_failed"],
    }
    write_json(path, payload)
    return payload


def _verify_cli_surface(paths: ProjectPaths, as_of_date: str, payloads: dict[str, dict[str, Any]], owner_status: dict[str, Any]) -> dict[str, Any]:
    help_results = [_run([sys.executable, "-m", "trading_core.cli", command, "--help"], paths.project_root) for command in V09_CLI_COMMANDS if command != "owner-daily-status"]
    owner_ok = bool(owner_status) and owner_status.get("known_owner_readiness_state") == "blocked"
    workflow = payloads["v09_daily_workflow_result"]
    automated = payloads["v09_automated_experiment_result"]
    rl_lab = payloads["v09_rl_simulated_strategy_lab_result"]
    promotion = payloads["v09_shadow_canary_promotion_result"]
    command_checks = {
        "owner-daily-status": owner_ok,
        "run-a-share-v09-daily-platform": workflow.get("run_status") == "passed",
        "audit-a-share-v09-platform": read_json(paths.data_dir / "equity_data_quality" / "a_share_v09_platform_completion_audit.json").get("overall_passed") is True,
        "run-and-audit-a-share-v09-platform": workflow.get("overall_passed") is True,
        "build-a-share-experiment-registry": payloads["v09_experiment_registry"].get("experiment_count", 0) > 0,
        "run-a-share-automated-experiments": automated.get("status") == "passed",
        "run-a-share-rl-simulated-strategy-lab": rl_lab.get("status") == "passed",
        "evaluate-a-share-simulated-strategy-promotion": promotion.get("promotion_status") == "simulated_canary_watch",
    }
    help_passed = all(item["returncode"] == 0 for item in help_results)
    blocking = [command for command, ok in command_checks.items() if not ok]
    if not help_passed:
        blocking.append("v09_cli_help_failed")
    return {
        "verification_id": "A-SHARE-V100-CLI-SURFACE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "commands": V09_CLI_COMMANDS,
        "command_checks": command_checks,
        "help_smoke_passed": help_passed,
        "cli_surface_verified": not blocking,
        "blocking_reasons": blocking,
        "note": "Command behavior is verified from existing v0.9.8 execution artifacts; help smoke avoids mutating v0.9.8 release artifacts.",
    }


def _artifact_integrity(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    json_paths = _v09_json_paths(paths, as_of_date)
    markdown_paths = _v09_markdown_paths(paths, as_of_date)
    missing_json = [name for name, path in json_paths.items() if not path.exists()]
    missing_md = [path.name for path in markdown_paths if not path.exists()]
    manifest = read_json(json_paths["v09_platform_manifest"])
    hashes = {name: sha256_file(path) for name, path in json_paths.items() if path.exists()}
    hashes.update({path.name: sha256_file(path) for path in markdown_paths if path.exists()})
    manifest_hashes = manifest.get("artifact_hashes", {})
    mismatches = []
    for name, digest in hashes.items():
        if name == "v09_platform_manifest":
            continue
        expected = manifest_hashes.get(name)
        if expected and expected != digest:
            mismatches.append(name)
    blocking = []
    if missing_json:
        blocking.append("v098_json_artifacts_missing")
    if missing_md:
        blocking.append("v098_markdown_reports_missing")
    if mismatches:
        blocking.append("v098_manifest_hash_mismatch")
    return {
        "check_id": "A-SHARE-V100-ARTIFACT-INTEGRITY-CHECK",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "json_count": len(json_paths) - len(missing_json),
        "markdown_count": len(markdown_paths) - len(missing_md),
        "required_json_count": len(V09_JSON_NAMES),
        "required_markdown_count": len(V09_MARKDOWN_NAMES),
        "missing_json": missing_json,
        "missing_markdown": missing_md,
        "manifest_hash_mismatches": mismatches,
        "manifest_hash_self_reference_excluded": True,
        "artifact_hashes": hashes,
        "artifact_integrity_passed": not blocking,
        "blocking_reasons": blocking,
    }


def _safety_boundary_sweep(as_of_date: str, payloads: dict[str, dict[str, Any]], owner_status: dict[str, Any]) -> dict[str, Any]:
    boundary = payloads["v09_platform_boundary_check"]
    workflow = payloads["v09_daily_workflow_result"]
    execution = payloads["v09_virtual_broker_execution_report"]
    proposal = payloads["v09_llm_research_proposal_register"]
    rl_lab = payloads["v09_rl_simulated_strategy_lab_result"]
    promotion = payloads["v09_shadow_canary_promotion_result"]
    blocking = []
    for key in BOUNDARY_TRUE:
        if boundary.get(key) is not True:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if boundary.get(key) is True or workflow.get(key) is True or execution.get(key) is True:
            blocking.append(f"forbidden_boundary_true:{key}")
    if owner_status.get("known_owner_readiness_state") != "blocked":
        blocking.append("owner_readiness_not_blocked")
    if owner_status.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    if owner_status.get("order_preview_generated") is True:
        blocking.append("owner_status_order_preview_generated")
    if proposal.get("external_llm_api_called") is True:
        blocking.append("external_llm_api_called")
    if rl_lab.get("real_account_action_generated") is True:
        blocking.append("rl_real_account_action_generated")
    if promotion.get("real_trading_promotion") is True:
        blocking.append("real_trading_promotion")
    return {
        "sweep_id": "A-SHARE-V100-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "protected_paths_untouched": boundary.get("protected_paths_untouched") is True,
        "external_llm_api_called": proposal.get("external_llm_api_called") is True,
        "real_account_action_generated": rl_lab.get("real_account_action_generated") is True,
        "real_trading_promotion": promotion.get("real_trading_promotion") is True,
        "safety_boundary_sweep_passed": not blocking,
        "blocking_reasons": blocking,
    }


def _release_readiness_decision(
    as_of_date: str,
    platform: dict[str, Any],
    warning: dict[str, Any],
    full_regression: dict[str, Any],
    cli_surface: dict[str, Any],
    integrity: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    if not full_regression["full_regression_passed"]:
        decision = "not_ready_full_regression_failed"
    elif warning["blocking_warning_count"]:
        decision = "not_ready_blocking_warnings"
    elif not boundary["safety_boundary_sweep_passed"]:
        decision = "not_ready_boundary_failure"
    elif not integrity["artifact_integrity_passed"]:
        decision = "not_ready_artifact_integrity_failure"
    elif not platform["v098_platform_verified"] or not cli_surface["cli_surface_verified"]:
        decision = "not_ready_artifact_integrity_failure"
    else:
        decision = "ready_for_v100_release"
    blocking = [
        *platform["blocking_reasons"],
        *warning["blocking_reasons"],
        *full_regression["blocking_reasons"],
        *cli_surface["blocking_reasons"],
        *integrity["blocking_reasons"],
        *boundary["blocking_reasons"],
    ]
    return {
        "decision_id": "A-SHARE-V100-PREP-RELEASE-READINESS-DECISION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "v098_platform_verified": platform["v098_platform_verified"],
        "warnings_classified": warning["warnings_classified"],
        "blocking_warning_count": warning["blocking_warning_count"],
        "full_regression_passed": full_regression["full_regression_passed"],
        "cli_surface_verified": cli_surface["cli_surface_verified"],
        "artifact_integrity_passed": integrity["artifact_integrity_passed"],
        "safety_boundary_sweep_passed": boundary["safety_boundary_sweep_passed"],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "release_readiness_decision": decision,
        "not_owner_readiness_pass": True,
        "not_live_trading_ready": True,
        "blocking_reasons": blocking,
        "warnings": warning["classifications"],
        **{key: boundary[key] for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, as_of_date: str, payloads: dict[str, dict[str, Any]], decision: dict[str, Any]) -> dict[str, Any]:
    artifacts = _artifact_paths(paths, as_of_date)
    return {
        "manifest_id": "A-SHARE-V100-PREP-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "json_artifact_count": len(V100_JSON_NAMES),
        "markdown_report_count": len(V100_MARKDOWN_NAMES),
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()},
        "overall_passed": decision["release_readiness_decision"] == "ready_for_v100_release",
        "blocking_reasons": decision["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _summary(
    decision: dict[str, Any],
    warnings: dict[str, Any],
    full_regression: dict[str, Any],
    cli_surface: dict[str, Any],
    integrity: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-V100-PREP-CLOSEOUT",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": decision["as_of_date"],
        "overall_passed": decision["release_readiness_decision"] == "ready_for_v100_release",
        "release_readiness_decision": decision["release_readiness_decision"],
        "blocking_reasons": decision["blocking_reasons"],
        "warnings": warnings["classifications"],
        "v098_platform_verified": decision["v098_platform_verified"],
        "v098_warnings_count": warnings["warning_count"],
        "blocking_warning_count": warnings["blocking_warning_count"],
        "full_regression_passed": full_regression["full_regression_passed"],
        "full_pytest_passed_count": full_regression["total_passed"],
        "full_pytest_skipped_count": full_regression["total_skipped"],
        "full_pytest_failed_count": full_regression["total_failed"],
        "full_pytest_duration_seconds": full_regression["duration_seconds"],
        "cli_surface_verified": cli_surface["cli_surface_verified"],
        "artifact_integrity_passed": integrity["artifact_integrity_passed"],
        "safety_boundary_sweep_passed": boundary["safety_boundary_sweep_passed"],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **{key: boundary[key] for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_reports(artifacts: dict[str, Path], decision: dict[str, Any], warnings: dict[str, Any], full_regression: dict[str, Any], boundary: dict[str, Any]) -> None:
    _write_text(
        artifacts["readiness_report"],
        "\n".join(
            [
                "# A-Share v1.0.0-prep Release Readiness Report",
                "",
                f"- release_readiness_decision: {decision['release_readiness_decision']}",
                f"- v098_platform_verified: {decision['v098_platform_verified']}",
                f"- blocking_warning_count: {decision['blocking_warning_count']}",
                f"- full_regression_passed: {decision['full_regression_passed']}",
                f"- cli_surface_verified: {decision['cli_surface_verified']}",
                f"- artifact_integrity_passed: {decision['artifact_integrity_passed']}",
                f"- safety_boundary_sweep_passed: {decision['safety_boundary_sweep_passed']}",
                f"- owner_readiness_state: {decision['owner_readiness_state']}",
                f"- owner_operationally_acceptable: {decision['owner_operationally_acceptable']}",
                f"- not_live_trading_ready: {decision['not_live_trading_ready']}",
                "",
                "This closeout is research-only and simulation-only. It is not a live-trading approval, not investment advice, not an order preview, and not a buy/sell signal.",
                "",
            ]
        ),
    )
    _write_text(
        artifacts["regression_report"],
        "\n".join(
            [
                "# A-Share v1.0.0-prep Full Regression Result",
                "",
                f"- command: {full_regression['command']}",
                f"- full_regression_passed: {full_regression['full_regression_passed']}",
                f"- total_passed: {full_regression['total_passed']}",
                f"- total_skipped: {full_regression['total_skipped']}",
                f"- total_failed: {full_regression['total_failed']}",
                f"- duration_seconds: {full_regression['duration_seconds']}",
                "",
            ]
        ),
    )
    _write_text(
        artifacts["boundary_report"],
        "\n".join(
            [
                "# A-Share v1.0.0-prep Safety Boundary Sweep",
                "",
                f"- safety_boundary_sweep_passed: {boundary['safety_boundary_sweep_passed']}",
                f"- owner_readiness_state: {boundary['owner_readiness_state']}",
                f"- source_readiness_score: {boundary['source_readiness_score']}",
                f"- minimum_owner_readiness_score: {boundary['minimum_owner_readiness_score']}",
                f"- score_gap: {boundary['score_gap']}",
                *[f"- {key}: {boundary[key]}" for key in BOUNDARY_FALSE],
                "",
                "Warnings classified:",
                *[f"- {item['warning_id']}: blocking_for_v100={item['blocking_for_v100']}" for item in warnings["classifications"]],
                "",
            ]
        ),
    )


def _load_v09_payloads(paths: ProjectPaths, as_of_date: str) -> dict[str, dict[str, Any]]:
    return {name: read_json(path) for name, path in _v09_json_paths(paths, as_of_date).items()}


def _v09_json_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    base = paths.data_dir / "equity_v09_platform" / "daily" / as_of_date
    return {name: base / f"{name}.json" for name in V09_JSON_NAMES}


def _v09_markdown_paths(paths: ProjectPaths, as_of_date: str) -> list[Path]:
    base = paths.outputs_dir / "equity_v09_platform" / "daily" / as_of_date
    return [base / name for name in V09_MARKDOWN_NAMES]


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v100_prep" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v100_prep" / "daily" / as_of_date
    return {
        "v100_prep_request": data_dir / "v100_prep_request.json",
        "v098_platform_verification": data_dir / "v098_platform_verification.json",
        "v098_warning_classification": data_dir / "v098_warning_classification.json",
        "v100_full_regression_result": data_dir / "v100_full_regression_result.json",
        "v100_cli_surface_verification": data_dir / "v100_cli_surface_verification.json",
        "v100_artifact_integrity_check": data_dir / "v100_artifact_integrity_check.json",
        "v100_safety_boundary_sweep": data_dir / "v100_safety_boundary_sweep.json",
        "v100_release_readiness_decision": data_dir / "v100_release_readiness_decision.json",
        "v100_prep_manifest": data_dir / "v100_prep_manifest.json",
        "readiness_report": output_dir / "A_SHARE_V100_PREP_RELEASE_READINESS_REPORT.md",
        "regression_report": output_dir / "A_SHARE_V100_PREP_FULL_REGRESSION_RESULT.md",
        "boundary_report": output_dir / "A_SHARE_V100_PREP_SAFETY_BOUNDARY_SWEEP.md",
    }


def _ensure_dirs(paths: ProjectPaths, as_of_date: str) -> None:
    for path in _artifact_paths(paths, as_of_date).values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _owner_daily_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    result = _run([sys.executable, "-m", "trading_core.cli", "owner-daily-status", "--as-of-date", as_of_date, "--format", "json"], paths.project_root)
    if result["returncode"] != 0:
        return {}
    try:
        return json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {}


def _run(command: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _count(text: str, label: str) -> int:
    matches = re.findall(rf"(\d+)\s+{re.escape(label)}", text)
    return int(matches[-1]) if matches else 0


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
