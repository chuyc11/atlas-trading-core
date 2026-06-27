"""Local historical panel fallback adapter."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import normalize_symbol, read_frame, utc_now
from trading_core.equity_data_quality.history_manifest import history_dirs
from trading_core.storage.file_paths import ProjectPaths


PROVIDER_NAME = "local_file_provider"


def fetch_local_price_history(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    paths: ProjectPaths,
    adjustment_type: str = "raw",
    max_workers: int = 1,
    retry: int = 0,
    rate_limit_per_minute: int | None = None,
) -> dict[str, Any]:
    del adjustment_type, max_workers, retry, rate_limit_per_minute
    panel = read_frame(history_dirs(paths)["market_history"] / "daily_price_history_panel.parquet")
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    wanted = {normalize_symbol(symbol) for symbol in symbols}
    if not panel.empty:
        panel = panel[panel["symbol"].isin(wanted)]
        panel = panel[(panel["date"] >= start_date) & (panel["date"] <= end_date)]
        rows = panel.to_dict("records")
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in wanted}
    for row in rows:
        by_symbol.setdefault(normalize_symbol(row.get("symbol")), []).append(row)
    for symbol in symbols:
        normalized = normalize_symbol(symbol)
        symbol_rows = by_symbol.get(normalized, [])
        dates = [row.get("date") for row in symbol_rows if row.get("date")]
        reason = "" if symbol_rows else "no local historical rows"
        symbol_results.append(
            {
                "symbol": normalized,
                "provider": PROVIDER_NAME,
                "provider_attempted": True,
                "provider_succeeded": bool(symbol_rows),
                "provider_failed": not bool(symbol_rows),
                "row_count": len(symbol_rows),
                "first_date": min(dates) if dates else "",
                "last_date": max(dates) if dates else "",
                "failure_reason": reason,
                "last_attempted_at": utc_now(),
            }
        )
        if not symbol_rows:
            failed.append({"symbol": normalized, "reason": reason})
    return {
        "provider": PROVIDER_NAME,
        "attempted_symbols": symbols,
        "succeeded_symbols": sorted({row["symbol"] for row in rows}),
        "failed_symbols": failed,
        "symbol_results": symbol_results,
        "rows": rows,
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }
