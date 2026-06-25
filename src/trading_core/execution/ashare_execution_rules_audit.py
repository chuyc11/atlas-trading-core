"""Release audit for v0.5.9 A-share execution rules hardening."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, RELEASE_CANDIDATE, paths_or_default, read_dict, rel, standard_boundary
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
    "ml approved for trading",
    "llm approved for trading",
    "rl approved for trading",
]


def audit_ashare_execution_rules(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("ASHARE-EXECUTION-RULES-AUDIT")
    artifacts = _load(paths)
    sections = {
        "gap_plan": _exists(artifacts["gap_plan"], "gap plan missing"),
        "calendar": _passed(bool(artifacts["calendar_contract"]) and artifacts["calendar_audit"].get("overall_passed") is True, "calendar contract/audit missing or failed"),
        "timeline": _passed(artifacts["timeline"].get("same_day_close_signal_execution_rejected") is True, "same-day close signal rejection missing"),
        "tradability": _passed(artifacts["price_status"].get("suspension_missing_limit_handled") is True and artifacts["price_status"].get("st_new_listing_handled") is True, "tradability handling incomplete"),
        "lot_position": _passed(artifacts["lot_position"].get("buy_must_satisfy_board_lot") is True and artifacts["lot_position"].get("t_plus_1_available_after_settlement") is True, "lot/position rules incomplete"),
        "costs": _passed(artifacts["costs"].get("costs_enter_cash_accounting") is True and artifacts["costs"].get("costs_enter_trade_record") is True, "cost rules incomplete"),
        "virtual_execution": _passed(bool(artifacts["virtual_execution"]) and artifacts["virtual_execution"].get("protected_path_guard") is True, "virtual execution contract incomplete"),
        "ledger_invariants": _passed(artifacts["ledger_audit"].get("overall_passed") is True, "isolated ledger invariant audit failed"),
        "replay_smoke": _passed(artifacts["smoke"].get("overall_passed") is True, "execution-aware replay smoke failed"),
        "day1_reclassification": _passed(bool(artifacts["reclassification"]) and artifacts["reclassification"].get("updated_day1_blocker_count") == 0, "day1 blocker reclassification incomplete"),
        "boundary": _audit_boundaries(artifacts),
        "protected_paths": {"passed": True, "issues": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording(paths),
    }
    changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not changes, "issues": changes, "checked_paths": list(PROTECTED_PATHS)}
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    reclass = artifacts["reclassification"]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "baseline_day1_blocker_count": reclass.get("baseline_day1_blocker_count", artifacts["gap_plan"].get("baseline_day1_blocker_count", 0)),
            "updated_day1_blocker_count": reclass.get("updated_day1_blocker_count"),
            "closed_blockers": [item.get("blocker_id") for item in reclass.get("closed_blockers", [])],
            "recommended_next_version": reclass.get("recommended_next_version"),
        },
        "sections": sections,
        "boundary": standard_boundary("execution_rules_hardening_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_execution_rules_audit.json"
    md_path = paths.outputs_dir / "audit" / "ASHARE_EXECUTION_RULES_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_execution_rules_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _load(paths: ProjectPaths) -> dict[str, dict[str, Any]]:
    names = {
        "gap_plan": "ashare_execution_gap_plan.json",
        "calendar_contract": "ashare_trading_calendar_contract.json",
        "calendar_audit": "ashare_trading_calendar_audit.json",
        "timeline": "execution_timeline_contract.json",
        "price_status": "ashare_price_status_contract.json",
        "lot_position": "ashare_lot_position_contract.json",
        "costs": "ashare_execution_cost_contract.json",
        "virtual_execution": "virtual_execution_contract.json",
        "ledger_audit": "isolated_ledger_invariant_audit.json",
        "smoke": "execution_aware_replay_smoke.json",
        "reclassification": "day1_blocker_reclassification_v059.json",
    }
    return {key: read_dict(paths.data_dir / "system" / name) for key, name in names.items()}


def _exists(data: dict[str, Any], issue: str) -> dict[str, Any]:
    return {"passed": bool(data), "issues": [] if data else [issue]}


def _passed(condition: bool, issue: str) -> dict[str, Any]:
    return {"passed": condition, "issues": [] if condition else [issue]}


def _audit_boundaries(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    issues = []
    for name, artifact in artifacts.items():
        boundary = artifact.get("boundary", {})
        for key in ["run_daily_called", "forward_dry_run_started", "main_ledger_written", "labels_used_as_authorization", "ml_shadow_used_as_authorization", "experiments_used_as_authorization", "llm_trading_decision", "rl_used", "promotion_triggered"]:
            if boundary.get(key) is not False:
                issues.append(f"{name} {key} is not false")
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
            if not lowered or any(token in lowered for token in ["not ", "no ", "false", "does not", "is not", "not used"]):
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def build_execution_rules_audit_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Execution Rules Audit", "", "## Overall Verdict", f"- overall_passed={str(payload['overall_passed']).lower()}", f"- blocking_reasons={payload['blocking_reasons']}", HARDENING_NOTICE, "", "## Execution Rule Coverage"]
    lines.extend(f"- {name}: {str(section['passed']).lower()}" for name, section in payload["sections"].items())
    lines.extend(["", "## Day-1 Blocker Reclassification", f"- baseline_day1_blocker_count: {payload['summary']['baseline_day1_blocker_count']}", f"- updated_day1_blocker_count: {payload['summary']['updated_day1_blocker_count']}", "", "## Recommended Next Version", f"- {payload['summary']['recommended_next_version']}", "", "## Boundary", "- execution rules hardening only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", "- not strategy effectiveness proof", "- not live trading readiness", "- no broker connected", "- ML shadow not used as authorization", "- LLM not used for trading decision", "- RL not used", "- promotion not triggered", "", "## Release Recommendation"])
    lines.append(f"Recommended release tag: {RELEASE_CANDIDATE}" if payload["overall_passed"] else "Release tag is not recommended until blockers are resolved.")
    lines.append("")
    return "\n".join(lines)

