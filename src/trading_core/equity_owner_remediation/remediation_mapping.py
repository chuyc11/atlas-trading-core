"""Known issue-code to safe remediation mapping."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


KNOWN_CODE_CATEGORIES = {
    "daily_basic:required_field_all_null": ("schema_issue", "known_non_blocking"),
    "trading_calendar:exchange_level_calendar_collapsed_to_trade_date": ("schema_issue", "known_non_blocking"),
    "TREND_ANALYSIS_INSUFFICIENT_HISTORY": ("insufficient_history_issue", "informational"),
    "DATA_REFRESH_FAILURE": ("data_refresh_issue", "critical"),
    "CURRENT_DAY_RUN_FAILURE": ("workflow_issue", "critical"),
    "OWNER_DASHBOARD_FAILURE": ("dashboard_issue", "critical"),
    "BOUNDARY_VIOLATION": ("boundary_issue", "critical"),
    "BROKER_OR_ORDER_SURFACE_DETECTED": ("boundary_issue", "critical"),
    "OLD_RUN_DAILY_DETECTED": ("boundary_issue", "critical"),
    "DAY2_EXECUTED_DETECTED": ("boundary_issue", "critical"),
    "FORBIDDEN_WORDING_DETECTED": ("boundary_issue", "critical"),
    "MISSING_REQUIRED_ARTIFACT": ("documentation_issue", "critical"),
    "PROVIDER_HEALTH_DEGRADED": ("provider_issue", "warning"),
    "DATA_FRESHNESS_DEGRADED": ("freshness_issue", "warning"),
    "SCHEMA_VALIDATION_FAILED": ("schema_issue", "critical"),
    "COVERAGE_VALIDATION_FAILED": ("coverage_issue", "critical"),
    "WORKFLOW_AUDIT_FAILED": ("workflow_issue", "critical"),
    "DASHBOARD_AUDIT_FAILED": ("dashboard_issue", "critical"),
    "MONITORING_AUDIT_FAILED": ("monitoring_issue", "critical"),
}

DISALLOWED_ACTIONS = [
    "do not connect broker",
    "do not read real account",
    "do not place orders",
    "do not generate buy or sell signals",
    "do not treat remediation as a trade instruction",
]


def mapping_for_code(issue_code: str, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    category, severity = KNOWN_CODE_CATEGORIES.get(issue_code, ("unknown_issue", "informational"))
    safe_commands = _safe_commands(category, as_of_date)
    return {
        "remediation_id": f"A-SHARE-OWNER-REMEDIATION-{_slug(issue_code)}",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "issue_code": issue_code,
        "category": category,
        "severity": severity,
        "owner_summary_zh": _owner_summary(issue_code, category),
        "safe_diagnostic_steps": _diagnostic_steps(category),
        "safe_rerun_commands": safe_commands,
        "manual_review_steps": _manual_steps(category),
        "escalation_condition": _escalation_condition(category),
        "disallowed_actions": list(DISALLOWED_ACTIONS),
        "expected_artifacts_to_check": _expected_artifacts(category),
        "explicitly_classified_unknown": issue_code not in KNOWN_CODE_CATEGORIES,
    }


def build_warning_remediation_map(issue_codes: list[str], *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    codes = sorted(set(issue_codes) | {"daily_basic:required_field_all_null", "trading_calendar:exchange_level_calendar_collapsed_to_trade_date"})
    return _map_payload("A-SHARE-OWNER-WARNING-REMEDIATION-MAP", "warning_remediation", codes, as_of_date)


def build_blocking_remediation_map(issue_codes: list[str], *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    required = ["DATA_REFRESH_FAILURE", "CURRENT_DAY_RUN_FAILURE", "OWNER_DASHBOARD_FAILURE", "BOUNDARY_VIOLATION", "MISSING_REQUIRED_ARTIFACT"]
    return _map_payload("A-SHARE-OWNER-BLOCKING-REMEDIATION-MAP", "blocking_remediation", sorted(set(issue_codes) | set(required)), as_of_date)


def build_alert_remediation_map(issue_codes: list[str], *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    required = [
        "TREND_ANALYSIS_INSUFFICIENT_HISTORY",
        "PROVIDER_HEALTH_DEGRADED",
        "DATA_FRESHNESS_DEGRADED",
        "BROKER_OR_ORDER_SURFACE_DETECTED",
        "OLD_RUN_DAILY_DETECTED",
        "DAY2_EXECUTED_DETECTED",
        "FORBIDDEN_WORDING_DETECTED",
        "SCHEMA_VALIDATION_FAILED",
        "COVERAGE_VALIDATION_FAILED",
        "WORKFLOW_AUDIT_FAILED",
        "DASHBOARD_AUDIT_FAILED",
        "MONITORING_AUDIT_FAILED",
    ]
    return _map_payload("A-SHARE-OWNER-ALERT-REMEDIATION-MAP", "alert_remediation", sorted(set(issue_codes) | set(required)), as_of_date)


def _map_payload(map_id: str, map_type: str, issue_codes: list[str], as_of_date: str) -> dict[str, Any]:
    return {
        "map_id": map_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "map_type": map_type,
        "items": [mapping_for_code(code, as_of_date=as_of_date) for code in issue_codes],
    }


def _safe_commands(category: str, as_of_date: str) -> list[str]:
    commands = {
        "data_refresh_issue": [f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
        "provider_issue": [f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
        "freshness_issue": [f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
        "schema_issue": [f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
        "coverage_issue": [f"python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
        "workflow_issue": [
            f"python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date {as_of_date} --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts"
        ],
        "dashboard_issue": [f"python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date {as_of_date} --mode build_dashboard_from_existing_run"],
        "monitoring_issue": [f"python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date {as_of_date} --mode build_monitoring_dashboard"],
    }
    return commands.get(category, [])


def _diagnostic_steps(category: str) -> list[str]:
    common = ["Open the source artifact listed in the issue catalog.", "Confirm the related upstream audit status before any rerun plan is considered."]
    category_steps = {
        "provider_issue": ["Review provider health and fallback reports.", "Check whether the provider issue is transient or repeated."],
        "freshness_issue": ["Review dataset freshness validation.", "Confirm whether the requested date is covered by existing local data."],
        "schema_issue": ["Review schema validation details.", "Check whether known nullable fields are documented."],
        "coverage_issue": ["Review coverage summary and gap report.", "Identify the affected dataset and symbol scope."],
        "workflow_issue": ["Review current-day run audit and workflow manifest.", "Confirm all expected research artifacts are present."],
        "dashboard_issue": ["Review owner dashboard audit and dashboard boundary check.", "Confirm required cards are present."],
        "monitoring_issue": ["Review owner monitoring audit and alert event log.", "Confirm monitoring boundary remains clean."],
        "boundary_issue": ["Stop release validation and inspect boundary check details.", "Escalate before running any further workflow."],
        "insufficient_history_issue": ["Confirm run history observation count.", "Wait for more daily observations before interpreting trend direction."],
    }
    return common + category_steps.get(category, ["Classify the issue manually and document why it is safe or unsafe to proceed."])


def _manual_steps(category: str) -> list[str]:
    if category == "insufficient_history_issue":
        return ["Document that trend analysis is intentionally unavailable until the minimum observation count is reached."]
    return ["Owner reviews the referenced artifacts.", "Developer review is required if a boundary, missing artifact, or failed audit is present."]


def _escalation_condition(category: str) -> str:
    if category in {"boundary_issue", "data_refresh_issue", "workflow_issue", "dashboard_issue", "monitoring_issue"}:
        return "Escalate immediately if the audit is failing or boundary check is not clean."
    if category == "unknown_issue":
        return "Escalate if the issue repeats or cannot be mapped to a documented remediation category."
    return "Escalate if the issue persists after safe validation artifacts are regenerated by a human."


def _expected_artifacts(category: str) -> list[str]:
    return {
        "provider_issue": ["provider_health_check.json", "provider_fallback_report.json"],
        "freshness_issue": ["dataset_freshness_validation.json", "data_gap_report.json"],
        "schema_issue": ["dataset_schema_validation.json", "data_gap_report.json"],
        "coverage_issue": ["dataset_coverage_summary.json", "data_gap_report.json"],
        "workflow_issue": ["current_day_run_manifest.json", "a_share_current_day_research_run_audit.json"],
        "dashboard_issue": ["dashboard_summary.json", "a_share_owner_dashboard_audit.json"],
        "monitoring_issue": ["monitoring_summary.json", "a_share_owner_monitoring_audit.json"],
        "boundary_issue": ["monitoring_boundary_check.json", "dashboard_boundary_check.json", "current_day_boundary_check.json"],
        "insufficient_history_issue": ["run_history_snapshot.json", "warning_trend_snapshot.json"],
    }.get(category, ["issue_catalog.json"])


def _owner_summary(issue_code: str, category: str) -> str:
    if category == "insufficient_history_issue":
        return "运行历史样本不足，趋势判断应等待更多观察。"
    if category == "known_non_blocking_issue":
        return "这是已知非阻塞事项，需记录但不自动操作。"
    if category == "unknown_issue":
        return f"{issue_code} 尚未纳入固定映射，需人工分类。"
    return f"{issue_code} 需要按 {category} 的安全排查步骤处理。"


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.upper()).strip("-")
