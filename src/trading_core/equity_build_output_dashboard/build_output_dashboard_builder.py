"""Builder for v0.8.9 build-output owner dashboard."""

from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_build_output_dashboard.artifact_navigation import build_artifact_navigation, source_paths
from trading_core.equity_build_output_dashboard.build_output_boundary import build_boundary_check
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_DASHBOARD,
    DEFAULT_AS_OF_DATE,
    FILES,
    VALIDATE_INPUTS,
    BuildOutputDashboardConfig,
    artifact_paths,
    data_dir,
    validate_config,
)
from trading_core.equity_build_output_dashboard.build_output_manifest import build_manifest, build_summary
from trading_core.equity_build_output_dashboard.build_output_report import (
    render_compact_dashboard,
    render_dashboard_comparison_report,
    render_navigation_report,
    render_owner_dashboard,
    render_repeatability_card_report,
    render_source_trace_report,
)
from trading_core.equity_build_output_dashboard.build_output_source_trace import build_source_trace
from trading_core.equity_build_output_dashboard.dashboard_comparison import build_dashboard_comparison
from trading_core.equity_build_output_dashboard.date_alignment import build_date_alignment
from trading_core.equity_build_output_dashboard.input_availability import build_input_availability, load_json
from trading_core.equity_build_output_dashboard.protected_path_card import build_protected_path_card
from trading_core.equity_build_output_dashboard.repeatability_card import build_repeatability_card
from trading_core.equity_build_output_dashboard.source_resolution import build_source_resolution
from trading_core.equity_build_output_dashboard.status_cards import (
    build_data_freshness_card,
    build_executive_status_card,
    build_optional_summary_card,
    build_research_output_card,
    build_workflow_status_card,
)
from trading_core.equity_build_output_dashboard.warning_blocker_card import build_warning_and_blocker_card
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_build_output_owner_dashboard_inputs(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "repeatability_audit_passed": availability["repeatability_audit_passed"],
        "gated_build_audit_passed": availability["gated_build_audit_passed"],
        "validate_source_dashboard_audit_passed": availability["validate_source_dashboard_audit_passed"],
        "data_refresh_audit_passed": availability["data_refresh_audit_passed"],
    }


def build_a_share_build_output_owner_dashboard(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_DASHBOARD,
    allow_date_mismatch: bool = False,
    allow_required_validate_fallback: bool = False,
    allow_business_output_drift: bool = False,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    config = BuildOutputDashboardConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        allow_required_validate_fallback=allow_required_validate_fallback,
        allow_business_output_drift=allow_business_output_drift,
    )
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")
    if mode == AUDIT_EXISTING:
        raise ValueError("use audit-a-share-build-output-owner-dashboard for audit_existing mode")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(
        paths=paths,
        as_of_date=as_of_date,
        input_availability=availability,
        allow_required_validate_fallback=allow_required_validate_fallback,
    )
    alignment = build_date_alignment(
        as_of_date=as_of_date,
        input_availability=availability,
        allow_date_mismatch=allow_date_mismatch,
    )
    payloads = {
        "build_output_dashboard_config": config.to_dict(),
        "build_output_input_availability": availability,
        "build_output_source_resolution": resolution,
        "build_output_date_alignment": alignment,
    }
    _write_json(payloads, artifacts)
    if mode == VALIDATE_INPUTS:
        return {
            "builder_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-BUILDER",
            "overall_passed": availability.get("overall_passed", False) and alignment.get("overall_passed", False),
            "blocking_reasons": availability.get("blocking_reasons", []) + alignment.get("blocking_reasons", []),
            "warnings": len(availability.get("warnings", []) + alignment.get("warnings", [])),
            "source_workflow_mode": "build_from_existing_data",
            "recommended_next_version": "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh",
        }

    cards = _build_cards(paths, as_of_date, availability, resolution)
    payloads.update(cards)
    comparison = build_dashboard_comparison(
        paths=paths,
        as_of_date=as_of_date,
        build_cards=cards,
        source_resolution=resolution,
    )
    payloads["validate_dashboard_vs_build_dashboard_comparison"] = comparison
    warning_card = build_warning_and_blocker_card(
        as_of_date=as_of_date,
        cards=cards,
        availability=availability,
        resolution=resolution,
    )
    payloads["build_output_warning_and_blocker_card"] = warning_card
    cards["build_output_warning_and_blocker_card"] = warning_card
    _write_json(payloads, artifacts)

    source_artifacts = _source_artifacts(paths, as_of_date)
    output_artifacts = {key: value for key, value in artifacts.items() if key in FILES}
    source_trace = build_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        source_artifacts=source_artifacts,
        output_artifacts=output_artifacts,
        source_resolution=resolution,
    )
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warning_card=warning_card,
        source_resolution=resolution,
    )
    manifest = build_manifest(
        as_of_date=as_of_date,
        mode=mode,
        cards=cards,
        source_resolution=resolution,
        source_trace=source_trace,
        boundary=boundary,
        output_artifacts=output_artifacts,
        source_artifacts=source_artifacts,
        paths=paths,
    )
    summary = build_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, cards=cards, comparison=comparison)
    payloads.update({
        "build_output_dashboard_source_trace": source_trace,
        "build_output_dashboard_boundary_check": boundary,
        "build_output_dashboard_manifest": manifest,
        "build_output_dashboard_summary": summary,
    })
    _write_json(payloads, artifacts)
    _write_reports(artifacts, as_of_date, cards, comparison, source_trace, summary)
    return {
        "builder_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-BUILDER",
        "overall_passed": summary.get("overall_passed", False),
        "blocking_reasons": summary.get("blocking_reasons", []),
        "warnings": len(summary.get("warnings", [])),
        "source_workflow_mode": "build_from_existing_data",
        "gated_build_audit_passed": summary.get("gated_build_audit_passed", False),
        "repeatability_audit_passed": summary.get("repeatability_audit_passed", False),
        "business_output_drift_count": summary.get("business_output_drift_count", 0),
        "protected_path_modifications_detected": summary.get("protected_path_modifications_detected", True),
        "required_cards_present": summary.get("required_cards_present", False),
        "optional_cards_present": summary.get("optional_cards_present", False),
        "required_validate_fallback_used": summary.get("required_validate_fallback_used", True),
        "optional_validate_fallback_used": summary.get("optional_validate_fallback_used", False),
        "comparison_completed": summary.get("comparison_completed", False),
        "dashboard_report": str(artifacts["build_output_owner_dashboard_report"]),
        "recommended_next_version": summary.get("recommended_next_version"),
    }


