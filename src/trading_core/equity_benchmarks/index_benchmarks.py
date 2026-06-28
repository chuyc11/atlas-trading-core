"""Index benchmark price loading for v0.7.10."""

from __future__ import annotations

import json
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_benchmarks.benchmark_config import (
    EASTMONEY_SECID_MAP,
    INDEX_BENCHMARK_IDS,
    INDEX_CODE_MAP,
    BenchmarkConfig,
    candidate_index_panel_paths,
    index_history_cache_paths,
)
from trading_core.equity_data_quality.common import json_safe, read_frame, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def load_index_benchmark_prices(
    *,
    paths: ProjectPaths,
    config: BenchmarkConfig,
    generated_at: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    generated_at = generated_at or utc_now()
    local = _load_local_index_panel(paths, config)
    source_attempts: list[dict[str, Any]] = []
    if _has_all_index_benchmarks(local, config):
        return local, _source_metadata("local_index_price_panel", _local_source_path(paths), source_attempts)

    fetched, fetch_attempts = fetch_eastmoney_index_history(config=config, generated_at=generated_at)
    source_attempts.extend(fetch_attempts)
    if not fetched.empty:
        cache_paths = index_history_cache_paths(paths)
        cache_paths["index_price_history_panel"].parent.mkdir(parents=True, exist_ok=True)
        fetched.to_parquet(cache_paths["index_price_history_panel"], index=False)
        write_json(
            cache_paths["index_price_history_manifest"],
            {
                "manifest_id": "A-SHARE-INDEX-BENCHMARK-HISTORY-MANIFEST",
                "target_version": config.to_dict()["target_version"],
                "as_of_date": config.as_of_date,
                "generated_at": generated_at,
                "source_type": "public_eastmoney_index_history",
                "benchmark_ids": sorted(fetched["benchmark_id"].unique().tolist()),
                "rows": int(len(fetched)),
                "source_attempts": source_attempts,
            },
        )
        return fetched, _source_metadata("public_eastmoney_index_history", cache_paths["index_price_history_panel"], source_attempts)

    if config.allow_placeholder_benchmarks:
        placeholders = _placeholder_index_prices(config, generated_at)
        return placeholders, _source_metadata("placeholder_allowed", None, source_attempts)
    return pd.DataFrame(), _source_metadata("missing", None, source_attempts)


def fetch_eastmoney_index_history(*, config: BenchmarkConfig, generated_at: str) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    begin = _begin_date(config.as_of_date, config.lookback_trading_days)
    end = config.as_of_date.replace("-", "")
    for benchmark_id in INDEX_BENCHMARK_IDS:
        secid = EASTMONEY_SECID_MAP[benchmark_id]
        url = (
            "https://push2his.eastmoney.com/api/qt/stock/kline/get"
            f"?secid={secid}&fields1=f1,f2,f3,f4,f5,f6"
            "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
            f"&klt=101&fqt=1&beg={begin}&end={end}"
        )
        try:
            payload = _read_json_url(url)
            klines = payload.get("data", {}).get("klines") or []
            attempts.append({"benchmark_id": benchmark_id, "provider": "eastmoney_public_http", "succeeded": bool(klines), "rows": len(klines)})
            for line in klines:
                parts = str(line).split(",")
                if len(parts) < 7:
                    continue
                day, open_, close, high, low, volume, amount = parts[:7]
                if day > config.as_of_date:
                    continue
                rows.append(
                    {
                        "date": day,
                        "benchmark_id": benchmark_id,
                        "symbol_or_index_code": INDEX_CODE_MAP[benchmark_id][0],
                        "open": _float(open_),
                        "high": _float(high),
                        "low": _float(low),
                        "close": _float(close),
                        "volume": _float(volume),
                        "amount": _float(amount),
                        "source_type": "public_eastmoney_index_history",
                        "source_path": "https://push2his.eastmoney.com/api/qt/stock/kline/get",
                        "source_timestamp": generated_at,
                        "is_placeholder": False,
                    }
                )
        except Exception as exc:  # pragma: no cover - exercised through missing-provider tests by monkeypatching
            attempts.append({"benchmark_id": benchmark_id, "provider": "eastmoney_public_http", "succeeded": False, "rows": 0, "error": str(exc)[:200]})
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, attempts
    return _tail_by_benchmark(frame, config.lookback_trading_days + 1), attempts


def availability_from_index_prices(frame: pd.DataFrame, *, config: BenchmarkConfig, source_meta: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for benchmark_id in INDEX_BENCHMARK_IDS:
        subset = frame[frame["benchmark_id"].astype(str) == benchmark_id] if not frame.empty and "benchmark_id" in frame.columns else pd.DataFrame()
        is_placeholder = bool(subset["is_placeholder"].any()) if not subset.empty and "is_placeholder" in subset.columns else False
        trading_days = int(subset["date"].nunique()) if not subset.empty else 0
        as_of_available = bool((subset["date"].astype(str) == config.as_of_date).any()) if not subset.empty else False
        enough = trading_days >= config.minimum_required_trading_days and as_of_available
        if is_placeholder and config.allow_placeholder_benchmarks:
            status = "placeholder_allowed"
        elif enough:
            status = "available"
        elif not subset.empty:
            status = "failed"
        else:
            status = "missing"
        records.append(
            {
                "benchmark_id": benchmark_id,
                "status": status,
                "source_type": source_meta.get("source_type") if not is_placeholder else "placeholder_allowed",
                "source_path": source_meta.get("source_path"),
                "symbol_or_index_code": INDEX_CODE_MAP[benchmark_id][0],
                "first_available_date": str(subset["date"].min()) if not subset.empty else "",
                "last_available_date": str(subset["date"].max()) if not subset.empty else "",
                "as_of_date_available": as_of_available,
                "trading_days_available": trading_days,
                "missing_reason": None if status in {"available", "placeholder_allowed"} else "index benchmark price history unavailable or insufficient",
                "is_placeholder": is_placeholder,
            }
        )
    return records


def _load_local_index_panel(paths: ProjectPaths, config: BenchmarkConfig) -> pd.DataFrame:
    frames = []
    for path in candidate_index_panel_paths(paths):
        frame = _normalize_local_index_panel(path, config, paths)
        if not frame.empty:
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(["date", "benchmark_id"]).sort_values(["benchmark_id", "date"])
    return _tail_by_benchmark(combined, config.lookback_trading_days + 1)


def _normalize_local_index_panel(path: Path, config: BenchmarkConfig, paths: ProjectPaths) -> pd.DataFrame:
    frame = read_frame(path)
    if frame.empty or "date" not in frame.columns:
        return pd.DataFrame()
    code_column = "benchmark_id" if "benchmark_id" in frame.columns else "symbol" if "symbol" in frame.columns else "index_code" if "index_code" in frame.columns else ""
    close_column = "close" if "close" in frame.columns else "adj_close" if "adj_close" in frame.columns else ""
    if not code_column or not close_column:
        return pd.DataFrame()
    records = []
    code_to_benchmark = {code: benchmark for benchmark, codes in INDEX_CODE_MAP.items() for code in codes}
    for _, row in frame.iterrows():
        code = str(row.get(code_column))
        benchmark_id = code if code in INDEX_BENCHMARK_IDS else code_to_benchmark.get(code)
        if benchmark_id not in INDEX_BENCHMARK_IDS:
            continue
        day = str(row.get("date"))
        if day > config.as_of_date:
            continue
        records.append(
            {
                "date": day,
                "benchmark_id": benchmark_id,
                "symbol_or_index_code": INDEX_CODE_MAP[benchmark_id][0],
                "open": _float(row.get("open", row.get(close_column))),
                "high": _float(row.get("high", row.get(close_column))),
                "low": _float(row.get("low", row.get(close_column))),
                "close": _float(row.get(close_column)),
                "volume": _float(row.get("volume")),
                "amount": _float(row.get("amount")),
                "source_type": "local_index_price_panel",
                "source_path": relative(path, paths.project_root),
                "source_timestamp": str(row.get("source_timestamp") or row.get("ingested_at") or ""),
                "is_placeholder": False,
            }
        )
    return pd.DataFrame(records)


def _placeholder_index_prices(config: BenchmarkConfig, generated_at: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": config.as_of_date,
                "benchmark_id": benchmark_id,
                "symbol_or_index_code": INDEX_CODE_MAP[benchmark_id][0],
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 1.0,
                "volume": 0.0,
                "amount": 0.0,
                "source_type": "placeholder_allowed",
                "source_path": None,
                "source_timestamp": generated_at,
                "is_placeholder": True,
            }
            for benchmark_id in INDEX_BENCHMARK_IDS
        ]
    )


