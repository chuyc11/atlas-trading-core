"""Acquire historical ETF daily bars into local CSV data packages."""

from __future__ import annotations

import csv
import math
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Protocol

from trading_core.config_loader import load_config
from trading_core.data.data_package_validator import REQUIRED_COLUMNS, validate_data_package
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json
from trading_core.universe.universe_loader import load_universe


AKSHARE_REQUIRED_MESSAGE = "akshare is required for fetch-prices. Install it manually or provide CSV data."
YFINANCE_REQUIRED_MESSAGE = "yfinance is required for source=yfinance. Install it manually or use source=akshare/manual_csv."
YFINANCE_LIMITATION = "Yahoo/yfinance data is used for research fallback and should be validated before backtesting."
VALID_SOURCE_MODES = {"akshare", "yfinance", "auto"}


class PriceSource(Protocol):
    source_name: str

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """Return raw OHLCV rows for one symbol."""


class AkSharePriceSource:
    source_name = "akshare"

    def __init__(self, ak_module: Any | None = None, symbol_mapping: dict[str, Any] | None = None) -> None:
        self.symbol_mapping = symbol_mapping or {}
        if ak_module is not None:
            self.ak = ak_module
            return
        try:
            import akshare as ak  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(AKSHARE_REQUIRED_MESSAGE) from exc
        self.ak = ak

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        start = _compact_date(start_date)
        end = _compact_date(end_date)
        mapped = _mapped_symbol(self.symbol_mapping, symbol, "akshare") or _akshare_symbol(symbol, market)
        if market == "HK":
            frame = self.ak.stock_hk_hist(
                symbol=mapped,
                period="daily",
                start_date=start,
                end_date=end,
                adjust="qfq",
            )
        else:
            frame = self.ak.fund_etf_hist_em(
                symbol=mapped,
                period="daily",
                start_date=start,
                end_date=end,
                adjust="qfq",
            )
        return _dedupe_records(_records_from_frame(frame))


class YFinancePriceSource:
    source_name = "yfinance"

    def __init__(self, yf_module: Any | None = None, symbol_mapping: dict[str, Any] | None = None) -> None:
        self.symbol_mapping = symbol_mapping or {}
        if yf_module is not None:
            self.yf = yf_module
            return
        try:
            import yfinance as yf  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(YFINANCE_REQUIRED_MESSAGE) from exc
        self.yf = yf

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        mapped = _mapped_symbol(self.symbol_mapping, symbol, "yfinance")
        if not mapped:
            raise ValueError(f"missing yfinance mapping for {symbol}")
        frame = self.yf.download(
            mapped,
            start=start_date,
            end=_exclusive_end_date(end_date),
            interval="1d",
            progress=False,
            auto_adjust=False,
            group_by="column",
            multi_level_index=False,
        )
        records = _records_from_yfinance_frame(frame)
        if not records:
            raise ValueError("no rows returned")
        return records


