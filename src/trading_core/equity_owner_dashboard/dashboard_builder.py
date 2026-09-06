"""Builder for the v0.8.2 A-share owner dashboard."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_dashboard.artifact_navigation import build_artifact_navigation_index
from trading_core.equity_owner_dashboard.attribution_summary_card import build_attribution_summary_card
from trading_core.equity_owner_dashboard.benchmark_summary_card import build_benchmark_summary_card
from trading_core.equity_owner_dashboard.candidate_summary_card import build_candidate_summary_card
from trading_core.equity_owner_dashboard.dashboard_boundary import build_dashboard_boundary_check
from trading_core.equity_owner_dashboard.dashboard_config import (
    AUDIT_EXISTING_DASHBOARD,
    BUILD_DASHBOARD_FROM_EXISTING_RUN,
    DEFAULT_AS_OF_DATE,
    VALIDATE_EXISTING_DASHBOARD_INPUTS,
    OwnerDashboardConfig,
    dashboard_artifact_paths,
    dashboard_output_dir,
    validate_dashboard_config,
)
from trading_core.equity_owner_dashboard.dashboard_manifest import build_dashboard_manifest, build_dashboard_summary
from trading_core.equity_owner_dashboard.dashboard_report import write_dashboard_reports
from trading_core.equity_owner_dashboard.dashboard_source_trace import build_dashboard_source_trace
from trading_core.equity_owner_dashboard.data_freshness_card import build_data_freshness_card
from trading_core.equity_owner_dashboard.input_availability import build_dashboard_input_availability, input_paths, load_json
from trading_core.equity_owner_dashboard.performance_summary_card import build_performance_summary_card
from trading_core.equity_owner_dashboard.portfolio_summary_card import build_portfolio_summary_card
from trading_core.equity_owner_dashboard.research_output_card import build_research_output_card
from trading_core.equity_owner_dashboard.status_cards import build_executive_status_card, build_provider_health_card
from trading_core.equity_owner_dashboard.warning_blocker_card import build_warning_and_blocker_card
from trading_core.equity_owner_dashboard.workflow_status_card import build_workflow_status_card
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def validate_a_share_owner_dashboard_inputs(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_date_mismatch: bool = False,
    fail_on_missing_optional_card: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    return build_a_share_owner_dashboard(
        as_of_date=as_of_date,
        mode=VALIDATE_EXISTING_DASHBOARD_INPUTS,
        allow_date_mismatch=allow_date_mismatch,
        fail_on_missing_optional_card=fail_on_missing_optional_card,
        compact_only=True,
        paths=paths,
    )


def build_a_share_owner_dashboard(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_DASHBOARD_FROM_EXISTING_RUN,
    allow_date_mismatch: bool = False,
    fail_on_missing_optional_card: bool = False,
    compact_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    resolved_as_of_date = _resolved_as_of_date(paths, as_of_date)
    config = OwnerDashboardConfig(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        fail_on_missing_optional_card=fail_on_missing_optional_card,
        compact_only=compact_only,
    )
    issues = validate_dashboard_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    artifacts = dashboard_artifact_paths(paths, as_of_date)
    generated_at = datetime.now(UTC).isoformat()
    availability = build_dashboard_input_availability(paths=paths, as_of_date=resolved_as_of_date)
    write_json(artifacts["dashboard_config"], config.to_dict())
    write_json(artifacts["dashboard_input_availability"], availability)
    if mode == VALIDATE_EXISTING_DASHBOARD_INPUTS:
        return {
            "builder_id": "A-SHARE-OWNER-DASHBOARD-INPUT-VALIDATION",
            "mode": mode,
            "as_of_date": as_of_date,
            "resolved_as_of_date": resolved_as_of_date,
            "overall_passed": availability["overall_passed"],
            "blocking_reasons": availability["blocking_reasons"],
            "warnings": availability["warnings"],
            "dashboard_config_path": str(artifacts["dashboard_config"]),
            "dashboard_input_availability_path": str(artifacts["dashboard_input_availability"]),
        }
    if mode == AUDIT_EXISTING_DASHBOARD:
        raise ValueError("use audit-a-share-owner-dashboard for audit_existing_dashboard mode")

    data_freshness = build_data_freshness_card(paths=paths, as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date)
    provider_health = build_provider_health_card(paths=paths, as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date)
    workflow_status = build_workflow_status_card(paths=paths, as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date)
    research_output = build_research_output_card(paths=paths, as_of_date=resolved_as_of_date)
    candidate_summary = build_candidate_summary_card(paths=paths, as_of_date=resolved_as_of_date)
    portfolio_summary = build_portfolio_summary_card(paths=paths, as_of_date=resolved_as_of_date)
    benchmark_summary = build_benchmark_summary_card(paths=paths, as_of_date=resolved_as_of_date)
    performance_summary = build_performance_summary_card(paths=paths, as_of_date=resolved_as_of_date)
    attribution_summary = build_attribution_summary_card(paths=paths, as_of_date=resolved_as_of_date)
    source_payloads = _source_payloads(paths, resolved_as_of_date)
    warning_blocker = build_warning_and_blocker_card(as_of_date=as_of_date, sources=source_payloads)
    warning_blocker["warnings"] = [row["message"] for row in warning_blocker["items"] if not row["blocking"]]
    warning_blocker["known_non_blocking_warnings"] = [row["message"] for row in warning_blocker["items"] if row["known_non_blocking"]]
    artifact_navigation = build_artifact_navigation_index(paths=paths, as_of_date=resolved_as_of_date)
    executive = build_executive_status_card(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        input_availability=availability,
        data_freshness_card=data_freshness,
        workflow_status_card=workflow_status,
        research_output_card=research_output,
        performance_summary_card=performance_summary,
        attribution_summary_card=attribution_summary,
        warning_and_blocker_card=warning_blocker,
    )
    cards = {
        "executive_status_card": executive,
        "data_freshness_card": data_freshness,
        "provider_health_card": provider_health,
        "workflow_status_card": workflow_status,
        "research_output_card": research_output,
        "candidate_summary_card": candidate_summary,
        "portfolio_summary_card": portfolio_summary,
        "benchmark_summary_card": benchmark_summary,
        "performance_summary_card": performance_summary,
        "attribution_summary_card": attribution_summary,
        "warning_and_blocker_card": warning_blocker,
        "artifact_navigation_index": artifact_navigation,
    }
    for key, value in cards.items():
        write_json(artifacts[key], value)

    output_paths = [artifacts[key] for key in artifacts if key.startswith("owner_") or key.startswith("dashboard_")]
    source_paths = _source_paths(paths, resolved_as_of_date)
    boundary = build_dashboard_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=warning_blocker.get("warnings", []),
        blocking_reasons=warning_blocker.get("blocking_reasons", []),
    )
    source_trace = build_dashboard_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        source_paths=source_paths,
        output_paths=output_paths,
        warnings=warning_blocker.get("warnings", []),
    )
    payload = {**cards, "dashboard_config": config.to_dict(), "dashboard_input_availability": availability}
    manifest = _manifest(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        mode=mode,
        cards=cards,
        warning_blocker=warning_blocker,
        artifacts=artifacts,
        source_paths=source_paths,
        boundary=boundary,
    )
    summary = build_dashboard_summary(as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date, mode=mode, cards=cards, manifest=manifest)
    payload.update({"dashboard_source_trace": source_trace, "dashboard_boundary_check": boundary, "dashboard_manifest": manifest, "dashboard_summary": summary})
    write_json(artifacts["dashboard_source_trace"], source_trace)
    write_json(artifacts["dashboard_boundary_check"], boundary)
    write_json(artifacts["dashboard_manifest"], manifest)
    write_json(artifacts["dashboard_summary"], summary)
    write_dashboard_reports(dashboard_output_dir(paths, as_of_date), payload, compact_only=compact_only)

    boundary = build_dashboard_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=warning_blocker.get("warnings", []),
        blocking_reasons=warning_blocker.get("blocking_reasons", []),
    )
    source_trace = build_dashboard_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        source_paths=source_paths,
        output_paths=output_paths,
        warnings=warning_blocker.get("warnings", []),
    )
    manifest = _manifest(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        mode=mode,
        cards=cards,
        warning_blocker=warning_blocker,
        artifacts=artifacts,
        source_paths=source_paths,
        boundary=boundary,
    )
    summary = build_dashboard_summary(as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date, mode=mode, cards=cards, manifest=manifest)
    payload.update({"dashboard_source_trace": source_trace, "dashboard_boundary_check": boundary, "dashboard_manifest": manifest, "dashboard_summary": summary})
    write_json(artifacts["dashboard_source_trace"], source_trace)
    write_json(artifacts["dashboard_boundary_check"], boundary)
    write_json(artifacts["dashboard_manifest"], manifest)
    write_json(artifacts["dashboard_summary"], summary)
    write_dashboard_reports(dashboard_output_dir(paths, as_of_date), payload, compact_only=compact_only)
    return {
        "builder_id": "A-SHARE-OWNER-DASHBOARD-BUILDER",
        "mode": mode,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "overall_status": executive["overall_status"],
        "overall_passed": boundary["overall_passed"] and availability["overall_passed"] and not warning_blocker["blocking_count"],
        "blocking_reasons": sorted(set(boundary["blocking_reasons"] + availability["blocking_reasons"] + warning_blocker["blocking_reasons"])),
        "warnings": warning_blocker["warnings"],
        "dashboard_manifest_path": str(artifacts["dashboard_manifest"]),
        "dashboard_summary_path": str(artifacts["dashboard_summary"]),
        "dashboard_report_path": str(artifacts["owner_dashboard_report"]),
        "recommended_next_version": manifest["recommended_next_version"],
    }


def _resolved_as_of_date(paths: ProjectPaths, as_of_date: str) -> str:
    current = current_day_artifact_paths(paths, as_of_date)
    for path in [current["current_day_run_manifest"], current["current_day_audit_json"]]:
        payload = load_json(path)
        if payload.get("resolved_as_of_date"):
            return str(payload["resolved_as_of_date"])
    return as_of_date


def _source_payloads(paths: ProjectPaths, as_of_date: str) -> dict[str, dict[str, Any]]:
    payloads = {}
    for group, values in input_paths(paths, as_of_date).items():
        for kind, path in values.items():
            payload = load_json(path)
            if payload:
                payload["_path"] = relative(path, paths.project_root)
                payloads[f"{group}_{kind}"] = payload
    return payloads


def _source_paths(paths: ProjectPaths, as_of_date: str) -> list[Path]:
    result: list[Path] = []
    for values in input_paths(paths, as_of_date).values():
        result.extend(values.values())
    return result


def _manifest(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    generated_at: str,
    mode: str,
    cards: dict[str, dict[str, Any]],
    warning_blocker: dict[str, Any],
    artifacts: dict[str, Path],
    source_paths: list[Path],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    required_cards = {"executive_status_card", "data_freshness_card", "workflow_status_card", "research_output_card", "warning_and_blocker_card", "artifact_navigation_index"}
    optional_cards = set(cards) - required_cards
    return build_dashboard_manifest(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        mode=mode,
        executive_status_card=cards["executive_status_card"],
        required_cards_present=all(key in cards for key in required_cards),
        optional_cards_present=all(key in cards for key in optional_cards),
        warning_and_blocker_card=warning_blocker,
        output_artifacts={key: str(path) for key, path in artifacts.items() if not key.startswith("dashboard_audit")},
        source_artifacts={path.name: str(path) for path in source_paths},
        boundary=boundary,
    )
