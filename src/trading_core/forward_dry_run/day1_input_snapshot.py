"""Input snapshot for virtual forward dry-run day 1."""

from __future__ import annotations

from typing import Any

from trading_core.daily_workflow.common import benchmark_rows_for_date, market_rows_for_date, risk_proxy_for_date
from trading_core.forward_dry_run.day1_common import DAY_INDEX, boundary, day_json, day_report, eligible_as_of_date, non_claim_lines, paths_or_default, source_hashes, write_artifact
from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.common import DEFAULT_BENCHMARKS, DEFAULT_UNIVERSE


def build_day1_input_snapshot(*, as_of_date: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    selected, details = eligible_as_of_date(paths, as_of_date)
    market_rows = market_rows_for_date(paths, selected)
    benchmark_rows = benchmark_rows_for_date(paths, selected)
    risk = risk_proxy_for_date(paths, selected)
    payload: dict[str, Any] = {
        "snapshot_id": "FORWARD-DRY-RUN-DAY1-INPUT-SNAPSHOT",
        "day_index": DAY_INDEX,
        "as_of_date": selected,
        "data_source_mode": "local_authorized_historical_data",
        "real_time_market_data_downloaded": False,
        "external_api_called": False,
        "universe_complete": details["universe_complete"],
        "benchmark_complete": details["benchmark_complete"],
        "risk_proxy_complete": details["risk_proxy_complete"],
        "trading_calendar_passed": details["trading_calendar_passed"],
        "missing_symbols": details["missing_symbols"],
        "missing_benchmarks": details["missing_benchmarks"],
        "symbols": {symbol: market_rows.get(symbol) for symbol in DEFAULT_UNIVERSE},
        "benchmarks": {benchmark: benchmark_rows.get(benchmark) for benchmark in DEFAULT_BENCHMARKS if benchmark != "EQUAL_ETF"},
        "risk_proxy": risk,
        "source_hashes": source_hashes(paths),
        "overall_passed": details["eligible"],
        "blocking_reasons": [] if details["eligible"] else ["day1 input data not eligible"],
        "boundary": {
            "input_snapshot_only": True,
            "broker_connected": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(day_json(paths, "day1_input_snapshot.json"), payload, day_report(paths, "DAY1_INPUT_SNAPSHOT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Input Snapshot",
        "",
        f"- as_of_date: {payload['as_of_date']}",
        f"- universe_complete: {str(payload['universe_complete']).lower()}",
        f"- benchmark_complete: {str(payload['benchmark_complete']).lower()}",
        f"- risk_proxy_complete: {str(payload['risk_proxy_complete']).lower()}",
        "- real_time_market_data_downloaded: false",
        "- external_api_called: false",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

