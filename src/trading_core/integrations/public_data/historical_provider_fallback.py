"""Provider fallback orchestration for A-share historical prices."""

from __future__ import annotations

from typing import Any, Callable

from trading_core.equity_data_quality.common import normalize_symbol, utc_now
from trading_core.integrations.public_data.akshare_history_provider import fetch_akshare_price_history
from trading_core.integrations.public_data.baostock_history_provider import fetch_baostock_price_history
from trading_core.integrations.public_data.eastmoney_kline_provider import fetch_eastmoney_price_history
from trading_core.integrations.public_data.local_history_provider import fetch_local_price_history
from trading_core.integrations.public_data.tushare_history_provider import fetch_tushare_price_history
from trading_core.storage.file_paths import ProjectPaths


DEFAULT_PROVIDER_PRIORITY = ["eastmoney", "akshare", "baostock", "tushare", "local"]
PROVIDER_ALIASES = {
    "eastmoney": "eastmoney_kline_public_http",
    "eastmoney_kline_public_http": "eastmoney_kline_public_http",
    "akshare": "akshare_provider",
    "akshare_provider": "akshare_provider",
    "baostock": "baostock_provider",
    "baostock_provider": "baostock_provider",
    "tushare": "tushare_provider",
    "tushare_provider": "tushare_provider",
    "local": "local_file_provider",
    "local_file_provider": "local_file_provider",
}


def normalize_provider_priority(value: str | list[str] | None) -> list[str]:
    if value is None:
        raw = DEFAULT_PROVIDER_PRIORITY
    elif isinstance(value, str):
        raw = [part.strip() for part in value.split(",") if part.strip()]
    else:
        raw = value
    providers: list[str] = []
    for item in raw:
        provider = PROVIDER_ALIASES.get(str(item).strip(), str(item).strip())
        if provider and provider not in providers:
            providers.append(provider)
    return providers or [PROVIDER_ALIASES["eastmoney"]]


def fetch_price_history_with_fallback(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    adjustment_type: str = "raw",
    provider_priority: str | list[str] | None = None,
    max_workers: int = 32,
    retry: int = 2,
    rate_limit_per_minute: int | None = None,
) -> dict[str, Any]:
    providers = normalize_provider_priority(provider_priority)
    remaining = [normalize_symbol(symbol) for symbol in symbols]
    rows: list[dict[str, Any]] = []
    failed_by_provider: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    provider_breakdown: dict[str, dict[str, int]] = {}
    external_api_called = False
    for provider in providers:
        if not remaining:
            break
        fetcher = _fetcher(provider)
        kwargs = {
            "start_date": start_date,
            "end_date": end_date,
            "adjustment_type": adjustment_type,
            "max_workers": max_workers,
            "retry": retry,
            "rate_limit_per_minute": rate_limit_per_minute,
        }
        if provider == "local_file_provider":
            if paths is None:
                result = _provider_unavailable(provider, remaining, "paths required for local_file_provider")
            else:
                result = fetch_local_price_history(remaining, paths=paths, **kwargs)
        else:
            result = fetcher(remaining, **kwargs)
        external_api_called = external_api_called or bool(result.get("external_api_called"))
        rows.extend(result.get("rows", []))
        symbol_results.extend(result.get("symbol_results", []))
        failed_by_provider.extend({"provider": provider, **item} for item in result.get("failed_symbols", []))
        succeeded = {normalize_symbol(symbol) for symbol in result.get("succeeded_symbols", [])}
        attempted = {normalize_symbol(symbol) for symbol in result.get("attempted_symbols", remaining)}
        provider_breakdown[provider] = {
            "attempted_symbol_count": len(attempted),
            "succeeded_symbol_count": len(succeeded),
            "failed_symbol_count": max(0, len(attempted - succeeded)),
        }
        remaining = [symbol for symbol in remaining if symbol not in succeeded]
    failed_symbols = [{"symbol": symbol, "reason": _latest_failure(symbol, failed_by_provider)} for symbol in remaining]
    return {
        "provider": "+".join(providers),
        "providers_attempted": providers,
        "providers_succeeded": [provider for provider, stats in provider_breakdown.items() if stats["succeeded_symbol_count"] > 0],
        "providers_failed": failed_by_provider,
        "provider_breakdown": provider_breakdown,
        "attempted_symbols": [normalize_symbol(symbol) for symbol in symbols],
        "succeeded_symbols": sorted({normalize_symbol(row["symbol"]) for row in rows if row.get("symbol")}),
        "failed_symbols": failed_symbols,
        "symbol_results": symbol_results,
        "rows": rows,
        "external_api_called": external_api_called,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }


def _fetcher(provider: str) -> Callable[..., dict[str, Any]]:
    return {
        "eastmoney_kline_public_http": fetch_eastmoney_price_history,
        "akshare_provider": fetch_akshare_price_history,
        "baostock_provider": fetch_baostock_price_history,
        "tushare_provider": fetch_tushare_price_history,
    }[provider]


def _latest_failure(symbol: str, failures: list[dict[str, Any]]) -> str:
    normalized = normalize_symbol(symbol)
    for failure in reversed(failures):
        if normalize_symbol(failure.get("symbol")) == normalized:
            provider = failure.get("provider", "")
            reason = failure.get("reason", "")
            return f"{provider}: {reason}" if provider else str(reason)
    return "no provider returned historical rows"


def _provider_unavailable(provider: str, symbols: list[str], reason: str) -> dict[str, Any]:
    return {
        "provider": provider,
        "attempted_symbols": symbols,
        "succeeded_symbols": [],
        "failed_symbols": [{"symbol": normalize_symbol(symbol), "reason": reason} for symbol in symbols],
        "symbol_results": [
            {
                "symbol": normalize_symbol(symbol),
                "provider": provider,
                "provider_attempted": True,
                "provider_succeeded": False,
                "provider_failed": True,
                "row_count": 0,
                "first_date": "",
                "last_date": "",
                "failure_reason": reason,
                "last_attempted_at": utc_now(),
            }
            for symbol in symbols
        ],
        "rows": [],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }
