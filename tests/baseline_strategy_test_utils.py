from __future__ import annotations

from pathlib import Path

from execution_test_utils import build_execution_stack, make_execution_paths


TEST_START = "2024-01-02"
TEST_END = "2024-01-12"


def make_baseline_paths(tmp_path: Path):
    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    return paths


def build_baseline_strategy_stack(paths, *, start_date: str = TEST_START, end_date: str = TEST_END) -> None:
    from trading_core.planning.day1_blocker_reclassification_v060 import reclassify_day1_blockers_after_baseline_strategies
    from trading_core.strategies.baseline_benchmark_comparison import compare_baseline_strategy_benchmarks
    from trading_core.strategies.baseline_order_preview import build_baseline_order_preview
    from trading_core.strategies.baseline_signal_engine import generate_baseline_strategy_signals
    from trading_core.strategies.baseline_strategy_contract import build_baseline_strategy_contract
    from trading_core.strategies.baseline_strategy_pack_audit import audit_baseline_strategy_pack
    from trading_core.strategies.baseline_strategy_pack_summary import build_baseline_strategy_pack_summary
    from trading_core.strategies.baseline_strategy_registry import build_baseline_strategy_registry
    from trading_core.strategies.baseline_strategy_report import build_baseline_strategy_report
    from trading_core.strategies.baseline_strategy_replay import replay_baseline_strategy
    from trading_core.strategies.baseline_strategy_scope_plan import build_baseline_strategy_scope_plan

    build_baseline_strategy_scope_plan(paths=paths)
    build_baseline_strategy_contract(paths=paths)
    build_baseline_strategy_registry(paths=paths)
    generate_baseline_strategy_signals(strategy="all", start_date=start_date, end_date=end_date, paths=paths)
    build_baseline_order_preview(strategy="all", execution_mode="isolated", paths=paths)
    replay_baseline_strategy(strategy="all", start_date=start_date, end_date=end_date, execution_mode="isolated", paths=paths)
    compare_baseline_strategy_benchmarks(strategy="all", start_date=start_date, end_date=end_date, paths=paths)
    build_baseline_strategy_report(strategy="all", start_date=start_date, end_date=end_date, paths=paths)
    build_baseline_strategy_pack_summary(start_date=start_date, end_date=end_date, paths=paths)
    audit_baseline_strategy_pack(start_date=start_date, end_date=end_date, paths=paths)
    reclassify_day1_blockers_after_baseline_strategies(paths=paths)

