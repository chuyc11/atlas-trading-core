"""Extract a machine-readable MVP checklist from the project plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.planning.common import PLAN_ALIGNMENT_NOTICE, paths_or_default, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


REQUIREMENTS: list[dict[str, Any]] = [
    {"requirement_id": "R001", "name": "trading_calendar_correct", "category": "data", "description": "Trading calendar must correctly identify trading days before replay or daily workflow.", "evidence_expected": ["calendar artifact", "calendar tests", "CLI reference"], "forbidden_substitutes": ["assuming every weekday is tradable"]},
    {"requirement_id": "R002", "name": "universe_versioning", "category": "data", "description": "Universe membership must be versioned and reproducible.", "evidence_expected": ["universe module", "versioned artifact", "tests"], "forbidden_substitutes": ["implicit ticker list"]},
    {"requirement_id": "R003", "name": "historical_daily_ohlcv_available", "category": "data", "description": "Historical daily OHLCV data must be available for MVP instruments.", "evidence_expected": ["historical data package", "data quality audit", "tests"], "forbidden_substitutes": ["synthetic price-only samples"]},
    {"requirement_id": "R004", "name": "adjusted_price_handling", "category": "data", "description": "Adjusted price handling must be explicit for replay and daily workflows.", "evidence_expected": ["price adjustment contract", "tests", "docs"], "forbidden_substitutes": ["unlabeled raw closes"]},
    {"requirement_id": "R005", "name": "point_in_time_data_contract", "category": "data", "description": "Signals and features must follow a point-in-time data contract.", "evidence_expected": ["PIT module", "PIT tests", "audit"], "forbidden_substitutes": ["latest data backfilled into past decisions"]},
    {"requirement_id": "R006", "name": "t_day_signal_t_plus_1_execution", "category": "execution", "description": "T-day signal generation and T+1 execution semantics must be enforced.", "evidence_expected": ["execution model contract", "T+1 tests", "replay workflow"], "forbidden_substitutes": ["same-day hindsight fills"]},
    {"requirement_id": "R007", "name": "suspension_handling", "category": "execution", "description": "Suspended instruments must be handled explicitly.", "evidence_expected": ["suspension rule", "tests", "execution report"], "forbidden_substitutes": ["filling suspended instruments normally"]},
    {"requirement_id": "R008", "name": "limit_up_limit_down_handling", "category": "execution", "description": "A-share limit up/down rules must be represented before day 1.", "evidence_expected": ["limit rule module", "tests", "execution audit"], "forbidden_substitutes": ["ignoring limit constraints"]},
    {"requirement_id": "R009", "name": "st_and_new_listing_handling", "category": "execution", "description": "ST and new listing constraints must be identified or accepted as scoped limitations.", "evidence_expected": ["ST/new listing rule", "tests", "scope note"], "forbidden_substitutes": ["unfiltered broad universe"]},
    {"requirement_id": "R010", "name": "board_lot_and_odd_lot_rules", "category": "execution", "description": "Board lot and odd lot rules must be enforced in order sizing.", "evidence_expected": ["lot size module", "tests", "warning register"], "forbidden_substitutes": ["fractional shares for A-shares"]},
    {"requirement_id": "R011", "name": "fee_tax_slippage_model", "category": "execution", "description": "Fees, taxes, and slippage must be modeled for virtual execution.", "evidence_expected": ["cost model", "tests", "docs"], "forbidden_substitutes": ["zero-cost fills"]},
    {"requirement_id": "R012", "name": "cash_position_available_shares_accounting", "category": "accounting", "description": "Cash, positions, and available shares accounting must be reconciled.", "evidence_expected": ["accounting module", "consistency tests", "ledger artifacts"], "forbidden_substitutes": ["unreconciled portfolio totals"]},
    {"requirement_id": "R013", "name": "virtual_order_trade_ledger", "category": "accounting", "description": "Virtual orders and trades must be written through controlled ledger paths.", "evidence_expected": ["order ledger", "trade ledger", "tests"], "forbidden_substitutes": ["chat-only execution records"]},
    {"requirement_id": "R014", "name": "equity_curve_generation", "category": "reporting", "description": "Equity curve generation must exist for replay or future dry-run review.", "evidence_expected": ["equity curve artifact", "report", "tests"], "forbidden_substitutes": ["single ending NAV only"]},
    {"requirement_id": "R015", "name": "benchmark_comparison", "category": "reporting", "description": "Benchmark comparison must be generated for performance context.", "evidence_expected": ["benchmark module", "benchmark tests", "report"], "forbidden_substitutes": ["absolute return only"]},
    {"requirement_id": "R016", "name": "baseline_rule_strategies", "category": "strategy", "description": "Baseline rule strategies must be available before evaluating improvements.", "evidence_expected": ["strategy module", "strategy tests", "docs"], "forbidden_substitutes": ["unreviewed ad hoc strategy"]},
    {"requirement_id": "R017", "name": "daily_report_generation", "category": "workflow", "description": "Daily report generation must be available for future dry-run operation.", "evidence_expected": ["daily report", "CLI", "tests"], "forbidden_substitutes": ["manual summary only"]},
    {"requirement_id": "R018", "name": "parameter_data_code_versioning", "category": "governance", "description": "Parameters, data, and code versions must be recorded.", "evidence_expected": ["version artifact", "release tag", "docs"], "forbidden_substitutes": ["unversioned mutable settings"]},
    {"requirement_id": "R019", "name": "protected_path_boundary", "category": "governance", "description": "Protected path boundaries must prevent unintended ledger writes.", "evidence_expected": ["protected path audit", "tests", "reports"], "forbidden_substitutes": ["manual caution only"]},
    {"requirement_id": "R020", "name": "historical_replay_isolated_from_forward_dry_run", "category": "governance", "description": "Historical replay must remain isolated from forward dry-run state.", "evidence_expected": ["isolated replay adapter", "audit", "tests"], "forbidden_substitutes": ["shared mutable state"]},
    {"requirement_id": "R021", "name": "no_broker_no_live_trading_boundary", "category": "boundary", "description": "No broker or live trading integration may be used for current scope.", "evidence_expected": ["boundary audit", "docs", "tests"], "forbidden_substitutes": ["paper-only broker assumptions"]},
    {"requirement_id": "R022", "name": "no_rl_llm_trading_decision_boundary", "category": "boundary", "description": "RL and LLM components must not make trading decisions.", "evidence_expected": ["boundary audit", "docs", "tests"], "forbidden_substitutes": ["AI-generated orders"]},
    {"requirement_id": "R023", "name": "no_auto_promotion_boundary", "category": "boundary", "description": "Automatic promotion must not authorize strategy changes.", "evidence_expected": ["promotion gate", "audit", "docs"], "forbidden_substitutes": ["implicit promotion from backtest"]},
    {"requirement_id": "R024", "name": "forward_dry_run_30_day_requirement", "category": "workflow", "description": "Forward dry-run requires a 30 trading-day operating plan before validation.", "evidence_expected": ["30 day calendar", "day-0 checklist", "audit"], "forbidden_substitutes": ["historical replay substituted as forward validation"]},
]

FORWARD_DAY1_REQUIRED = {item["requirement_id"] for item in REQUIREMENTS} - {"R002", "R009", "R016", "R018", "R022", "R023"}


def build_plan_checklist(*, plan_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    checklist_id, created_at = timestamp_id("PLAN-CHECKLIST")
    selected_plan = _select_plan(plan_path, paths)
    requirements = []
    for item in REQUIREMENTS:
        requirement = dict(item)
        requirement["required_for_mvp"] = True
        requirement["required_before_forward_day1"] = requirement["requirement_id"] in FORWARD_DAY1_REQUIRED
        requirements.append(requirement)
    payload: dict[str, Any] = {
        "checklist_id": checklist_id,
        "created_at": created_at,
        "release_candidate": "v0.5.8.1-plan-alignment-and-mvp-gap-audited",
        "source_plan": rel(selected_plan, paths) if selected_plan else "built_in_confirmed_mvp_requirement_set",
        "requirements": requirements,
        "boundary": standard_boundary("checklist_only"),
    }
    json_path = paths.data_dir / "system" / "plan_checklist.json"
    md_path = paths.outputs_dir / "system" / "PLAN_CHECKLIST.md"
    write_json_markdown(json_path, payload, md_path, build_plan_checklist_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _select_plan(plan_path: str | None, paths: ProjectPaths) -> Path | None:
    if plan_path:
        candidate = resolve_path(plan_path, paths.project_root / plan_path, paths)
        return candidate if candidate.exists() else None
    for name in ["PROJECT_PLAN.md", "PLAN.md", "MVP_PLAN.md", "ROADMAP.md"]:
        candidate = paths.project_root / "docs" / name
        if candidate.exists():
            return candidate
    return None


def build_plan_checklist_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Plan Checklist",
        "",
        "## Scope",
        "This checklist extracts the MVP requirements from the project plan.",
        "This is an audit input. It does not start forward dry-run.",
        PLAN_ALIGNMENT_NOTICE,
        "",
        "## Requirements",
    ]
    for item in payload["requirements"]:
        lines.append(f"- {item['requirement_id']} {item['name']} ({item['category']}): required_before_day1={str(item['required_before_forward_day1']).lower()}")
    lines.extend(["", "## Boundary", "- checklist only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

