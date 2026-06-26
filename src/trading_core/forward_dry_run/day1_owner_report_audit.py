"""Audit the v0.6.3.2 day1 owner report pack."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import write_artifact
from trading_core.forward_dry_run.day1_owner_report_common import (
    RECOMMENDED_NEXT_VERSION,
    REPORT_ARTIFACTS,
    TARGET_VERSION,
    audit_paths,
    load_day1_owner_report_context,
    owner_non_claim_lines,
    paths_or_default,
    project_path,
    report_boundary,
    scope_plan_system_paths,
)
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_POSITIVE_PHRASES = [
    "day2 executed",
    "day3 executed",
    "run-daily executed",
    "real orders placed",
    "broker connected",
    "strategy effectiveness proven",
    "forward dry-run fully validated",
    "live trading ready",
    "production trading ready",
    "ML approved for trading",
    "LLM approved for trading",
    "RL approved for trading",
    "promotion approved",
]


def audit_day1_owner_report_pack(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    scope_json, _scope_md = scope_plan_system_paths(paths)
    report_missing = [relative for relative in REPORT_ARTIFACTS.values() if not project_path(paths, relative).exists()]
    blocking: list[str] = []
    if not scope_json.exists():
        blocking.append("scope_plan_missing")
    blocking.extend(f"missing_report: {relative}" for relative in report_missing)
    if not context["core"]["overall_passed"]:
        blocking.extend(context["core"]["blocking_reasons"])
    if context["day2_executed"]:
        blocking.append("day2_executed=true")
    if context["day3_executed"]:
        blocking.append("day3_executed=true")
    if context["missing_required"]:
        blocking.extend(f"missing_required_input: {relative}" for relative in context["missing_required"])
    blocking.extend(_forbidden_wording_issues(paths))
    summary_report = context["payloads"].get("day1_post_execution_audit", {})
    pack_summary_path = project_path(paths, REPORT_ARTIFACTS["owner_report_pack_summary"])
    pack_summary = {}
    if pack_summary_path.exists():
        from trading_core.execution.common import read_dict

        pack_summary = read_dict(pack_summary_path)
    warnings = []
    if not context["day2_input_readiness_evidence_found"]:
        warnings.append("day2 input readiness evidence not found")
    payload: dict[str, Any] = {
        "audit_id": "FORWARD-DRY-RUN-DAY1-OWNER-REPORT-AUDIT",
        "release_candidate": TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "summary": {
            "owner_report_pack_complete": pack_summary.get("owner_report_pack_complete", False),
            "day1_completed": True,
            "day2_executed": False,
            "recommended_next_version": RECOMMENDED_NEXT_VERSION,
            "day1_post_execution_audit_passed": summary_report.get("overall_passed") is True,
        },
        "boundary": {
            **report_boundary("report_pack_only"),
            "report_pack_only": True,
            "day2_executed": False,
            "day3_executed": False,
            "run_daily_called": False,
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_fully_validated": False,
            "live_trading_ready": False,
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
            "promotion_triggered": False,
        },
    }
    json_path, report_path = audit_paths(paths)
    lines = [
        "# Forward Dry-Run Day1 Owner Report Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(warnings)}",
        f"- owner_report_pack_complete: {str(payload['summary']['owner_report_pack_complete']).lower()}",
        "- day1_completed: true",
        "- day2_executed: false",
        f"- recommended_next_version: {RECOMMENDED_NEXT_VERSION}",
        "",
        "## Boundary",
        *owner_non_claim_lines(),
        "",
    ]
    return write_artifact(json_path, payload, report_path, "\n".join(lines))


def _forbidden_wording_issues(paths: ProjectPaths) -> list[str]:
    issues: list[str] = []
    candidates = list((paths.outputs_dir / "forward_dry_run" / "day_001" / "reports").glob("*.md"))
    for path in candidates:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lower = line.lower()
            for phrase in FORBIDDEN_POSITIVE_PHRASES:
                phrase_lower = phrase.lower()
                if phrase_lower in lower and not _is_negated(lower, phrase_lower):
                    issues.append(f"forbidden positive wording: {path.name}:{number}:{phrase}")
    return issues


def _is_negated(line: str, phrase: str) -> bool:
    idx = line.find(phrase)
    prefix = line[max(0, idx - 40) : idx]
    return any(marker in prefix for marker in ["not ", "no ", "false", "without ", "did not ", "was not ", "is not "]) or any(marker in line for marker in ["=false", ": false"])
