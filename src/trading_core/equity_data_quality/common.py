"""Shared helpers for v0.7.1 A-share data foundation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


TARGET_VERSION = "v0.7.1-a-share-full-market-data-ingestion"
HISTORICAL_BACKFILL_VERSION = "v0.7.1.1-a-share-historical-panel-backfill"
HISTORICAL_TARGET_VERSION = "v0.7.1.2-a-share-historical-data-provider-expansion"
HISTORICAL_BASELINE_VERSION = "v0.7.1-a-share-full-market-data-ingestion"
HISTORICAL_BASELINE_FAIL_CLOSED_COMMIT = "1138fc08ff9d406e6683e2b488358f1407c53143"
RECOMMENDED_NEXT_VERSION = "v0.7.2-a-share-tradable-universe-filter"
HISTORICAL_DATA_SOURCE_UPGRADE_VERSION = "v0.7.1.3-a-share-historical-data-source-upgrade"
SNAPSHOT_CACHE = "a_share_public_snapshot_cache.json"

EQUITY_MASTER_COLUMNS = [
    "symbol",
    "exchange",
    "market",
    "name",
    "list_date",
    "delist_date",
    "board",
    "is_active",
    "is_st",
    "is_star_market",
    "is_chinext",
    "is_bse",
    "currency",
    "source",
    "source_timestamp",
]
TRADING_CALENDAR_COLUMNS = ["date", "exchange", "is_trading_day", "previous_trading_day", "next_trading_day", "source", "source_timestamp"]
DAILY_PRICE_COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume", "amount", "turnover", "pre_close", "change", "pct_change", "source", "source_timestamp"]
ADJUSTED_PRICE_COLUMNS = ["date", "symbol", "adj_open", "adj_high", "adj_low", "adj_close", "adj_factor", "adjustment_type", "source", "source_timestamp"]
DAILY_BASIC_COLUMNS = ["date", "symbol", "total_mv", "circ_mv", "turnover_rate", "volume_ratio", "pe", "pe_ttm", "pb", "ps", "ps_ttm", "dv_ratio", "dv_ttm", "source", "source_timestamp"]
INDUSTRY_COLUMNS = ["symbol", "industry_level_1", "industry_level_2", "industry_level_3", "industry_standard", "effective_date", "source", "source_timestamp"]
FINANCIAL_COLUMNS = ["report_date", "ann_date", "symbol", "revenue", "net_profit", "roe", "gross_margin", "net_margin", "operating_cash_flow", "debt_to_asset", "eps", "bps", "source", "source_timestamp"]
DAILY_PRICE_HISTORY_COLUMNS = [*DAILY_PRICE_COLUMNS, "provider", "ingested_at"]
ADJUSTED_PRICE_HISTORY_COLUMNS = [*ADJUSTED_PRICE_COLUMNS, "provider", "ingested_at"]
DAILY_BASIC_HISTORY_COLUMNS = [*DAILY_BASIC_COLUMNS, "provider", "ingested_at"]
FINANCIAL_HISTORY_COLUMNS = [*FINANCIAL_COLUMNS, "provider", "ingested_at"]

PROTECTED_BOUNDARY = {
    "data_ingestion_only": True,
    "selection_generated": False,
    "scores_generated": False,
    "virtual_portfolio_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "third_party_code_merged_into_main_flow": False,
    "model_profit_guaranteed": False,
}
HISTORICAL_BOUNDARY = {
    "historical_backfill_only": True,
    "data_backfill_only": True,
    "selection_generated": False,
    "scores_generated": False,
    "candidates_generated": False,
    "virtual_portfolio_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "third_party_code_merged_into_main_flow": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def latest_weekday(today: date | None = None) -> str:
    current = today or date.today()
    while current.weekday() >= 5:
        current -= timedelta(days=1)
    return current.isoformat()


def safe_float(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    number = safe_float(value)
    return int(number) if number is not None else None


def normalize_symbol(code: Any) -> str:
    text = str(code).strip().upper()
    if "." in text:
        raw, suffix = text.split(".", 1)
        return f"{raw.zfill(6)}.{suffix}"
    raw = text.zfill(6)
    if raw.startswith(("6", "9")):
        return f"{raw}.SH"
    if raw.startswith(("4", "8")):
        return f"{raw}.BJ"
    return f"{raw}.SZ"


def exchange_for_symbol(symbol: str) -> str:
    suffix = symbol.split(".")[-1]
    return {"SH": "SSE", "SZ": "SZSE", "BJ": "BSE"}.get(suffix, "UNKNOWN")


def board_for_symbol(symbol: str) -> str:
    code = symbol.split(".")[0]
    if symbol.endswith(".BJ"):
        return "BSE"
    if code.startswith("688"):
        return "STAR"
    if code.startswith(("300", "301")):
        return "CHINEXT"
    if code.startswith("6"):
        return "SSE_MAIN"
    if code.startswith(("0", "2")):
        return "SZSE_MAIN"
    return "UNKNOWN"


def normalize_date(value: Any, fallback: str | None = None) -> str:
    if value in (None, "", "-", "--"):
        return fallback or ""
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"
    return text[:10]


def data_quality_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_data_quality"


def snapshot_cache_path(paths: ProjectPaths) -> Path:
    return data_quality_dir(paths) / SNAPSHOT_CACHE


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, ensure_ascii=False), encoding="utf-8")


def write_frame(frame: pd.DataFrame, parquet_path: Path, json_path: Path | None = None) -> None:
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(parquet_path, index=False)
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(frame.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")


def read_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": rel(path, root),
        "exists": path.exists(),
        "rows": int(len(read_frame(path))) if path.exists() and path.suffix == ".parquet" else None,
        "sha256": sha256_file(path),
    }


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def write_report(json_path: Path, payload: dict[str, Any], report_path: Path, markdown: str) -> dict[str, Any]:
    safe_payload = json_safe(payload)
    write_json_markdown(json_path, safe_payload, report_path, markdown)
    return {**safe_payload, "json_path": str(json_path), "report_path": str(report_path)}


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    return value


def markdown_boundary() -> list[str]:
    return [
        "- Data ingestion only.",
        "- No stock scores generated.",
        "- No candidates generated.",
        "- No virtual portfolios generated.",
        "- Official forward dry-run status unchanged.",
        "- Day2 was not executed.",
        "- run-daily was not called.",
        "- No broker is connected.",
        "- No real orders were placed.",
        "- Third-party code was not merged into the main flow.",
        "- This is not a model profit guarantee.",
    ]


def default_project_paths(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def source_timestamp(snapshot: dict[str, Any]) -> str:
    return str(snapshot.get("source_timestamp") or utc_now())