def _build_cards(paths: ProjectPaths, as_of_date: str, availability: dict, resolution: dict) -> dict:
    repeatability_audit = load_json(paths.data_dir / "equity_data_quality" / "a_share_build_repeatability_audit.json")
    comparison = load_json(paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "build_vs_build_comparison.json")
    protected = load_json(paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "protected_path_modification_check.json")
    cards = {
        "build_output_data_freshness_card": build_data_freshness_card(paths=paths, as_of_date=as_of_date),
        "build_output_workflow_status_card": build_workflow_status_card(paths=paths, as_of_date=as_of_date),
        "build_output_research_output_card": build_research_output_card(paths=paths, as_of_date=as_of_date),
        "build_output_candidate_summary_card": build_optional_summary_card(
            paths=paths,
            as_of_date=as_of_date,
            card_id="BUILD_OUTPUT_CANDIDATE_SUMMARY",
            source_path=paths.data_dir / "equity_selection" / "daily" / as_of_date / "candidate_generation_summary.json",
        ),
        "build_output_portfolio_summary_card": build_optional_summary_card(
            paths=paths,
            as_of_date=as_of_date,
            card_id="BUILD_OUTPUT_PORTFOLIO_SUMMARY",
            source_path=paths.data_dir / "equity_portfolios" / "daily" / as_of_date / "portfolio_manifest.json",
        ),
        "build_output_benchmark_summary_card": build_optional_summary_card(
            paths=paths,
            as_of_date=as_of_date,
            card_id="BUILD_OUTPUT_BENCHMARK_SUMMARY",
            source_path=paths.data_dir / "equity_benchmarks" / "daily" / as_of_date / "benchmark_summary.json",
        ),
        "build_output_performance_summary_card": build_optional_summary_card(
            paths=paths,
            as_of_date=as_of_date,
            card_id="BUILD_OUTPUT_PERFORMANCE_SUMMARY",
            source_path=paths.data_dir / "equity_performance" / "daily" / as_of_date / "performance_summary.json",
        ),
        "build_output_attribution_summary_card": build_optional_summary_card(
            paths=paths,
            as_of_date=as_of_date,
            card_id="BUILD_OUTPUT_ATTRIBUTION_SUMMARY",
            source_path=paths.data_dir / "equity_attribution" / "daily" / as_of_date / "attribution_summary.json",
        ),
        "build_output_repeatability_card": build_repeatability_card(
            as_of_date=as_of_date,
            repeatability_audit=repeatability_audit,
            comparison=comparison,
        ),
        "build_output_protected_path_card": build_protected_path_card(as_of_date=as_of_date, protected_check=protected),
        "build_output_artifact_navigation": build_artifact_navigation(paths=paths, as_of_date=as_of_date),
    }
    warning = build_warning_and_blocker_card(as_of_date=as_of_date, cards=cards, availability=availability, resolution=resolution)
    cards["build_output_warning_and_blocker_card"] = warning
    cards["build_output_executive_status_card"] = build_executive_status_card(
        as_of_date=as_of_date,
        availability=availability,
        resolution=resolution,
    )
    return cards


def _write_json(payloads: dict, artifacts: dict) -> None:
    for key, payload in payloads.items():
        path = artifacts.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_reports(artifacts: dict, as_of_date: str, cards: dict, comparison: dict, source_trace: dict, summary: dict) -> None:
    reports = {
        "build_output_owner_dashboard_report": render_owner_dashboard(
            as_of_date=as_of_date,
            cards=cards,
            comparison=comparison,
            summary=summary,
        ),
        "build_output_owner_dashboard_compact_report": render_compact_dashboard(as_of_date=as_of_date, summary=summary),
        "build_output_artifact_navigation_report": render_navigation_report(navigation=cards["build_output_artifact_navigation"]),
        "build_output_repeatability_card_report": render_repeatability_card_report(
            repeatability_card=cards["build_output_repeatability_card"]
        ),
        "validate_dashboard_vs_build_dashboard_report": render_dashboard_comparison_report(comparison=comparison),
        "build_output_dashboard_source_trace_report": render_source_trace_report(source_trace=source_trace),
    }
    for key, content in reports.items():
        path = artifacts[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _source_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    result = {
        "repeatability_audit": paths.data_dir / "equity_data_quality" / "a_share_build_repeatability_audit.json",
        "gated_build_audit": paths.data_dir / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json",
        "owner_dashboard_audit": paths.data_dir / "equity_data_quality" / "a_share_owner_dashboard_audit.json",
        "data_refresh_audit": paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json",
        "repeatability_summary": paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "repeatability_summary.json",
        "gated_build_summary": paths.data_dir / "equity_current_day_builds" / "daily" / as_of_date / "gated_build_summary.json",
    }
    for key, path in source_paths(paths, as_of_date).items():
        if key != "build_output_dashboard_report":
            result[key] = path
    return result
