"""Daily market data snapshot from local authorized historical packages."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id
from trading_core.strategies.common import DEFAULT_BENCHMARKS, DEFAULT_UNIVERSE

from .common import BENCHMARK_DATA_SOURCE, DEFAULT_AS_OF_DATE, MARKET_DATA_SOURCE, NOTICE, RISK_PROXY_SOURCE, benchmark_rows_for_date, boundary_markdown, latest_available_market_date, market_rows_for_date, paths_or_default, price_for_symbol, risk_proxy_for_date, source_record, volume_for_symbol, workflow_boundary, write_artifact


def build_daily_market_data_snapshot(*, as_of_date: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    latest = latest_available_market_date(paths)
    as_of = as_of_date or latest or DEFAULT_AS_OF_DATE
    snapshot_id, created_at = timestamp_id("DAILY-MARKET-DATA-SNAPSHOT")
    market_rows = market_rows_for_date(paths, as_of)
    benchmark_rows = benchmark_rows_for_date(paths, as_of)
    risk_row = risk_proxy_for_date(paths, as_of)
    symbol_records = {}
    for symbol in DEFAULT_UNIVERSE:
        row = market_rows.get(symbol)
        symbol_records[symbol] = {
            "available": row is not None,
            "close_available": price_for_symbol(market_rows, symbol) is not None,
            "volume_available": volume_for_symbol(market_rows, symbol) is not None,
            "stale": row is None,
            "source_date": row.get("date") if row else None,
        }
    benchmark_records = {
        benchmark: {
            "available": benchmark in benchmark_rows or benchmark == "EQUAL_ETF",
            "source_date": benchmark_rows.get(benchmark, {}).get("date"),
            "missing_reason": None if benchmark in benchmark_rows or benchmark == "EQUAL_ETF" else "not_available_for_pinned_as_of_date",
        }
        for benchmark in DEFAULT_BENCHMARKS
    }
    payload: dict[str, Any] = {
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "as_of_date": as_of,
        "latest_available_trading_date": latest,
        "market_data_source": MARKET_DATA_SOURCE.as_posix(),
        "benchmark_data_source": BENCHMARK_DATA_SOURCE.as_posix(),
        "risk_proxy_source": RISK_PROXY_SOURCE.as_posix(),
        "source_records": {
            "market_data": source_record(paths, MARKET_DATA_SOURCE),
            "benchmark_data": source_record(paths, BENCHMARK_DATA_SOURCE),
            "risk_proxy": source_record(paths, RISK_PROXY_SOURCE),
        },
        "universe": list(DEFAULT_UNIVERSE),
        "symbols": symbol_records,
        "benchmarks": benchmark_records,
        "risk_proxy_available": risk_row is not None,
        "risk_proxy_as_of_date": risk_row.get("as_of_date") if risk_row else None,
        "no_external_download": True,
        "boundary": workflow_boundary("snapshot_only"),
    }
    json_path = paths.data_dir / "daily_workflow" / "snapshots" / f"daily_market_data_snapshot-{as_of}.json"
    md_path = paths.outputs_dir / "daily_workflow" / f"DAILY_MARKET_DATA_SNAPSHOT-{as_of}.md"
    return write_artifact(json_path, payload, md_path, build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Market Data Snapshot - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Summary",
        f"- latest_available_trading_date: {payload['latest_available_trading_date']}",
        f"- symbols: {sum(1 for item in payload['symbols'].values() if item['available'])}/{len(payload['symbols'])}",
        f"- risk_proxy_available: {str(payload['risk_proxy_available']).lower()}",
        "",
        "## Boundary",
    ]
    lines.extend(boundary_markdown("snapshot only"))
    lines.append("")
    return "\n".join(lines)