def fetch_prices(
    start_date: str,
    end_date: str,
    output_path: Path,
    paths: ProjectPaths | None = None,
    source: PriceSource | None = None,
    universe: dict[str, Any] | None = None,
    source_mode: str = "akshare",
    sources: dict[str, PriceSource] | None = None,
    config: dict[str, Any] | None = None,
    symbol_mapping: dict[str, Any] | None = None,
    sleep_func: Callable[[float], None] = time.sleep,
    random_func: Callable[[], float] = random.random,
) -> dict[str, Any]:
    paths = paths or project_paths()
    config = config or load_config("price_acquisition.yaml")
    symbol_mapping = symbol_mapping or load_config("symbol_mapping.yaml")
    universe = universe or load_universe()
    source_mode = source.source_name if source is not None and source_mode == "akshare" else source_mode
    if source_mode not in VALID_SOURCE_MODES and source is None:
        raise ValueError(f"Unsupported price source: {source_mode}")

    source_map = sources or _build_source_map(source_mode, symbol_mapping, source)
    symbols = [row for row in universe.get("symbols", []) if row.get("asset_type") == "ETF"]
    output_path = _resolve_output_path(output_path, paths)
    output_path.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    symbols_success: list[str] = []
    symbols_failed: list[str] = []
    output_files: dict[str, str] = {}
    source_by_symbol: dict[str, str] = {}
    fallback_source: dict[str, str] = {}
    attempts_by_symbol: dict[str, list[dict[str, Any]]] = {}
    errors_by_symbol: dict[str, list[str]] = {}
    elapsed_seconds_by_symbol: dict[str, float] = {}

    for index, item in enumerate(symbols):
        symbol = str(item["symbol"])
        market = str(item["market"])
        started = perf_counter()
        attempts_by_symbol[symbol] = []
        errors_by_symbol[symbol] = []
        result = _fetch_symbol(
            symbol,
            market,
            start_date,
            end_date,
            source_mode,
            source_map,
            config,
            attempts_by_symbol[symbol],
            errors_by_symbol[symbol],
            sleep_func,
            random_func,
        )
        elapsed_seconds_by_symbol[symbol] = round(perf_counter() - started, 6)
        if result["rows"]:
            source_name = str(result["source"])
            try:
                normalized, row_warnings = _normalize_rows(symbol, result["rows"], source_name)
                warnings.extend(f"{symbol}: {warning}" for warning in row_warnings)
                errors_by_symbol[symbol].extend(row_warnings)
                if not normalized:
                    raise ValueError("no valid rows after source-row validation")
                output_file = output_path / f"{symbol}.csv"
                _write_symbol_csv(output_file, normalized)
                symbols_success.append(symbol)
                output_files[symbol] = str(output_file)
                source_by_symbol[symbol] = source_name
                if result.get("fallback_source"):
                    fallback_source[symbol] = str(result["fallback_source"])
            except Exception as exc:  # noqa: BLE001 - bad source rows must be audited, not crash the batch.
                symbols_failed.append(symbol)
                error = f"{source_name} normalize: {exc}"
                errors_by_symbol[symbol].append(error)
                attempts_by_symbol[symbol].append(
                    {
                        "source": source_name,
                        "attempt": "normalize",
                        "status": "failed",
                        "error": str(exc),
                        "sleep_seconds": 0.0,
                    }
                )
                warnings.append(f"{symbol}: {error}")
        else:
            symbols_failed.append(symbol)
            warnings.append(f"{symbol}: {errors_by_symbol[symbol][-1] if errors_by_symbol[symbol] else 'fetch failed'}")
        if index < len(symbols) - 1:
            sleep_seconds = float(config.get("throttle", {}).get("sleep_between_symbols_seconds", 0))
            if sleep_seconds > 0:
                sleep_func(sleep_seconds)

    if any(source_name == "yfinance" for source_name in source_by_symbol.values()):
        warnings.append(YFINANCE_LIMITATION)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "start_date": start_date,
        "end_date": end_date,
        "symbols_requested": [str(row["symbol"]) for row in symbols],
        "symbols_success": symbols_success,
        "symbols_failed": symbols_failed,
        "source": source_mode,
        "source_by_symbol": source_by_symbol,
        "fallback_source": fallback_source,
        "warnings": warnings,
        "output_path": str(output_path),
        "output_files": output_files,
        "attempts_by_symbol": attempts_by_symbol,
        "errors_by_symbol": errors_by_symbol,
        "elapsed_seconds_by_symbol": elapsed_seconds_by_symbol,
        "retry_policy": config.get("retry", {}),
        "throttle_policy": config.get("throttle", {}),
        "failure_policy": config.get("failure_policy", {}),
    }
    manifest_path = output_path / "manifest.json"
    write_json(manifest_path, manifest)
    validation = validate_data_package(output_path, paths)
    return {"manifest_path": str(manifest_path), "manifest": manifest, "validation": validation}


def should_return_failure(result: dict[str, Any]) -> bool:
    return bool(result["manifest"]["symbols_requested"]) and not result["manifest"]["symbols_success"]


