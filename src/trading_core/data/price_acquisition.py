"""Acquire historical ETF daily bars into local CSV data packages."""

from __future__ import annotations

import csv
from datetime import date as Date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

from trading_core.data.data_package_validator import REQUIRED_COLUMNS, validate_data_package
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json
from trading_core.universe.universe_loader import load_universe


AKSHARE_REQUIRED_MESSAGE = "akshare is required for fetch-prices. Install it manually or provide CSV data."


class PriceSource(Protocol):
    source_name: str

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """Return raw OHLCV rows for one symbol."""


class AkSharePriceSource:
    source_name = "akshare"

    def __init__(self, ak_module: Any | None = None, retries: int = 3) -> None:
        self.retries = retries
        if ak_module is not None:
            self.ak = ak_module
            return
        try:
            import akshare as ak  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(AKSHARE_REQUIRED_MESSAGE) from exc
        self.ak = ak

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for start, end in _month_chunks(start_date, end_date):
            frame = self._fetch_frame(symbol, market, start, end)
            records.extend(_records_from_frame(frame))
        return _dedupe_records(records)

    def _fetch_frame(self, symbol: str, market: str, start_date: str, end_date: str) -> Any:
        start = _compact_date(start_date)
        end = _compact_date(end_date)
        last_error: Exception | None = None
        for _ in range(max(1, self.retries)):
            try:
                return self._fetch_frame_once(symbol, market, start, end)
            except Exception as exc:  # noqa: BLE001 - preserve source error after bounded retries.
                last_error = exc
        raise last_error if last_error else RuntimeError("akshare fetch failed")

    def _fetch_frame_once(self, symbol: str, market: str, start: str, end: str) -> Any:
        if market == "HK":
            return self.ak.stock_hk_hist(
                symbol=_hk_symbol(symbol),
                period="daily",
                start_date=start,
                end_date=end,
                adjust="qfq",
            )
        return self.ak.fund_etf_hist_em(
            symbol=_a_share_symbol(symbol),
            period="daily",
            start_date=start,
            end_date=end,
            adjust="qfq",
        )


def fetch_prices(
    start_date: str,
    end_date: str,
    output_path: Path,
    paths: ProjectPaths | None = None,
    source: PriceSource | None = None,
    universe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    source = source or AkSharePriceSource()
    universe = universe or load_universe()
    symbols = [row for row in universe.get("symbols", []) if row.get("asset_type") == "ETF"]
    output_path = _resolve_output_path(output_path, paths)
    output_path.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    symbols_success: list[str] = []
    symbols_failed: list[str] = []
    output_files: dict[str, str] = {}

    for item in symbols:
        symbol = str(item["symbol"])
        market = str(item["market"])
        try:
            raw_rows = source.fetch_daily(symbol, market, start_date, end_date)
            normalized = [_normalize_row(symbol, raw, source.source_name) for raw in raw_rows]
            if not normalized:
                raise ValueError("no rows returned")
            output_file = output_path / f"{symbol}.csv"
            _write_symbol_csv(output_file, normalized)
            symbols_success.append(symbol)
            output_files[symbol] = str(output_file)
        except Exception as exc:  # noqa: BLE001 - per-symbol acquisition must not abort the package.
            symbols_failed.append(symbol)
            warnings.append(f"{symbol}: {exc}")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "start_date": start_date,
        "end_date": end_date,
        "symbols_requested": [str(row["symbol"]) for row in symbols],
        "symbols_success": symbols_success,
        "symbols_failed": symbols_failed,
        "source": source.source_name,
        "warnings": warnings,
        "output_path": str(output_path),
        "output_files": output_files,
    }
    manifest_path = output_path / "manifest.json"
    write_json(manifest_path, manifest)
    validation = validate_data_package(output_path, paths)
    return {"manifest_path": str(manifest_path), "manifest": manifest, "validation": validation}


def _normalize_row(symbol: str, row: dict[str, Any], source_name: str) -> dict[str, Any]:
    return {
        "date": _date_value(_first(row, ["date", "日期", "时间"])),
        "symbol": symbol,
        "open": _positive_float(_first(row, ["open", "开盘", "今开"]), "open"),
        "high": _positive_float(_first(row, ["high", "最高"]), "high"),
        "low": _positive_float(_first(row, ["low", "最低"]), "low"),
        "close": _positive_float(_first(row, ["close", "收盘", "最新价"]), "close"),
        "volume": _non_negative_float(_first(row, ["volume", "成交量"]), "volume"),
        "source": source_name,
        "quality": "fresh",
    }


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


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for row in records:
        by_date[_date_value(_first(row, ["date", "日期", "时间"]))] = row
    return [by_date[key] for key in sorted(by_date)]


def _month_chunks(start_date: str, end_date: str) -> list[tuple[str, str]]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    chunks: list[tuple[str, str]] = []
    current = start
    while current <= end:
        next_month = Date(current.year + (1 if current.month == 12 else 0), 1 if current.month == 12 else current.month + 1, 1)
        chunk_end = min(next_month - timedelta(days=1), end)
        chunks.append((current.isoformat(), chunk_end.isoformat()))
        current = next_month
    return chunks


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
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _non_negative_float(value: Any, name: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def _compact_date(value: str) -> str:
    return value.replace("-", "")


def _a_share_symbol(symbol: str) -> str:
    return symbol.split(".", 1)[0]


def _hk_symbol(symbol: str) -> str:
    return symbol.split(".", 1)[0].zfill(5)


def _resolve_output_path(output_path: Path, paths: ProjectPaths) -> Path:
    if output_path.is_absolute():
        return output_path
    parts = [part.lower() for part in output_path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / output_path
    return output_path.resolve()
