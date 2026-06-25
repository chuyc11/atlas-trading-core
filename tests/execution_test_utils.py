from __future__ import annotations

from planning_test_utils import build_planning_stack, make_planning_paths


def make_execution_paths(tmp_path):
    paths = make_planning_paths(tmp_path)
    build_planning_stack(paths)
    return paths


def build_execution_stack(paths) -> None:
    from trading_core.execution.ashare_execution_gap_plan import build_ashare_execution_gap_plan
    from trading_core.execution.ashare_execution_rules_audit import audit_ashare_execution_rules
    from trading_core.execution.ashare_lot_position_contract import build_lot_position_contract
    from trading_core.execution.execution_aware_replay_smoke import run_execution_aware_replay_smoke
    from trading_core.execution.execution_cost_contract import build_execution_cost_contract
    from trading_core.execution.execution_timeline_contract import build_execution_timeline_contract
    from trading_core.execution.isolated_ledger_invariant_audit import audit_isolated_ledger_invariants
    from trading_core.execution.price_status_contract import build_price_status_contract
    from trading_core.execution.trading_calendar_audit import audit_trading_calendar
    from trading_core.execution.trading_calendar_contract import build_trading_calendar_contract
    from trading_core.execution.virtual_execution_contract import build_virtual_execution_contract
    from trading_core.planning.day1_blocker_reclassification import reclassify_day1_blockers_after_execution_hardening

    build_ashare_execution_gap_plan(paths=paths)
    build_trading_calendar_contract(paths=paths)
    audit_trading_calendar(paths=paths)
    build_execution_timeline_contract(paths=paths)
    build_price_status_contract(paths=paths)
    build_lot_position_contract(paths=paths)
    build_execution_cost_contract(paths=paths)
    build_virtual_execution_contract(paths=paths)
    audit_isolated_ledger_invariants(paths=paths)
    run_execution_aware_replay_smoke(paths=paths)
    reclassify_day1_blockers_after_execution_hardening(paths=paths)
    audit_ashare_execution_rules(paths=paths)

