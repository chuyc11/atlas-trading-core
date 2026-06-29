"""Issue catalog generation for owner remediation."""

from __future__ import annotations

import hashlib
from typing import Any

from trading_core.equity_owner_remediation.remediation_mapping import DISALLOWED_ACTIONS, mapping_for_code
from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


def build_issue_catalog(*, as_of_date: str, payloads: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warning_snapshot = payloads.get("warning_trend_snapshot", {})
    dashboard_audit = payloads.get("owner_dashboard_audit", {})
    for code in sorted(set(warning_snapshot.get("current_warning_codes", []) + dashboard_audit.get("warnings", []))):
        issues.append(_issue(as_of_date, code, "owner_dashboard", "warning_trend_snapshot", "warning", False, code in _known_non_blocking_codes()))
    blocking_sources = [
        ("owner_monitoring_audit", payloads.get("owner_monitoring_audit", {})),
        ("owner_dashboard_audit", dashboard_audit),
        ("current_day_run_audit", payloads.get("current_day_run_audit", {})),
        ("data_refresh_audit", payloads.get("data_refresh_audit", {})),
    ]
    for source_name, source in blocking_sources:
        for code in source.get("blocking_reasons", []):
            issues.append(_issue(as_of_date, str(code), source_name, source_name, "critical", True, False))
    for event in payloads.get("alert_event_log", {}).get("events", []):
        status = event.get("status")
        if status not in {"triggered", "insufficient_history"}:
            continue
        issues.append(
            _issue(
                as_of_date,
                str(event.get("rule_id")),
                str(event.get("source_stage")),
                str(event.get("source_artifact")),
                str(event.get("severity") or "informational"),
                bool(event.get("blocking")),
                bool(event.get("known_non_blocking")),
                message=str(event.get("message") or ""),
            )
        )
    run_history = payloads.get("run_history_snapshot", {})
    if run_history.get("insufficient_history_for_trends") is True:
        issues.append(
            _issue(
                as_of_date,
                "insufficient_history_for_trends",
                "run_history",
                "run_history_snapshot",
                "known_non_blocking",
                False,
                True,
                message="run history observation count is below trend threshold",
            )
        )
    deduped = {item["issue_code"]: item for item in issues}
    result = list(deduped.values())
    return {
        "catalog_id": "A-SHARE-OWNER-REMEDIATION-ISSUE-CATALOG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "issue_count": len(result),
        "issues": result,
    }


def _issue(
    as_of_date: str,
    issue_code: str,
    source_stage: str,
    source_artifact: str,
    severity: str,
    blocking: bool,
    known_non_blocking: bool,
    *,
    message: str = "",
) -> dict[str, Any]:
    mapping = mapping_for_code(issue_code, as_of_date=as_of_date)
    if known_non_blocking and mapping["category"] == "unknown_issue":
        category = "known_non_blocking_issue"
        mapped_severity = "known_non_blocking"
    elif issue_code == "insufficient_history_for_trends":
        category = "insufficient_history_issue"
        mapped_severity = "known_non_blocking"
    else:
        category = mapping["category"]
        mapped_severity = severity if severity in {"critical", "warning", "informational", "known_non_blocking"} else mapping["severity"]
    digest = hashlib.sha256(issue_code.encode("utf-8")).hexdigest()[:10]
    return {
        "issue_id": f"A-SHARE-OWNER-ISSUE-{digest}",
        "issue_code": issue_code,
        "source_stage": source_stage,
        "source_artifact": source_artifact,
        "severity": mapped_severity,
        "category": category,
        "blocking": blocking,
        "known_non_blocking": known_non_blocking,
        "detected": True,
        "message": message or mapping["owner_summary_zh"],
        "owner_impact": _owner_impact(category, blocking),
        "remediation_category": mapping["category"],
        "recommended_safe_actions": mapping["safe_diagnostic_steps"],
        "disallowed_actions": list(DISALLOWED_ACTIONS),
        "manual_review_required": blocking or category in {"unknown_issue", "boundary_issue"},
        "explicitly_classified_unknown": mapping["explicitly_classified_unknown"],
    }


def _known_non_blocking_codes() -> set[str]:
    return {
        "daily_basic:required_field_all_null",
        "trading_calendar:exchange_level_calendar_collapsed_to_trade_date",
        "portfolio observation history is below the minimum required window",
        "portfolio relative metrics limited by first-day initialization",
    }


def _owner_impact(category: str, blocking: bool) -> str:
    if blocking:
        return "Blocks release validation until manually reviewed."
    if category == "insufficient_history_issue":
        return "Trend interpretation should wait for more run history."
    return "Requires owner awareness and safe artifact inspection only."
