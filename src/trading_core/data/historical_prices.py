"""Historical ETF price import and loading."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_jsonl


REQUIRED_COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume", "source", "quality"]


def import_prices_csv(input_path: Path, market: str, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    rows: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing CSV columns: {missing}")
        for row in reader:
            rows.append(
                {
                    "date": row["date"],
                    "symbol": row["symbol"],
                    "market": market,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "source": row["source"],
                    "quality": row["quality"],
                }
            )
    output = paths.data_dir / "raw" / "prices" / f"prices-{market}.jsonl"
    write_jsonl(output, rows)
    return {"rows_imported": len(rows), "output_path": str(output)}


def load_imported_prices(market: str = "A_SHARE", paths: ProjectPaths | None = None) -> list[dict[str, Any]]:
    paths = paths or project_paths()
    return read_jsonl(paths.data_dir / "raw" / "prices" / f"prices-{market}.jsonl")


def prices_by_date(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    sorted_rows = sorted(rows, key=lambda row: (row["symbol"], row["date"]))
    previous_close: dict[str, float] = {}
    for row in sorted_rows:
        date = str(row["date"])
        symbol = str(row["symbol"])
        close = float(row["close"])
        prior = previous_close.get(symbol, close)
        grouped.setdefault(date, {})[symbol] = {
            "symbol": symbol,
            "market": row.get("market", "A_SHARE"),
            "open": float(row["open"]),
            "price": close,
            "close": close,
            "previous_close": prior,
            "volume": row.get("volume"),
            "source": row.get("source"),
            "quality": row.get("quality", "fresh"),
        }
        previous_close[symbol] = close
    return grouped