def _read_json_url(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _source_metadata(source_type: str, source_path: Path | None, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return json_safe(
        {
            "source_type": source_type,
            "source_path": str(source_path) if source_path else None,
            "source_attempts": attempts,
        }
    )


def _local_source_path(paths: ProjectPaths) -> Path | None:
    for path in candidate_index_panel_paths(paths):
        if path.exists():
            return path
    return None


def _has_all_index_benchmarks(frame: pd.DataFrame, config: BenchmarkConfig) -> bool:
    if frame.empty or "benchmark_id" not in frame.columns:
        return False
    available = set(frame["benchmark_id"].astype(str).unique())
    if not set(INDEX_BENCHMARK_IDS).issubset(available):
        return False
    for benchmark_id in INDEX_BENCHMARK_IDS:
        subset = frame[frame["benchmark_id"].astype(str) == benchmark_id]
        if subset["date"].nunique() < config.minimum_required_trading_days:
            return False
        if not (subset["date"].astype(str) == config.as_of_date).any():
            return False
    return True


def _tail_by_benchmark(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    frame = frame.dropna(subset=["date", "benchmark_id", "close"]).copy()
    frame["date"] = frame["date"].astype(str)
    frame = frame.sort_values(["benchmark_id", "date"])
    return frame.groupby("benchmark_id", group_keys=False).tail(count).reset_index(drop=True)


def _begin_date(as_of_date: str, lookback_trading_days: int) -> str:
    start = date.fromisoformat(as_of_date) - timedelta(days=max(lookback_trading_days * 3, 90))
    return start.strftime("%Y%m%d")


def _float(value: Any) -> float | None:
    try:
        if value in (None, "", "-"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
