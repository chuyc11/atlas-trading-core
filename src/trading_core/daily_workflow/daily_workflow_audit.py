"""Release audit for v0.6.1 daily workflow binding."""

from __future__ import annotations

from typing import Any

from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import protected_diff

from .common import DEFAULT_AS_OF_DATE, NEXT_VERSION, NOTICE, RELEASE_CANDIDATE, STRATEGY_IDS, boundary_markdown, daily_order_preview_path, daily_report_packet_path, daily_signals_path, data_quality_path, execution_preview_path, freeze_path, paths_or_default, read_json_file, snapshot_path, workflow_boundary, write_artifact


FORBIDDEN_POSITIVE_PHRASES = [
    "strategy effectiveness proven",
    "forward dry-run validated",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
    "ml approved for trading",
    "llm approved for trading",
    "rl approved for trading",
    "production daily trading ready",
]


def audit_daily_workflow(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    artifacts = _load(paths, as_of_date)
    sections = {
        "scope_plan": _exists(artifacts["scope_plan"], "scope plan missing"),
        "snapshot": _exists(artifacts["snapshot"], "daily market data snapshot missing"),
        "data_quality": _data_quality_section(artifacts["data_quality"]),
        "freeze_manifest": _exists(artifacts["freeze"], "daily input freeze manifest missing"),
        "daily signals": _signals_section(artifacts["signals"]),
        "order_preview": _order_preview_section(artifacts["order_preview"]),
        "execution_preview": _execution_preview_section(artifacts["execution_preview"]),
        "daily_report": _exists(artifacts["daily_report"], "daily report packet missing"),
        "protected_path_residue": _residue_section(artifacts["residue_scan"]),
        "boundary": _boundary_section(artifacts),
        "wording": _wording_section(paths),
        "protected_paths": {"passed": True, "issues": []},
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": protected_changes}
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    signals = artifacts["signals"].get("signals", []) if isinstance(artifacts["signals"], dict) else []
    payload: dict[str, Any] = {
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": artifacts["data_quality"].get("warnings", []) if isinstance(artifacts["data_quality"], dict) else [],
        "summary": {
            "as_of_date": as_of_date,
            "strategies_total": len(STRATEGY_IDS),
            "strategies_with_daily_signals": len({signal.get("strategy_id") for signal in signals}),
            "order_preview_exists": bool(artifacts["order_preview"]),
            "daily_report_exists": bool(artifacts["daily_report"]),
            "protected_path_blocker_count": artifacts["residue_scan"].get("blocker_count", 0) if isinstance(artifacts["residue_scan"], dict) else 0,
            "recommended_next_version": NEXT_VERSION,
        },
        "sections": sections,
        "boundary": {
            **workflow_boundary("daily_workflow_binding_only"),
            "historical_daily_workflow_fixture_passed": not blocking,
        },
    }
    json_path = paths.data_dir / "system" / "daily_workflow_audit.json"
    md_path = paths.outputs_dir / "audit" / "DAILY_WORKFLOW_AUDIT.md"
    return write_artifact(json_path, payload, md_path, build_markdown(payload))


def _load(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    return {
        "scope_plan": read_json_file(paths.data_dir / "system" / "daily_workflow_scope_plan.json"),
        "snapshot": read_json_file(snapshot_path(paths, as_of_date)),
        "data_quality": read_json_file(data_quality_path(paths, as_of_date)),
        "freeze": read_json_file(freeze_path(paths, as_of_date)),
        "signals": read_json_file(daily_signals_path(paths, as_of_date)),
        "order_preview": read_json_file(daily_order_preview_path(paths, as_of_date)),
        "execution_preview": read_json_file(execution_preview_path(paths, as_of_date)),
        "daily_report": read_json_file(daily_report_packet_path(paths, as_of_date)),
        "residue_scan": read_json_file(paths.data_dir / "system" / "protected_path_residue_scan.json"),
    }


def _exists(data: Any, issue: str) -> dict[str, Any]:
    return {"passed": bool(data), "issues": [] if data else [issue]}


def _data_quality_section(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"passed": False, "issues": ["data quality audit missing"]}
    return {"passed": data.get("overall_passed") is True, "issues": [] if data.get("overall_passed") is True else data.get("blocking_reasons", ["data quality audit failed"])}


def _signals_section(data: dict[str, Any]) -> dict[str, Any]:
    issues = []
    signals = data.get("signals", []) if data else []
    present = {signal.get("strategy_id") for signal in signals}
    for strategy_id in STRATEGY_IDS:
        if strategy_id not in present:
            issues.append(f"{strategy_id} daily signal missing")
    if not all(signal.get("pit_constraints_passed") is True for signal in signals):
        issues.append("daily signal PIT constraints failed")
    return {"passed": bool(signals) and not issues, "issues": issues or ([] if signals else ["daily signals missing"])}


def _order_preview_section(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"passed": False, "issues": ["daily order preview missing"]}
    issues = []
    if data.get("preview_only") is not True:
        issues.append("preview_only is not true")
    if data.get("executed") is not False:
        issues.append("executed is not false")
    return {"passed": not issues, "issues": issues}


def _execution_preview_section(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"passed": False, "issues": ["daily isolated execution preview missing"]}
    checks = {
        "execution_mode": data.get("execution_mode") == "isolated_preview",
        "preview_only": data.get("preview_only") is True,
        "executed": data.get("executed") is False,
        "state_updated": data.get("state_updated") is False,
        "ledger_invariants": data.get("ledger_invariants", {}).get("passed") is True,
    }
    issues = [name for name, passed in checks.items() if not passed]
    return {"passed": not issues, "issues": issues}


def _residue_section(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"passed": False, "issues": ["protected path residue scan missing"]}
    count = int(data.get("blocker_count", 0) or 0)
    return {"passed": count == 0, "issues": [] if count == 0 else [f"protected path blocker count={count}"]}


def _boundary_section(artifacts: dict[str, Any]) -> dict[str, Any]:
    issues = []
    forbidden = [
        "run_daily_called",
        "forward_dry_run_started",
        "forward_dry_run_validated",
        "main_ledger_written",
        "labels_used_as_authorization",
        "ml_shadow_used_as_authorization",
        "experiments_used_as_authorization",
        "llm_trading_decision",
        "rl_used",
        "promotion_triggered",
        "strategy_effectiveness_proven",
        "live_trading_ready",
        "broker_connected",
        "production_daily_trading_ready",
        "ml_trading_approved",
        "llm_trading_approved",
        "rl_trading_approved",
    ]
    for name, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            continue
        boundary = artifact.get("boundary", {})
        for key in forbidden:
            if artifact.get(key) is True or boundary.get(key) is True:
                issues.append(f"{name} {key} is true")
    return {"passed": not issues, "issues": issues}


def _wording_section(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    for root in [paths.outputs_dir / "daily_workflow", paths.outputs_dir / "audit", paths.project_root / "docs"]:
        if not root.exists():
            continue
        for file in root.rglob("*.md"):
            for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                lowered = line.lower()
                if not lowered or any(token in lowered for token in ["not ", "no ", "false", "does not", "is not", "not used"]):
                    continue
                for phrase in FORBIDDEN_POSITIVE_PHRASES:
                    if phrase in lowered:
                        issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Daily Workflow Audit",
        "",
        NOTICE,
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        f"- warnings={len(payload['warnings'])}",
        "",
        "## Summary",
        f"- as_of_date: {payload['summary']['as_of_date']}",
        f"- strategies_with_daily_signals: {payload['summary']['strategies_with_daily_signals']}",
        f"- protected_path_blocker_count: {payload['summary']['protected_path_blocker_count']}",
        f"- recommended_next_version: {payload['summary']['recommended_next_version']}",
        "",
        "## Boundary",
    ]
    lines.extend(boundary_markdown("daily workflow binding only"))
    lines.extend(["", "## Release Recommendation"])
    lines.append(f"Recommended release tag: {RELEASE_CANDIDATE}" if payload["overall_passed"] else "Release tag is not recommended until blockers are resolved.")
    lines.append("")
    return "\n".join(lines)
