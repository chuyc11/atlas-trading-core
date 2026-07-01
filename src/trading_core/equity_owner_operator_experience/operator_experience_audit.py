"""Audit for v0.9.1 owner/operator experience."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_operator_experience.io import load_json, write_json, write_text
from trading_core.equity_owner_operator_experience.operator_config import (
    BOUNDARY,
    DEFAULT_AS_OF_DATE,
    FILES,
    FORBIDDEN_POSITIVE_WORDING,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    SOURCE_RELEASE_CANDIDATE,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_operator_experience.report import render_audit
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_operator_experience(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in FILES}
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("operator_input_availability", {})
    status = payloads.get("owner_daily_status_card", {})
    banner = payloads.get("known_blocked_state_banner", {})
    explanation = payloads.get("known_blocked_state_explanation", {})
    menu = payloads.get("operator_action_menu", {})
    boundary = payloads.get("operator_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("operator_experience_config", {}).get("mode", "build_owner_daily_status"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "v090_rc_audit_passed": availability.get("checks", {}).get("v090_rc_audit_passed") is True,
            "v090_full_pytest_passed": availability.get("v090_full_pytest_passed") is True,
            "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
        },
        "operator_experience_checks": {
            "owner_daily_status_generated": status.get("status_card_id") == "A-SHARE-OWNER-DAILY-STATUS-CARD",
            "known_blocked_state_banner_generated": banner.get("banner_id") == "A-SHARE-KNOWN-BLOCKED-STATE-BANNER",
            "known_blocked_state_explanation_generated": explanation.get("explanation_id") == "A-SHARE-KNOWN-BLOCKED-STATE-EXPLANATION",
            "operator_action_menu_generated": menu.get("menu_id") == "A-SHARE-OPERATOR-ACTION-MENU",
            "artifact_navigation_index_generated": payloads.get("artifact_navigation_index", {}).get("index_id") == "A-SHARE-ARTIFACT-NAVIGATION-INDEX",
            "known_owner_readiness_state": availability.get("known_owner_readiness_state"),
            "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
            "blocked_state_misrepresented_as_acceptable": availability.get("blocked_state_misrepresented_as_acceptable"),
            "live_trading_ready_claimed": status.get("live_trading_ready") is True,
            "forbidden_operator_actions_present": menu.get("forbidden_operator_actions_present") is True,
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "test_policy": {
            "full_pytest_run": False,
            "targeted_pytest_required": True,
            "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        },
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    write_json(artifacts["operator_experience_audit_json"], audit)
    write_text(artifacts["operator_experience_audit_report"], render_audit(audit))
    _append_audit_artifacts_to_trace(paths=paths, artifacts=artifacts)
    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "input_checks": audit["input_checks"],
        "operator_experience_checks": audit["operator_experience_checks"],
        "boundary": audit["boundary"],
        "test_policy": audit["test_policy"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifacts["operator_experience_audit_json"]),
        "report_path": str(artifacts["operator_experience_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("operator_input_availability", {})
    config = payloads.get("operator_experience_config", {})
    status = payloads.get("owner_daily_status_card", {})
    banner = payloads.get("known_blocked_state_banner", {})
    explanation = payloads.get("known_blocked_state_explanation", {})
    capability = payloads.get("operator_capability_matrix", {})
    menu = payloads.get("operator_action_menu", {})
    navigation = payloads.get("artifact_navigation_index", {})
    summary = payloads.get("operator_summary", {})
    trace = payloads.get("operator_source_trace", {})
    boundary = payloads.get("operator_boundary_check", {})
    manifest = payloads.get("operator_manifest", {})
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "config_preserves_boundaries": _config_preserves_boundaries(config),
        "input_availability_passed": availability.get("overall_passed") is True,
        "source_resolution_passed": payloads.get("operator_source_resolution", {}).get("overall_passed") is True,
        "date_alignment_passed": payloads.get("operator_date_alignment", {}).get("overall_passed") is True,
        "owner_daily_status_generated": status.get("status_card_id") == "A-SHARE-OWNER-DAILY-STATUS-CARD",
        "known_blocked_state_banner_generated": banner.get("banner_id") == "A-SHARE-KNOWN-BLOCKED-STATE-BANNER",
        "known_blocked_state_explanation_generated": explanation.get("explanation_id") == "A-SHARE-KNOWN-BLOCKED-STATE-EXPLANATION",
        "capability_matrix_generated": capability.get("matrix_id") == "A-SHARE-OPERATOR-CAPABILITY-MATRIX",
        "operator_action_menu_generated": menu.get("menu_id") == "A-SHARE-OPERATOR-ACTION-MENU",
        "artifact_navigation_index_generated": navigation.get("index_id") == "A-SHARE-ARTIFACT-NAVIGATION-INDEX",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-OPERATOR-EXPERIENCE-SUMMARY",
        "input_v090_rc_audit_passed": availability.get("checks", {}).get("v090_rc_audit_passed") is True,
        "v090_full_pytest_passed": availability.get("v090_full_pytest_passed") is True,
        "known_owner_readiness_state_blocked": availability.get("known_owner_readiness_state") == "blocked",
        "owner_operationally_acceptable_false": availability.get("owner_operationally_acceptable") is False,
        "blocked_state_not_misrepresented": availability.get("blocked_state_misrepresented_as_acceptable") is False,
        "operator_status_does_not_claim_live_ready": status.get("live_trading_ready") is False,
        "operator_action_menu_safe": menu.get("forbidden_operator_actions_present") is False,
        "capability_matrix_forbids_forbidden": capability.get("forbidden_capabilities_disallowed") is True,
        "new_gate_score_not_generated": boundary.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": boundary.get("new_gate_decision_generated") is False,
        "owner_readiness_gate_not_rerun": boundary.get("rerun_owner_readiness_gate") is False,
        "build_from_existing_data_not_rerun": boundary.get("rerun_build_from_existing_data") is False,
        "daily_pack_not_rerun": boundary.get("rerun_daily_pack") is False,
        "full_pytest_not_rerun": boundary.get("run_full_pytest") is False,
        "threshold_not_lowered": boundary.get("threshold_lowered") is False,
        "auto_waiver_false": boundary.get("auto_waiver_allowed") is False,
        "manual_waiver_approval_false": boundary.get("manual_waiver_approval_recorded") is False,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True,
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and _markdown_wording_clean(paths, as_of_date),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-OPERATOR-EXPERIENCE-MANIFEST",
    }


def _config_preserves_boundaries(config: dict[str, Any]) -> bool:
    false_fields = [
        "rerun_owner_readiness_gate",
        "rerun_build_from_existing_data",
        "rerun_daily_pack",
        "generate_new_gate_score",
        "generate_new_gate_decision",
        "run_full_pytest",
        "execute_remediation_actions",
        "send_external_notifications",
        "allow_public_network_refresh",
        "allow_full_research_run",
        "allow_broker",
        "allow_real_orders",
        "allow_order_preview",
        "allow_buy_sell_signals",
        "allow_old_run_daily",
        "execute_official_forward_dry_run_day2",
    ]
    return all(config.get(key) is False for key in false_fields) and config.get("does_not_lower_threshold") is True and config.get("does_not_auto_waive") is True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for section in ("source_artifacts", "output_artifacts"):
        for row in trace.get(section, []):
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if row.get("required") is True and not path.exists():
                return False
            if row.get("artifact_key") == "operator_source_trace":
                continue
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _markdown_wording_clean(paths: ProjectPaths, as_of_date: str) -> bool:
    root = paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date
    if not root.exists():
        return True
    for path in root.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(phrase in text for phrase in FORBIDDEN_POSITIVE_WORDING):
            return False
    return True


def _append_audit_artifacts_to_trace(*, paths: ProjectPaths, artifacts: dict[str, Path]) -> None:
    trace_path = artifacts.get("operator_source_trace")
    if not trace_path or not trace_path.exists():
        return
    trace = load_json(trace_path)
    rows = trace.get("output_artifacts", [])
    existing = {row.get("artifact_key") for row in rows}
    for key in ["operator_experience_audit_json", "operator_experience_audit_report"]:
        path = artifacts[key]
        if key in existing:
            continue
        rows.append(
            {
                "artifact_key": key,
                "path": str(path),
                "relative_path": str(path.relative_to(paths.project_root)) if path.is_relative_to(paths.project_root) else str(path),
                "required": True,
                "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() and path.is_file() else "",
            }
        )
    trace["output_artifacts"] = rows
    trace["source_trace_complete"] = all(not row.get("required") or row.get("exists") for row in trace.get("source_artifacts", []) + rows)
    trace["missing_required_artifacts"] = [row.get("artifact_key") for row in trace.get("source_artifacts", []) + rows if row.get("required") and not row.get("exists")]
    write_json(trace_path, trace)
