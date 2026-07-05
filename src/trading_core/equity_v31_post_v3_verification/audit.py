"""Audit v3.1.0 post-v3 verification artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v31_post_v3_verification.builder import (
    DEFAULT_AS_OF_DATE,
    JSON_NAMES,
    MARKDOWN_NAMES,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
    VOLATILE_CONTENT_HASH_FIELDS,
    _artifact_paths,
)
from trading_core.equity_v31_post_v3_verification.evidence import canonical_json_sha256, validate_full_regression_evidence
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v31_post_v3_verification(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
    input_dir: Path | None = None,
    release_mode: bool = True,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, as_of_date, output_dir=input_dir)
    payloads = {name: read_json(artifacts[name]) for name in JSON_NAMES}
    result = payloads["v31_post_v3_verification_result"]
    markdowns = [artifacts[f"md:{name}"] for name in MARKDOWN_NAMES]
    blocking: list[str] = []

    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if result.get("target_version") != TARGET_VERSION:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
    for key in _required_true_fields():
        if result.get(key) is not True:
            blocking.append(f"required_true_missing:{key}")
    for key in _required_false_fields():
        if result.get(key) is not False:
            blocking.append(f"required_false_not_false:{key}")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    evidence = payloads.get("v31_full_regression_command_evidence", {})
    blocking.extend(validate_full_regression_evidence(evidence=evidence, paths=paths, release_mode=release_mode))
    summary = evidence.get("summary", {}) if isinstance(evidence, dict) else {}
    if result.get("full_regression_total_passed") != summary.get("passed") or result.get("full_regression_total_skipped") != summary.get("skipped"):
        blocking.append("full_regression_totals_do_not_match_command_evidence")
    if payloads.get("v31_split_matrix_regression_evidence", {}).get("full_regression_total_passed") != summary.get("passed"):
        blocking.append("compat_regression_artifact_does_not_match_command_evidence")
    if result.get("full_regression_mode") != "single_command":
        blocking.append("full_regression_mode_not_single_command")
    if result.get("single_command_pytest_completed") is not True:
        blocking.append("single_command_pytest_not_completed")
    if result.get("owner_readiness_state") != "blocked" or result.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_state_mismatch")
    blocking.extend(_validate_semantic_source_references(payloads.get("v31_semantic_regression_pack_result", {})))
    blocking.extend(_validate_manifest_checksums(payloads.get("v31_post_v3_verification_manifest", {}), paths))

    audit = {
        "audit_id": "A-SHARE-V31-POST-V3-VERIFICATION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {
            "json_count": len(JSON_NAMES),
            "markdown_count": len(MARKDOWN_NAMES),
            "audit_markdown_count": 1,
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
            "json_budget_passed": len(JSON_NAMES) <= 26,
            "markdown_budget_passed": len(MARKDOWN_NAMES) <= 11,
            "audit_markdown_budget_passed": True,
        },
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "owner_readiness_state": result.get("owner_readiness_state"),
        "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
        "live_trading_ready": result.get("live_trading_ready"),
        "full_regression_mode": result.get("full_regression_mode"),
        "full_regression_total_passed": result.get("full_regression_total_passed"),
        "full_regression_total_skipped": result.get("full_regression_total_skipped"),
        "full_regression_command_text": evidence.get("command_text") if isinstance(evidence, dict) else None,
        "full_regression_raw_stdout_sha256": evidence.get("raw_stdout_sha256") if isinstance(evidence, dict) else None,
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path, report_path = _audit_paths(paths, input_dir)
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "v30_baseline_verified",
        "semantic_fix_commit_verified",
        "semantic_regression_pack_generated",
        "split_matrix_regression_evidence_generated",
        "test_evidence_truthfulness_contract_generated",
        "git_diff_evidence_pack_generated",
        "artifact_checksum_provenance_pack_generated",
        "external_reviewer_audit_package_generated",
        "local_environment_limitation_result_generated",
        "owner_post_v3_verification_dashboard_generated",
        "not_live_trading_ready_explanation_generated",
        "t_plus_one_dated_settlement_verified",
        "same_day_sell_rejection_verified",
        "holiday_settlement_delay_verified",
        "period_cumulative_excess_return_verified",
        "formal_calendar_fail_closed_verified",
        "raw_adjusted_price_fallback_blocked_by_default",
        "execution_path_market_constraints_verified",
        "account_apply_trade_bypass_absent",
        "historical_backtester_no_future_price_window_verified",
        "historical_backtester_next_bar_execution_verified",
        "full_regression_run",
        "full_regression_passed",
        "single_command_pytest_completed",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit",
        "fabricated_test_result",
        "fabricated_split_matrix_result",
        "fabricated_audit_evidence",
        "fabricated_checksum",
        "fabricated_git_evidence",
        "fabricated_semantic_fix_evidence",
        "historical_evidence_deleted",
        "audit_evidence_deleted",
        "release_evidence_deleted",
        "required_artifacts_deleted",
        "owner_operationally_acceptable",
        "owner_readiness_gate_rerun",
        "controlled_gate_reevaluation_run",
        "new_gate_score_generated",
        "new_gate_decision_generated",
        "broker_connected",
        "real_account_data_read",
        "real_orders_placed",
        "real_order_preview_generated",
        "buy_sell_signals_generated",
        "old_run_daily_called",
        "day2_executed",
        "live_trading_ready",
    ]


def _validate_semantic_source_references(semantic: dict[str, Any]) -> list[str]:
    blockers = []
    refs = semantic.get("source_evidence_references")
    if not isinstance(refs, dict):
        return ["semantic_source_evidence_references_missing"]
    semantic_keys = [key for key, value in semantic.items() if (key.endswith("_verified") or key.endswith("_invariant")) and value is True]
    for key in semantic_keys:
        if not refs.get(key):
            blockers.append(f"semantic_source_evidence_reference_missing:{key}")
    return blockers


def _validate_manifest_checksums(manifest: dict[str, Any], paths: ProjectPaths) -> list[str]:
    blockers: list[str] = []
    records = manifest.get("artifact_records")
    if not isinstance(records, list) or not records:
        return ["manifest_artifact_records_missing"]
    for record in records:
        artifact_path = _record_path(record, paths)
        if not artifact_path.exists():
            blockers.append(f"manifest_record_missing:{record.get('name')}")
            continue
        if record.get("envelope_sha256") != sha256_file(artifact_path):
            blockers.append(f"manifest_envelope_checksum_mismatch:{record.get('name')}")
        expected_content = record.get("content_sha256")
        if artifact_path.suffix == ".json" and record.get("name") != "v31_post_v3_verification_manifest":
            actual_content = canonical_json_sha256(read_json(artifact_path), exclude_keys=VOLATILE_CONTENT_HASH_FIELDS)
        else:
            actual_content = sha256_file(artifact_path)
        if expected_content != actual_content:
            blockers.append(f"manifest_content_checksum_mismatch:{record.get('name')}")
    return blockers


def _record_path(record: dict[str, Any], paths: ProjectPaths) -> Path:
    raw = Path(str(record.get("path") or ""))
    return raw if raw.is_absolute() else paths.project_root / raw


def _audit_paths(paths: ProjectPaths, input_dir: Path | None) -> tuple[Path, Path]:
    if input_dir is None:
        return (
            paths.data_dir / "equity_data_quality" / "a_share_v31_post_v3_verification_audit.json",
            paths.outputs_dir / "audit" / "A_SHARE_V31_POST_V3_VERIFICATION_AUDIT.md",
        )
    root = Path(input_dir)
    return (
        root / "data" / "equity_data_quality" / "a_share_v31_post_v3_verification_audit.json",
        root / "outputs" / "audit" / "A_SHARE_V31_POST_V3_VERIFICATION_AUDIT.md",
    )


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v3.1 Post-v3 Verification Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- full_regression_mode: {audit['full_regression_mode']}",
        f"- full_regression_total_passed: {audit['full_regression_total_passed']}",
        f"- full_regression_total_skipped: {audit['full_regression_total_skipped']}",
        f"- owner_readiness_state: {audit['owner_readiness_state']}",
        f"- live_trading_ready: {audit['live_trading_ready']}",
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
