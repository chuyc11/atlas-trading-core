"""Accepted warning register for day-0 readiness."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import TRADING_AUTHORIZATION_NOTICE, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


KNOWN_CATEGORIES = {"source_download_failed", "missing_signal_component", "coverage_gap", "missing_optional_package", "missing_price", "lot_size_constraint"}


def build_day0_warning_register(*, warning_inventory_path: str | None = None, gap_closure_report_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    register_id, created_at = timestamp_id("DAY0-WARNING-REGISTER")
    inventory_path = resolve_path(warning_inventory_path, paths.data_dir / "system" / "historical_warning_inventory.json", paths)
    report_path = resolve_path(gap_closure_report_path, paths.data_dir / "system" / "historical_data_gap_closure_report.json", paths)
    inventory = read_dict(inventory_path)
    report = read_dict(report_path)
    warnings = [_classify_group(group, report) for group in inventory.get("top_groups", [])]
    accepted = [item for item in warnings if item["status"] == "accepted"]
    unresolved = [item for item in warnings if item["status"] == "unresolved"]
    blocking = [item for item in warnings if item["status"] == "blocking"]
    payload: dict[str, Any] = {
        "register_id": register_id,
        "created_at": created_at,
        "warning_inventory": rel(inventory_path, paths),
        "gap_closure_report": rel(report_path, paths),
        "raw_warning_count": inventory.get("raw_warning_count", 0),
        "grouped_warning_count": inventory.get("grouped_warning_count", len(warnings)),
        "accepted_count": len(accepted),
        "unresolved_count": len(unresolved),
        "blocking_count": len(blocking),
        "warnings": warnings,
        "boundary": standard_boundary("warning_register_only"),
    }
    json_path = paths.data_dir / "system" / "day0_accepted_warning_register.json"
    md_path = paths.outputs_dir / "system" / "DAY0_ACCEPTED_WARNING_REGISTER.md"
    write_json_markdown(json_path, payload, md_path, build_warning_register_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _classify_group(group: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    category = str(group.get("category") or "unknown")
    status = "unresolved"
    rationale = "warning category requires manual review"
    if category == "source_download_failed":
        status = "accepted"
        rationale = "optional source failed but replacement/proxy source is active or documented"
    elif category == "missing_signal_component":
        affected = str(group.get("affected_package") or "")
        if "EPU" in affected:
            epu = report.get("epu", {})
            status = "accepted" if epu.get("current_status") == "partial_downloaded" else "blocking"
            rationale = "EPU partial accepted because Global/China proxy components are available"
        elif "OECD" in affected:
            oecd = report.get("oecd", {})
            status = "accepted" if oecd.get("source") == "authorized_macro_cycle_proxy" else "blocking"
            rationale = "OECD macro-cycle proxy accepted only when clearly marked as proxy"
        else:
            status = "accepted"
            rationale = "non-critical missing signal component accepted for day-0 proxy readiness"
    elif category == "coverage_gap":
        coverage = report.get("proxy_coverage_ratio", {}).get("current")
        if coverage is not None and coverage < 0.80:
            status = "blocking"
            rationale = f"proxy coverage below 0.80: {coverage}"
        elif coverage is not None and coverage < 0.90:
            status = "unresolved"
            rationale = f"proxy coverage requires manual review: {coverage}"
        else:
            status = "accepted"
            rationale = f"proxy coverage accepted: {coverage}"
    elif category == "missing_optional_package":
        status = "accepted"
        rationale = "internal global-briefing package not_configured accepted in proxy mode; internal signal not validated"
    elif category == "missing_price":
        status = "accepted"
        rationale = "remaining missing prices are accepted historical replay limitations, not forward validation evidence"
    elif category == "lot_size_constraint":
        status = "accepted"
        rationale = "isolated replay execution model limitation from lot size and target weight"
    elif category not in KNOWN_CATEGORIES:
        status = "blocking" if category in {"future_leakage", "missing_critical_package"} else "unresolved"
    return {
        "category": category,
        "severity": group.get("severity"),
        "raw_count": group.get("raw_count", 0),
        "message_pattern": group.get("message_pattern"),
        "affected_package": group.get("affected_package"),
        "status": status,
        "rationale": rationale,
        "day0_blocking": status == "blocking",
    }


def build_warning_register_markdown(payload: dict[str, Any]) -> str:
    accepted = [f"- {item['category']}: raw_count={item['raw_count']} rationale={item['rationale']}" for item in payload["warnings"] if item["status"] == "accepted"] or ["- none"]
    unresolved = [f"- {item['category']}: {item['rationale']}" for item in payload["warnings"] if item["status"] == "unresolved"] or ["- none"]
    blocking = [f"- {item['category']}: {item['rationale']}" for item in payload["warnings"] if item["status"] == "blocking"] or ["- none"]
    return "\n".join(
        [
            "# Day-0 Accepted Warning Register",
            "",
            "## Scope",
            "This register classifies known warnings before any future forward dry-run.",
            "It does not start forward dry-run.",
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Accepted Warnings",
            *accepted,
            "",
            "## Unresolved Warnings",
            *unresolved,
            "",
            "## Blocking Warnings",
            *blocking,
            "",
            "## Boundary",
            "- warning register only",
            "- not forward dry-run",
            "- run-daily not called",
            "- main ledger not written",
            "",
        ]
    )
