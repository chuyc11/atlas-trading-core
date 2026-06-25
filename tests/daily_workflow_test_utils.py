from __future__ import annotations

import json
from pathlib import Path

from baseline_strategy_test_utils import build_baseline_strategy_stack
from execution_test_utils import build_execution_stack, make_execution_paths
from trading_core.strategies.common import DEFAULT_UNIVERSE


AS_OF = "2024-12-31"


def make_daily_workflow_paths(tmp_path: Path):
    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    write_authorized_daily_fixture(paths)
    build_baseline_strategy_stack(paths)
    return paths


def write_authorized_daily_fixture(paths) -> None:
    market = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-ETF-OHLCV-CN-HK-V1.csv"
    market.parent.mkdir(parents=True, exist_ok=True)
    lines = ["date,symbol,open,high,low,close,adjusted_close,volume,amount,currency,exchange,source,downloaded_at"]
    for index, symbol in enumerate(DEFAULT_UNIVERSE, 1):
        exchange = "HK" if symbol.endswith(".HK") else "SH" if symbol.endswith(".SH") else "SZ"
        price = round(1.0 + index * 0.5, 6)
        lines.append(f"{AS_OF},{symbol},{price},{price},{price},{price},{price},{1000 * index},,CNY,{exchange},fixture,2026-06-25T00:00:00Z")
    market.write_text("\n".join(lines) + "\n", encoding="utf-8")
    benchmark = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-BENCHMARK-INDEX-CN-HK-V1.csv"
    benchmark.write_text(
        "\n".join(
            [
                "date,benchmark_id,open,high,low,close,adjusted_close,volume,source,downloaded_at",
                f"{AS_OF},CSI300,1,1,1,1,1,1000,fixture,2026-06-25T00:00:00Z",
                f"{AS_OF},CASH,1,1,1,1,1,0,fixture,2026-06-25T00:00:00Z",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    risk = paths.project_root / "data" / "global_briefing" / "normalized" / "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl"
    risk.parent.mkdir(parents=True, exist_ok=True)
    risk.write_text(
        json.dumps({"as_of_date": AS_OF, "signals": {"global_risk_off": 0.35, "risk_off": 0.35}, "source": "fixture", "version": "v1"})
        + "\n",
        encoding="utf-8",
    )


def build_daily_workflow_stack(paths, as_of_date: str = AS_OF) -> None:
    from trading_core.daily_workflow.daily_baseline_signal_binding import build_daily_baseline_signals
    from trading_core.daily_workflow.daily_data_quality_audit import audit_daily_data_quality
    from trading_core.daily_workflow.daily_input_freeze_manifest import build_daily_input_freeze_manifest
    from trading_core.daily_workflow.daily_isolated_execution_preview import build_daily_isolated_execution_preview
    from trading_core.daily_workflow.daily_market_data_snapshot import build_daily_market_data_snapshot
    from trading_core.daily_workflow.daily_order_preview_binding import build_daily_order_preview
    from trading_core.daily_workflow.daily_report_packet import build_daily_report_packet
    from trading_core.daily_workflow.daily_workflow_audit import audit_daily_workflow
    from trading_core.daily_workflow.daily_workflow_scope_plan import build_daily_workflow_scope_plan
    from trading_core.daily_workflow.protected_path_residue_scanner import scan_protected_path_residue
    from trading_core.planning.day1_blocker_reclassification_v061 import reclassify_day1_blockers_after_daily_workflow

    build_daily_workflow_scope_plan(paths=paths)
    build_daily_market_data_snapshot(as_of_date=as_of_date, paths=paths)
    audit_daily_data_quality(snapshot=f"data/daily_workflow/snapshots/daily_market_data_snapshot-{as_of_date}.json", paths=paths)
    build_daily_input_freeze_manifest(as_of_date=as_of_date, paths=paths)
    build_daily_baseline_signals(as_of_date=as_of_date, strategy="all", paths=paths)
    build_daily_order_preview(as_of_date=as_of_date, strategy="all", execution_mode="isolated", paths=paths)
    build_daily_isolated_execution_preview(as_of_date=as_of_date, execution_mode="isolated", paths=paths)
    build_daily_report_packet(as_of_date=as_of_date, paths=paths)
    scan_protected_path_residue(paths=paths)
    audit_daily_workflow(as_of_date=as_of_date, paths=paths)
    reclassify_day1_blockers_after_daily_workflow(paths=paths)

