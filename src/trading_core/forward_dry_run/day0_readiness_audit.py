"""Release audit for v0.5.8 day-0 operational readiness."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import RELEASE_CANDIDATE, TRADING_AUTHORIZATION_NOTICE, paths_or_default, read_dict, rel, standard_boundary
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import protected_diff, timestamp_id, write_json_markdown


FORBIDDEN_PHRASES = [
    "forward dry-run started",
    "forward dry-run validated",
    "strategy effectiveness proven",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
    "manual confirmation complete",
]


def audit_day0_readiness(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("DAY0-READINESS-AUDIT")
    artifacts = _load_artifacts(paths)
    sections = {
        "data_freeze": _audit_data_freeze(artifacts["data_freeze"]),
        "warning_register": _audit_warning_register(artifacts["warning_register"]),
        "blocking_conditions": _audit_blocking_conditions(artifacts["blocking_conditions"]),
        "preflight": _audit_preflight(artifacts["preflight"]),
        "manual_confirmation": _audit_manual_confirmation(artifacts["manual_confirmation"]),
        "operating_calendar": _audit_calendar(artifacts["operating_calendar"]),
        "readiness_report": _audit_report(artifacts["readiness_report"]),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording(paths),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": ["protected path changed", *protected_changes] if protected_changes else [], "modified_paths": [rel(item, paths) for item in protected_changes], "checked_paths": list(PROTECTED_PATHS)}
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    manual = artifacts["manual_confirmation"]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "day0_status": {
            "ready_for_manual_confirmation": not blocking,
            "manual_confirmation_complete": manual.get("manual_confirmation_complete", False),
            "forward_dry_run_started": False,
            "run_daily_called": False,
        },
        "boundary": standard_boundary("day0_readiness_only"),
    }
    json_path = paths.data_dir / "system" / "day0_readiness_audit.json"
    md_path = paths.outputs_dir / "audit" / "DAY0_READINESS_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_day0_readiness_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _load_artifacts(paths: ProjectPaths) -> dict[str, dict[str, Any]]:
    names = {
        "data_freeze": "day0_data_freeze_manifest.json",
        "warning_register": "day0_accepted_warning_register.json",
        "blocking_conditions": "day0_blocking_conditions.json",
        "preflight": "day0_run_daily_preflight.json",
        "manual_confirmation": "day0_manual_confirmation_packet.json",
        "operating_calendar": "forward_dry_run_operating_calendar.json",
        "readiness_report": "day0_readiness_report.json",
    }
    return {key: read_dict(paths.data_dir / "system" / name) for key, name in names.items()}


def _audit_data_freeze(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not data:
        issues.append("data freeze missing")
    packages = data.get("packages", {})
    for package_id in [
        "HIST-ETF-OHLCV-CN-HK-V1",
        "HIST-BENCHMARK-INDEX-CN-HK-V1",
        "HIST-FX-USDCNY-V1",
        "HIST-GLOBAL-RISK-VIX-V1",
        "HIST-RATES-LIQUIDITY-V1",
        "HIST-COMMODITY-INFLATION-RISK-V1",
        "HIST-POLICY-UNCERTAINTY-EPU-V1",
        "HIST-OECD-CLI-MACRO-CYCLE-V1",
    ]:
        if package_id not in packages:
            issues.append(f"{package_id} not frozen")
    if "missing us_epu/europe_epu" not in packages.get("HIST-POLICY-UNCERTAINTY-EPU-V1", {}).get("accepted_limitations", []):
        issues.append("EPU partial limitation missing")
    if "not official OECD CLI" not in packages.get("HIST-OECD-CLI-MACRO-CYCLE-V1", {}).get("accepted_limitations", []):
        issues.append("OECD proxy limitation missing")
    auth = packages.get("HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1", {})
    if auth.get("status") != "not_configured" or auth.get("production_internal_global_briefing_validated") is not False:
        issues.append("internal global-briefing package misrepresented")
    if data.get("proxy_package", {}).get("exists") is not True:
        issues.append("proxy package not frozen")
    return {"passed": not issues, "issues": issues}


def _audit_warning_register(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not data:
        issues.append("warning register missing")
    if data.get("blocking_count") != 0:
        issues.append("warning register blocking_count is non-zero")
    return {"passed": not issues, "issues": issues}


def _audit_blocking_conditions(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not data:
        issues.append("blocking conditions missing")
    if data.get("current_blocking_count") != 0:
        issues.append("current_blocking_count is non-zero")
    if data.get("manual_confirmation_still_required") is not True:
        issues.append("manual confirmation requirement missing")
    return {"passed": not issues, "issues": issues}


def _audit_preflight(data: dict[str, Any]) -> dict[str, Any]:
    preview = data.get("run_daily_command_preview", {})
    issues = []
    if not data:
        issues.append("preflight missing")
    if data.get("overall_passed") is not True:
        issues.append("preflight not passed")
    if preview.get("preview_only") is not True:
        issues.append("preflight preview_only is not true")
    if preview.get("executed") is not False:
        issues.append("preflight executed is not false")
    return {"passed": not issues, "issues": issues}


def _audit_manual_confirmation(data: dict[str, Any]) -> dict[str, Any]:
    confirmations = data.get("confirmations", {})
    issues = []
    if not data:
        issues.append("manual confirmation packet missing")
    if any(value is not False for value in confirmations.values()):
        issues.append("manual confirmation field is not default false")
    if data.get("manual_confirmation_complete") is not False:
        issues.append("manual confirmation complete is not false")
    if data.get("forward_dry_run_start_authorized") is not False:
        issues.append("forward dry-run start authorized is not false")
    if data.get("boundary", {}).get("auto_confirmation") is not False:
        issues.append("auto confirmation is not false")
    return {"passed": not issues, "issues": issues}


def _audit_calendar(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not data:
        issues.append("operating calendar missing")
    if data.get("calendar_status") not in {"template_only", "scheduled_template"}:
        issues.append("calendar status invalid")
    if data.get("forward_dry_run_started") is not False:
        issues.append("calendar claims forward dry-run started")
    return {"passed": not issues, "issues": issues}


def _audit_report(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not data:
        issues.append("readiness report missing")
    if data.get("forward_dry_run_started") is not False:
        issues.append("readiness report claims forward dry-run started")
    if data.get("can_start_forward_dry_run_without_manual_confirmation") is not False:
        issues.append("readiness report allows start without manual confirmation")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: ProjectPaths) -> dict[str, Any]:
    files = []
    for root in [paths.outputs_dir / "system", paths.outputs_dir / "audit", paths.project_root / "docs"]:
        if root.exists():
            files.extend(root.glob("*.md"))
    issues = []
    for file in files:
        for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            lowered = line.lower()
            if not lowered or any(token in lowered for token in ["not ", "no ", "false", "does not", "is not", "preview only"]):
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def build_day0_readiness_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-0 Readiness Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## Section Results",
    ]
    lines.extend(f"- {name}: passed={str(section['passed']).lower()} issues={section.get('issues', [])}" for name, section in payload["sections"].items())
    lines.extend(
        [
            "",
            "## Day-0 Status",
            "- ready for manual confirmation",
            f"- manual confirmation complete: {str(payload['day0_status']['manual_confirmation_complete']).lower()}",
            f"- forward dry-run started: {str(payload['day0_status']['forward_dry_run_started']).lower()}",
            f"- run-daily called: {str(payload['day0_status']['run_daily_called']).lower()}",
            "",
            "## Boundary",
            "- day-0 readiness only",
            "- this does not start forward dry-run",
            "- this does not validate forward dry-run",
            "- this does not prove strategy effectiveness",
            "- this is not live trading readiness",
            "- main ledger not written",
            "- run-daily not called",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "",
            "## Release Recommendation",
        ]
    )
    lines.extend([f"Recommended release tag: {RELEASE_CANDIDATE}" if payload["overall_passed"] else "Release tag is not recommended until blockers are resolved.", ""])
    return "\n".join(lines)