def _build_source_map(source_mode: str, symbol_mapping: dict[str, Any], source: PriceSource | None) -> dict[str, PriceSource]:
    if source is not None:
        return {source.source_name: source}
    if source_mode == "akshare":
        return {"akshare": AkSharePriceSource(symbol_mapping=symbol_mapping)}
    if source_mode == "yfinance":
        return {"yfinance": YFinancePriceSource(symbol_mapping=symbol_mapping)}
    return {
        "akshare": AkSharePriceSource(symbol_mapping=symbol_mapping),
        "yfinance": YFinancePriceSource(symbol_mapping=symbol_mapping),
    }


def _fetch_symbol(
    symbol: str,
    market: str,
    start_date: str,
    end_date: str,
    source_mode: str,
    sources: dict[str, PriceSource],
    config: dict[str, Any],
    attempts: list[dict[str, Any]],
    errors: list[str],
    sleep_func: Callable[[float], None],
    random_func: Callable[[], float],
) -> dict[str, Any]:
    source_order = ["akshare", "yfinance"] if source_mode == "auto" else [source_mode]
    for index, source_name in enumerate(source_order):
        source = sources.get(source_name)
        if source is None:
            errors.append(f"{source_name}: source unavailable")
            continue
        rows = _fetch_with_retry(source, symbol, market, start_date, end_date, config, attempts, errors, sleep_func, random_func)
        if rows:
            return {
                "rows": rows,
                "source": source_name,
                "fallback_source": source_name if source_mode == "auto" and index > 0 else None,
            }
    return {"rows": [], "source": None, "fallback_source": None}


def _fetch_with_retry(
    source: PriceSource,
    symbol: str,
    market: str,
    start_date: str,
    end_date: str,
    config: dict[str, Any],
    attempts: list[dict[str, Any]],
    errors: list[str],
    sleep_func: Callable[[float], None],
    random_func: Callable[[], float],
) -> list[dict[str, Any]]:
    retry = config.get("retry", {})
    max_attempts = int(retry.get("max_attempts", 1))
    initial_sleep = float(retry.get("initial_sleep_seconds", 0))
    multiplier = float(retry.get("backoff_multiplier", 1))
    jitter = float(retry.get("jitter_seconds", 0))
    for attempt in range(1, max(1, max_attempts) + 1):
        try:
            rows = source.fetch_daily(symbol, market, start_date, end_date)
            if not rows:
                raise ValueError("no rows returned")
            attempts.append({"source": source.source_name, "attempt": attempt, "status": "success", "sleep_seconds": 0.0})
            return rows
        except Exception as exc:  # noqa: BLE001 - acquisition must record source errors, not abort all symbols.
            error = f"{source.source_name} attempt {attempt}: {exc}"
            errors.append(error)
            sleep_seconds = _retry_sleep_seconds(attempt, max_attempts, initial_sleep, multiplier, jitter, random_func)
            attempts.append(
                {
                    "source": source.source_name,
                    "attempt": attempt,
                    "status": "failed",
                    "error": str(exc),
                    "sleep_seconds": round(sleep_seconds, 6),
                }
            )
            if sleep_seconds > 0:
                sleep_func(sleep_seconds)
    return []


def _retry_sleep_seconds(
    attempt: int,
    max_attempts: int,
    initial_sleep: float,
    multiplier: float,
    jitter: float,
    random_func: Callable[[], float],
) -> float:
    if attempt >= max_attempts:
        return 0.0
    base = initial_sleep * (multiplier ** max(0, attempt - 1))
    return max(0.0, base + (jitter * random_func()))


def _normalize_row(symbol: str, row: dict[str, Any], source_name: str) -> dict[str, Any]:
    return {
        "date": _date_value(_first(row, ["date", "日期", "Date", "时间"])),
        "symbol": symbol,
        "open": _positive_float(_first(row, ["open", "开盘", "Open", "今开"]), "open"),
        "high": _positive_float(_first(row, ["high", "最高", "High"]), "high"),
        "low": _positive_float(_first(row, ["low", "最低", "Low"]), "low"),
        "close": _positive_float(_first(row, ["close", "收盘", "Close", "最新价"]), "close"),
        "volume": _non_negative_float(_first(row, ["volume", "成交量", "Volume"]), "volume"),
        "source": source_name,
        "quality": "fresh",
    }


