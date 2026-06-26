"""Audit the virtual forward dry-run day 1 execution package."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import DAY_INDEX, NEXT_VERSION, RELEASE_CANDIDATE, audit_report, boundary, day_json, non_claim_lines, paths_or_default, read_json_file, write_artifact
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_POSITIVE_PHRASES = [
    "real trading started",
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
NEGATION_MARKERS = ["not ", "does not ", "no ", "without ", "false", "not_", "not-"]


def audit_forward_dry_run_day1(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    artifacts = {
        "pre_execution_gate": day_json(paths, "day1_pre_execution_gate.json"),
        "input_snapshot": day_json(paths, "day1_input_snapshot.json"),
        "strategy_signals": day_json(paths, "day1_strategy_signals.json"),
        "order_preview": day_json(paths, "day1_virtual_order_preview.json"),
        "execution_result": day_json(paths, "day1_virtual_execution_result.json"),
        "ledger_snapshot": day_json(paths, "day1_forward_dry_run_ledger_snapshot.json"),
        "risk_report": day_json(paths, "day1_risk_and_boundary_report.json"),
        "operator_report": day_json(paths, "day1_operator_report.json"),
    }
    payloads = {name: read_json_file(path) for name, path in artifacts.items()}
    blocking: list[str] = []
    for name, path in artifacts.items():
        if not path.exists() or not payloads[name]:
            blocking.append(f"missing {name}")
    gate = payloads["pre_execution_gate"]
    signals = payloads["strategy_signals"]
    preview = payloads["order_preview"]
    execution = payloads["execution_result"]
    ledger = payloads["ledger_snapshot"]
    risk = payloads["risk_report"]
    _block_if(blocking, gate.get("overall_passed") is not True, "pre-execution gate not passed")
    _block_if(blocking, signals.get("strategies_generated") != 3, "all three baseline strategies not included")
    _block_if(blocking, preview.get("preview_only") is not True, "order preview preview_only not true")
    _block_if(blocking, preview.get("real_order") is True, "real_order=true")
    _block_if(blocking, preview.get("broker_order") is True, "broker_order=true")
    _block_if(blocking, execution.get("execution_mode") != "forward_dry_run_virtual", "execution_mode not forward_dry_run_virtual")
    _block_if(blocking, execution.get("virtual_execution") is not True, "virtual_execution not true")
    _block_if(blocking, execution.get("real_execution") is True, "real_execution=true")
    _block_if(blocking, execution.get("broker_execution") is True, "broker_execution=true")
    writes = execution.get("ledger_writes", {})
    _block_if(blocking, writes.get("forward_dry_run_ledger_written") is not True, "forward dry-run isolated ledger not written")
    for key in ["main_orders_written", "main_trades_written", "main_portfolio_written", "main_accounts_written"]:
        _block_if(blocking, writes.get(key) is True, f"{key}=true")
    _block_if(blocking, ledger.get("forward_dry_run_started") is not True, "forward_dry_run_started not true")
    _block_if(blocking, ledger.get("forward_dry_run_days_completed") != 1, "forward_dry_run_days_completed not 1")
    _block_if(blocking, ledger.get("next_day_index") != 2, "next_day_index not 2")
    boundary_summary = risk.get("boundary_summary", {})
    for key in ["ml_shadow_used_as_authorization", "llm_trading_decision", "rl_used", "promotion_triggered", "strategy_effectiveness_proven", "live_trading_ready"]:
        _block_if(blocking, boundary_summary.get(key) is True, f"{key}=true")
    blocking.extend(_forbidden_wording_issues(paths))
    payload: dict[str, Any] = {
        "audit_id": "FORWARD-DRY-RUN-DAY1-POST-EXECUTION-AUDIT",
        "release_candidate": RELEASE_CANDIDATE,
        "day_index": DAY_INDEX,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "forward_dry_run_started": True,
            "forward_dry_run_days_completed": 1,
            "next_day_index": 2,
            "virtual_execution_completed": execution.get("executed") is True,
            "main_ledger_written": False,
            "recommended_next_version": NEXT_VERSION,
        },
        "boundary": {
            "virtual_forward_dry_run_only": True,
            "real_trading": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "main_ledger_written": False,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_fully_validated": False,
            "live_trading_ready": False,
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
            "promotion_triggered": False,
        },
    }
    return write_artifact(day_json(paths, "day1_post_execution_audit.json"), payload, audit_report(paths, "FORWARD_DRY_RUN_DAY1_POST_EXECUTION_AUDIT.md"), build_markdown(payload))


def _block_if(blocking: list[str], condition: bool, reason: str) -> None:
    if condition:
        blocking.append(reason)


def _forbidden_wording_issues(paths: ProjectPaths) -> list[str]:
    issues: list[str] = []
    candidates = [
        day_report for day_report in (paths.outputs_dir / "forward_dry_run" / "day_001").glob("*.md")
        if day_report.exists()
    ]
    for path in candidates:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lower = line.lower()
            for phrase in FORBIDDEN_POSITIVE_PHRASES:
                if phrase.lower() in lower and not _is_negated(lower, phrase.lower()):
                    issues.append(f"forbidden positive wording: {path.name}:{number}:{phrase}")
    return issues


def _is_negated(line: str, phrase: str) -> bool:
    idx = line.find(phrase)
    prefix = line[max(0, idx - 24) : idx]
    return any(marker in prefix for marker in NEGATION_MARKERS) or any(marker in line for marker in ["=false", ": false"])


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Post-Execution Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        "- forward_dry_run_started: true",
        "- forward_dry_run_days_completed: 1",
        "- next_day_index: 2",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)


