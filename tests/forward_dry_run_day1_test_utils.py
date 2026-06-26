from __future__ import annotations

import json
from pathlib import Path

from forward_dry_run_authorization_test_utils import build_authorization_materialization_stack, make_authorization_paths
from trading_core.strategies.common import DEFAULT_BENCHMARKS, DEFAULT_UNIVERSE


DAY1_AS_OF = "2026-06-25"


def make_day1_paths(tmp_path: Path):
    paths = make_authorization_paths(tmp_path)
    write_day1_latest_fixture(paths)
    return paths


def write_day1_latest_fixture(paths) -> None:
    market = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-ETF-OHLCV-CN-HK-V1.csv"
    lines = ["date,symbol,open,high,low,close,adjusted_close,volume,amount,currency,exchange,source,downloaded_at"]
    for index, symbol in enumerate(DEFAULT_UNIVERSE, 1):
        exchange = "HK" if symbol.endswith(".HK") else "SH" if symbol.endswith(".SH") else "SZ"
        price = round(1.2 + index * 0.7, 6)
        lines.append(f"{DAY1_AS_OF},{symbol},{price},{price},{price},{price},{price},{2000 * index},,CNY,{exchange},fixture,2026-06-25T00:00:00Z")
    market.write_text("\n".join(lines) + "\n", encoding="utf-8")

    benchmark = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-BENCHMARK-INDEX-CN-HK-V1.csv"
    benchmark_rows = ["date,benchmark_id,open,high,low,close,adjusted_close,volume,source,downloaded_at"]
    for index, benchmark_id in enumerate([item for item in DEFAULT_BENCHMARKS if item != "EQUAL_ETF"], 1):
        price = round(1000 + index * 10, 6)
        volume = 0 if benchmark_id == "CASH" else 100000 * index
        benchmark_rows.append(f"{DAY1_AS_OF},{benchmark_id},{price},{price},{price},{price},{price},{volume},fixture,2026-06-25T00:00:00Z")
    benchmark.write_text("\n".join(benchmark_rows) + "\n", encoding="utf-8")

    risk = paths.project_root / "data" / "global_briefing" / "normalized" / "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl"
    risk.write_text(
        json.dumps({"as_of_date": DAY1_AS_OF, "signals": {"global_risk_off": 0.21, "risk_off": 0.21}, "source": "fixture", "version": "v1"})
        + "\n",
        encoding="utf-8",
    )


def build_day1_authorized_stack(paths) -> None:
    build_authorization_materialization_stack(paths)


def build_day1_execution_stack(paths) -> None:
    from trading_core.forward_dry_run.day1_input_snapshot import build_day1_input_snapshot
    from trading_core.forward_dry_run.day1_ledger_snapshot import build_day1_ledger_snapshot
    from trading_core.forward_dry_run.day1_operator_report import build_day1_operator_report
    from trading_core.forward_dry_run.day1_post_execution_audit import audit_forward_dry_run_day1
    from trading_core.forward_dry_run.day1_pre_execution_gate import build_day1_pre_execution_gate
    from trading_core.forward_dry_run.day1_risk_and_boundary_report import build_day1_risk_and_boundary_report
    from trading_core.forward_dry_run.day1_strategy_signals import build_day1_strategy_signals
    from trading_core.forward_dry_run.day1_virtual_execution_result import build_day1_virtual_execution_result
    from trading_core.forward_dry_run.day1_virtual_order_preview import build_day1_virtual_order_preview
    from trading_core.forward_dry_run.forward_dry_run_status import build_forward_dry_run_status
    from trading_core.planning.day1_blocker_reclassification_v063 import reclassify_day1_blockers_after_forward_dry_run_day1

    build_day1_authorized_stack(paths)
    build_day1_pre_execution_gate(paths=paths, git_status_clean_override=True)
    build_day1_input_snapshot(paths=paths)
    build_day1_strategy_signals(paths=paths)
    build_day1_virtual_order_preview(paths=paths)
    build_day1_virtual_execution_result(paths=paths)
    build_day1_ledger_snapshot(paths=paths)
    build_day1_risk_and_boundary_report(paths=paths)
    build_day1_operator_report(paths=paths)
    audit_forward_dry_run_day1(paths=paths)
    build_forward_dry_run_status(paths=paths)
    reclassify_day1_blockers_after_forward_dry_run_day1(paths=paths)