def _normalize_rows(symbol: str, rows: list[dict[str, Any]], source_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    normalized = []
    warnings = []
    for index, row in enumerate(rows, 1):
        try:
            item = _normalize_row(symbol, row, source_name)
            _validate_normalized_ohlc(item)
        except Exception as exc:  # noqa: BLE001 - invalid source rows are dropped and audited.
            raw_date = _safe_date(row)
            warnings.append(f"dropped invalid {source_name} row {raw_date or index}: {exc}")
            continue
        normalized.append(item)
    return normalized, warnings


def _validate_normalized_ohlc(row: dict[str, Any]) -> None:
    open_price = float(row["open"])
    high = float(row["high"])
    low = float(row["low"])
    close = float(row["close"])
    if high < max(open_price, close, low):
        raise ValueError("high below OHLC max")
    if low > min(open_price, close, high):
        raise ValueError("low above OHLC min")


def _safe_date(row: dict[str, Any]) -> str | None:
    try:
        return _date_value(_first(row, ["date", "日期", "Date", "Datetime", "时间"]))
    except Exception:
        return None


def _write_symbol_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in REQUIRED_COLUMNS})


def _records_from_frame(frame: Any) -> list[dict[str, Any]]:
    if hasattr(frame, "to_dict"):
        return list(frame.to_dict("records"))
    if isinstance(frame, list):
        return [dict(row) for row in frame]
    raise TypeError("unsupported akshare response type")


def _records_from_yfinance_frame(frame: Any) -> list[dict[str, Any]]:
    if frame is None:
        return []
    if hasattr(frame, "empty") and bool(frame.empty):
        return []
    if hasattr(frame, "reset_index"):
        frame = frame.reset_index()
    records = _records_from_frame(frame)
    output = []
    for row in records:
        output.append(
            {
                "date": _row_get(row, ["Date", "Datetime", "date"]),
                "open": _row_get(row, ["Open", "open"]),
                "high": _row_get(row, ["High", "high"]),
                "low": _row_get(row, ["Low", "low"]),
                "close": _row_get(row, ["Close", "close"]),
                "volume": _row_get(row, ["Volume", "volume"], default=0),
            }
        )
    return output


def _row_get(row: dict[str, Any], names: list[str], default: Any | None = None) -> Any:
    lowered = {name.lower() for name in names}
    for key, value in row.items():
        if key in names:
            return value
        if isinstance(key, tuple) and key and str(key[0]).lower() in lowered:
            return value
        if str(key).lower() in lowered:
            return value
    return default


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for row in records:
        by_date[_date_value(_first(row, ["date", "日期", "Date", "时间"]))] = row
    return [by_date[key] for key in sorted(by_date)]


def _first(row: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    raise ValueError(f"missing column: {names[0]}")


def _date_value(value: Any) -> str:
    text = str(value)[:10]
    return datetime.strptime(text, "%Y-%m-%d").date().isoformat()


def _positive_float(value: Any, name: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _non_negative_float(value: Any, name: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def _compact_date(value: str) -> str:
    return value.replace("-", "")


def _exclusive_end_date(value: str) -> str:
    parsed = datetime.strptime(value, "%Y-%m-%d").date()
    return (parsed + timedelta(days=1)).isoformat()


def _akshare_symbol(symbol: str, market: str) -> str:
    raw = symbol.split(".", 1)[0]
    return raw.zfill(5) if market == "HK" else raw


def _mapped_symbol(symbol_mapping: dict[str, Any], symbol: str, source_name: str) -> str | None:
    row = symbol_mapping.get(symbol, {})
    value = row.get(source_name) if isinstance(row, dict) else None
    return str(value) if value else None


def _resolve_output_path(output_path: Path, paths: ProjectPaths) -> Path:
    if output_path.is_absolute():
        return output_path
    parts = [part.lower() for part in output_path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / output_path
    return output_path.resolve()
