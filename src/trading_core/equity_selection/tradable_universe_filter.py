"""Build the v0.7.2 A-share tradable universe filter artifacts."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, normalize_symbol, sha256_file, utc_now, write_json
from trading_core.equity_selection.filter_config import TARGET_VERSION, TRADABLE_UNIVERSE_BOUNDARY, TradableUniverseFilterConfig
from trading_core.equity_selection.filter_inputs import load_tradable_universe_inputs, resolve_as_of_date, selection_data_dir
from trading_core.equity_selection.filter_reasons import (
    BUCKET_CAUTION,
    BUCKET_EXCLUDED,
    BUCKET_STRICT,
    BUCKET_UNKNOWN,
    bucket_for_reasons,
    primary_reason,
    stage_for_reason,
)
from trading_core.equity_selection.filter_report import write_tradable_universe_reports
from trading_core.equity_selection.limit_status_filter import detect_limit_status
from trading_core.equity_selection.listing_age_filter import listing_trading_days
from trading_core.equity_selection.market_cap_filter import latest_market_cap_rows, normalize_market_cap
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_tradable_universe(
    *,
    config: TradableUniverseFilterConfig | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = config or TradableUniverseFilterConfig()
    inputs = load_tradable_universe_inputs(paths=paths)
    resolution = resolve_as_of_date(inputs.trading_calendar, config.as_of_date, allow_previous_trading_day=config.allow_previous_trading_day)
    as_of_date = resolution.as_of_date
    data_dir = selection_data_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)

    master = _prepare_master(inputs.equity_master)
    industry = _latest_by_symbol(inputs.industry_classification, "effective_date", as_of_date)
    price_stats = _price_stats(inputs.daily_price_history, inputs.trading_calendar, as_of_date)
    market_caps, market_cap_snapshot_only = latest_market_cap_rows(inputs.daily_basic_history, inputs.daily_basic_snapshot, as_of_date)
    financial_counts = _row_counts(inputs.basic_financials_history, "report_date")
    rows = []
    created_at = utc_now()
    for item in master.to_dict(orient="records"):
        rows.append(
            _evaluate_symbol(
                item,
                industry.get(item["symbol"], {}),
                price_stats.get(item["symbol"], {}),
                market_caps.get(item["symbol"], {}),
                financial_counts.get(item["symbol"], 0),
                inputs.trading_calendar,
                as_of_date,
                config,
                created_at,
            )
        )

    strict_rows = [row for row in rows if row["bucket"] == BUCKET_STRICT]
    caution_rows = [row for row in rows if row["bucket"] == BUCKET_CAUTION]
    excluded_rows = [_excluded_record(row) for row in rows if row["bucket"] == BUCKET_EXCLUDED]
    unknown_rows = [row for row in rows if row["bucket"] == BUCKET_UNKNOWN]
    tradable_rows = strict_rows + caution_rows if config.include_caution else strict_rows
    reason_breakdown = _reason_breakdown(rows, config, inputs, as_of_date)
    config_payload = {
        **config.to_dict(),
        "requested_as_of_date": resolution.requested_as_of_date,
        "as_of_date": as_of_date,
        "used_previous_trading_day": resolution.used_previous_trading_day,
        "previous_trading_day_reason": resolution.previous_trading_day_reason,
        "daily_basic_history_market_cap_available": _has_market_cap(inputs.daily_basic_history),
        "daily_basic_snapshot_market_cap_fallback_used": bool(market_cap_snapshot_only or not _has_market_cap(inputs.daily_basic_history)),
        "created_at": created_at,
    }
    counts = {
        "equity_master_symbols": int(master["symbol"].nunique()),
        "input_symbols": len(rows),
        "strict_tradable_count": len(strict_rows),
        "caution_count": len(caution_rows),
        "excluded_count": len(excluded_rows),
        "unknown_status_count": len(unknown_rows),
        "tradable_output_count": len(tradable_rows),
    }
    artifacts = _write_artifacts(data_dir, config_payload, tradable_rows, strict_rows, caution_rows, excluded_rows, unknown_rows, reason_breakdown)
    manifest = _manifest(paths, data_dir, artifacts, counts, config_payload, inputs, created_at)
    write_json(data_dir / "tradable_universe_manifest.json", manifest)
    reports = write_tradable_universe_reports(
        paths,
        as_of_date,
        {
            "counts": counts,
            "config": config_payload,
            "reason_breakdown": reason_breakdown,
        },
    )
    payload = {
        "builder_id": "A-SHARE-TRADABLE-UNIVERSE-FILTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "requested_as_of_date": resolution.requested_as_of_date,
        "counts": counts,
        "warnings": _warnings(config_payload, counts),
        "config": config_payload,
        "reason_breakdown": reason_breakdown,
        "artifacts": {**artifacts, "manifest": str(data_dir / "tradable_universe_manifest.json"), **reports},
        "manifest": manifest,
        "boundary": dict(TRADABLE_UNIVERSE_BOUNDARY),
    }
    return json_safe(payload)


def _prepare_master(master: pd.DataFrame) -> pd.DataFrame:
    if master.empty:
        return pd.DataFrame(columns=["symbol", "exchange", "name", "list_date", "delist_date", "board", "is_active", "is_st", "source"])
    frame = master.copy()
    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    return frame.drop_duplicates("symbol").sort_values("symbol")


def _price_stats(price: pd.DataFrame, calendar: pd.DataFrame, as_of_date: str) -> dict[str, dict[str, Any]]:
    if price.empty:
        return {}
    columns = [column for column in ["date", "symbol", "open", "high", "low", "close", "volume", "amount", "pct_change", "source"] if column in price.columns]
    frame = price.loc[:, columns].copy()
    frame["date"] = frame["date"].astype(str)
    frame["symbol"] = frame["symbol"].map(normalize_symbol)
    frame = frame[frame["date"] <= as_of_date].copy()
    if frame.empty:
        return {}
    for column in ["open", "high", "low", "close", "volume", "amount", "pct_change"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    trading_dates = _trading_dates(calendar, as_of_date)
    windows = {
        "20d": set(trading_dates[-20:]),
        "60d": set(trading_dates[-60:]),
    }
    frame["valid_observation"] = frame["close"].notna() & (frame["close"] > 0) & (frame["volume"].isna() | (frame["volume"] >= 0))
    estimated_amount = frame["amount"].isna() & frame["volume"].notna() & frame["close"].notna()
    frame["effective_amount"] = frame["amount"].where(frame["amount"].notna(), frame["volume"] * frame["close"])
    frame["estimated_amount"] = estimated_amount & frame["effective_amount"].notna()
    history_counts = frame.groupby("symbol")["date"].nunique()
    as_of_rows = frame[frame["date"] == as_of_date].sort_values(["symbol", "date"]).drop_duplicates("symbol", keep="last")
    stats: dict[str, dict[str, Any]] = {}
    for symbol, count in history_counts.items():
        stats[symbol] = {
            "history_days": int(count),
            "has_20d_history": int(count) >= 20,
            "has_60d_history": int(count) >= 60,
            "has_120d_history": int(count) >= 120,
            "has_250d_history": int(count) >= 250,
        }
    for label, dates in windows.items():
        subset = frame[frame["date"].isin(dates)]
        grouped = subset.groupby("symbol").agg(
            effective_days=("valid_observation", "sum"),
            avg_amount=("effective_amount", "mean"),
            estimated_amount=("estimated_amount", "any"),
            amount_rows=("effective_amount", "count"),
        )
        for symbol, row in grouped.iterrows():
            stats.setdefault(symbol, {})
            stats[symbol][f"effective_trading_days_{label}"] = int(row["effective_days"])
            stats[symbol][f"avg_amount_{label}"] = _finite_or_none(row["avg_amount"])
            stats[symbol][f"estimated_amount_{label}"] = bool(row["estimated_amount"])
            stats[symbol][f"amount_rows_{label}"] = int(row["amount_rows"])
    for row in as_of_rows.to_dict(orient="records"):
        symbol = row["symbol"]
        stats.setdefault(symbol, {})
        stats[symbol]["as_of_price"] = row
    return stats


def _evaluate_symbol(
    master_row: dict[str, Any],
    industry_row: dict[str, Any],
    price_stat: dict[str, Any],
    market_cap_row: dict[str, Any],
    financial_quarters: int,
    calendar: pd.DataFrame,
    as_of_date: str,
    config: TradableUniverseFilterConfig,
    created_at: str,
) -> dict[str, Any]:
    symbol = normalize_symbol(master_row.get("symbol"))
    exchange = str(master_row.get("exchange") or "")
    board = str(master_row.get("board") or "")
    name = str(master_row.get("name") or "")
    reasons: list[str] = []
    if exchange not in {"SSE", "SZSE", "BSE"}:
        reasons.append("unsupported_exchange")
    active = _bool_or_none(master_row.get("is_active"))
    if active is False:
        reasons.append("inactive")
    list_date = _date_text(master_row.get("list_date"))
    if not list_date:
        reasons.append("missing_list_date")
    elif list_date > as_of_date:
        reasons.append("not_yet_listed")
    delist_date = _date_text(master_row.get("delist_date"))
    if delist_date and delist_date <= as_of_date:
        reasons.append("delisted")
    is_st = _bool_or_none(master_row.get("is_st"))
    name_upper = name.upper().replace(" ", "")
    if is_st is None:
        reasons.append("st_status_unknown")
    if is_st is True:
        reasons.append("st_stock")
    if "ST" in name_upper:
        reasons.append("name_contains_st")
    if "风险" in name or "警示" in name:
        reasons.append("risk_warning_stock")
    if "退" in name:
        reasons.append("delisting_board")
    age = listing_trading_days(list_date, exchange, as_of_date, calendar) if list_date else None
    if age is None:
        reasons.append("listing_age_unknown")
    elif age < config.min_listing_trading_days:
        reasons.append("new_listing_lt_120_trading_days")

    as_of_price = price_stat.get("as_of_price") or {}
    close = _number(as_of_price.get("close"))
    if not as_of_price:
        reasons.append("missing_price_on_as_of_date")
    effective_20d = int(price_stat.get("effective_trading_days_20d") or 0)
    effective_60d = int(price_stat.get("effective_trading_days_60d") or 0)
    if effective_20d < config.min_effective_trading_days_20d:
        reasons.append("insufficient_20d_trading_observations")
    if effective_60d < config.min_effective_trading_days_60d:
        reasons.append("insufficient_60d_trading_observations")
    if "missing_price_on_as_of_date" in reasons or "insufficient_20d_trading_observations" in reasons or "insufficient_60d_trading_observations" in reasons:
        reasons.append("possible_suspension")

    avg_amount_20d = _finite_or_none(price_stat.get("avg_amount_20d"))
    avg_amount_60d = _finite_or_none(price_stat.get("avg_amount_60d"))
    estimated_amount = bool(price_stat.get("estimated_amount_20d") or price_stat.get("estimated_amount_60d"))
    if avg_amount_20d is None and avg_amount_60d is None:
        reasons.append("amount_missing")
    elif avg_amount_20d is None or avg_amount_60d is None:
        reasons.append("liquidity_unknown")
    else:
        if avg_amount_20d < config.min_avg_amount_20d:
            reasons.append("avg_amount_20d_below_threshold")
        if avg_amount_60d < config.min_avg_amount_60d:
            reasons.append("avg_amount_60d_below_threshold")

    total_mv, circ_mv, unit_normalized, unit_unknown = normalize_market_cap(
        market_cap_row.get("total_mv"),
        market_cap_row.get("circ_mv"),
        str(market_cap_row.get("source") or market_cap_row.get("provider") or ""),
    )
    if unit_unknown:
        reasons.append("market_cap_unit_unknown")
    if total_mv is None or circ_mv is None:
        reasons.append("market_cap_missing")
    else:
        if total_mv < config.min_total_mv:
            reasons.append("total_mv_below_threshold")
        if circ_mv < config.min_circ_mv:
            reasons.append("circ_mv_below_threshold")

    if close is None:
        reasons.append("close_price_missing")
    elif close < config.min_close_price:
        reasons.append("close_price_below_threshold")

    reasons.extend(_price_sanity_reasons(as_of_price))
    limit_up, limit_down, limit_unknown = detect_limit_status(as_of_price, board=board, exchange=exchange, is_st=is_st)
    if limit_up:
        reasons.append("one_word_limit_up_risk")
    if limit_down:
        reasons.append("one_word_limit_down_risk")
    if limit_unknown:
        reasons.append("limit_status_unknown")

    if config.require_20d_history and not price_stat.get("has_20d_history"):
        reasons.append("insufficient_20d_history")
    if config.require_60d_history and not price_stat.get("has_60d_history"):
        reasons.append("insufficient_60d_history")
    if config.require_120d_history and not price_stat.get("has_120d_history"):
        reasons.append("insufficient_120d_history")
    if config.require_250d_history and not price_stat.get("has_250d_history"):
        reasons.append("insufficient_250d_history")

    deduped_reasons = list(dict.fromkeys(reasons))
    bucket = bucket_for_reasons(deduped_reasons)
    return {
        "as_of_date": as_of_date,
        "symbol": symbol,
        "name": name,
        "exchange": exchange,
        "board": board,
        "industry_level_1": str(industry_row.get("industry_level_1") or ""),
        "industry_level_2": str(industry_row.get("industry_level_2") or ""),
        "list_date": list_date,
        "listing_trading_days": age,
        "close": close,
        "avg_amount_20d": avg_amount_20d,
        "avg_amount_60d": avg_amount_60d,
        "total_mv": total_mv,
        "circ_mv": circ_mv,
        "effective_trading_days_20d": effective_20d,
        "effective_trading_days_60d": effective_60d,
        "has_20d_history": bool(price_stat.get("has_20d_history")),
        "has_60d_history": bool(price_stat.get("has_60d_history")),
        "has_120d_history": bool(price_stat.get("has_120d_history")),
        "has_250d_history": bool(price_stat.get("has_250d_history")),
        "history_days": int(price_stat.get("history_days") or 0),
        "financial_quarters": int(financial_quarters),
        "estimated_amount": estimated_amount,
        "market_cap_unit_normalized": unit_normalized,
        "market_cap_source": str(market_cap_row.get("source") or market_cap_row.get("provider") or ""),
        "bucket": bucket,
        "filter_passed": bucket == BUCKET_STRICT,
        "filter_reasons": deduped_reasons,
        "primary_reason": primary_reason(deduped_reasons),
        "failed_filter_stage": stage_for_reason(primary_reason(deduped_reasons)) if deduped_reasons else "",
        "source": _source_text(as_of_price, market_cap_row),
        "created_at": created_at,
    }


def _price_sanity_reasons(row: dict[str, Any]) -> list[str]:
    if not row:
        return []
    reasons = []
    open_ = _number(row.get("open"))
    high = _number(row.get("high"))
    low = _number(row.get("low"))
    close = _number(row.get("close"))
    pct_change = _number(row.get("pct_change"))
    volume = _number(row.get("volume"))
    amount = _number(row.get("amount"))
    prices = [open_, high, low, close]
    if any(value is None or value <= 0 for value in prices):
        reasons.append("invalid_price_record")
    if high is not None and low is not None and high < low:
        reasons.append("invalid_high_low")
    if high is not None and (open_ is not None and high < open_ or close is not None and high < close):
        reasons.append("invalid_high_low")
    if low is not None and (open_ is not None and low > open_ or close is not None and low > close):
        reasons.append("invalid_high_low")
    if pct_change is None or not math.isfinite(pct_change):
        reasons.append("invalid_price_record")
    if volume is not None and volume < 0:
        reasons.append("invalid_volume")
    if amount is not None and amount < 0:
        reasons.append("invalid_amount")
    return reasons


def _excluded_record(row: dict[str, Any]) -> dict[str, Any]:
    reasons = row["filter_reasons"]
    return {
        "as_of_date": row["as_of_date"],
        "symbol": row["symbol"],
        "name": row["name"],
        "exchange": row["exchange"],
        "board": row["board"],
        "bucket": BUCKET_EXCLUDED,
        "filter_passed": False,
        "primary_exclusion_reason": row["primary_reason"],
        "all_exclusion_reasons": reasons,
        "failed_filter_stage": row["failed_filter_stage"],
        "source": row["source"],
        "created_at": row["created_at"],
    }


def _write_artifacts(
    data_dir,
    config_payload: dict[str, Any],
    tradable_rows: list[dict[str, Any]],
    strict_rows: list[dict[str, Any]],
    caution_rows: list[dict[str, Any]],
    excluded_rows: list[dict[str, Any]],
    unknown_rows: list[dict[str, Any]],
    reason_breakdown: dict[str, Any],
) -> dict[str, str]:
    artifacts = {
        "filter_config": data_dir / "filter_config.json",
        "tradable_universe_json": data_dir / "tradable_universe.json",
        "tradable_universe_parquet": data_dir / "tradable_universe.parquet",
        "strict_tradable_universe_json": data_dir / "strict_tradable_universe.json",
        "caution_universe": data_dir / "caution_universe.json",
        "excluded_universe": data_dir / "excluded_universe.json",
        "unknown_status_universe": data_dir / "unknown_status_universe.json",
        "filter_reason_breakdown": data_dir / "filter_reason_breakdown.json",
    }
    _write_json_any(artifacts["filter_config"], config_payload)
    _write_json_any(artifacts["tradable_universe_json"], tradable_rows)
    _write_json_any(artifacts["strict_tradable_universe_json"], strict_rows)
    pd.DataFrame(tradable_rows).to_parquet(artifacts["tradable_universe_parquet"], index=False)
    _write_json_any(artifacts["caution_universe"], caution_rows)
    _write_json_any(artifacts["excluded_universe"], excluded_rows)
    _write_json_any(artifacts["unknown_status_universe"], unknown_rows)
    _write_json_any(artifacts["filter_reason_breakdown"], reason_breakdown)
    return {key: str(path) for key, path in artifacts.items()}


def _reason_breakdown(rows: list[dict[str, Any]], config: TradableUniverseFilterConfig, inputs, as_of_date: str) -> dict[str, Any]:
    reason_counts: Counter[str] = Counter()
    stage_counts: Counter[str] = Counter()
    for row in rows:
        for reason in row["filter_reasons"]:
            reason_counts[reason] += 1
        if row["failed_filter_stage"]:
            stage_counts[row["failed_filter_stage"]] += 1
    strict = sum(1 for row in rows if row["bucket"] == BUCKET_STRICT)
    caution = sum(1 for row in rows if row["bucket"] == BUCKET_CAUTION)
    excluded = sum(1 for row in rows if row["bucket"] == BUCKET_EXCLUDED)
    unknown = sum(1 for row in rows if row["bucket"] == BUCKET_UNKNOWN)
    return {
        "as_of_date": as_of_date,
        "equity_master_symbols": int(inputs.equity_master["symbol"].nunique()) if not inputs.equity_master.empty else 0,
        "input_symbols": len(rows),
        "strict_tradable_count": strict,
        "caution_count": caution,
        "excluded_count": excluded,
        "unknown_status_count": unknown,
        "reason_counts": dict(reason_counts),
        "stage_counts": dict(stage_counts),
        "thresholds": config.thresholds(),
    }


def _manifest(paths: ProjectPaths, data_dir, artifacts: dict[str, str], counts: dict[str, Any], config_payload: dict[str, Any], inputs, created_at: str) -> dict[str, Any]:
    source_artifacts = {
        "equity_master": paths.data_dir / "equity_universe" / "equity_master.parquet",
        "trading_calendar": paths.data_dir / "equity_universe" / "trading_calendar.parquet",
        "daily_price_history_panel": paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet",
        "adjusted_price_history_panel": paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet",
        "daily_basic_history_panel": paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet",
        "daily_basic_panel": paths.data_dir / "equity_market" / "daily_basic_panel.parquet",
        "industry_classification": paths.data_dir / "equity_industry" / "industry_classification.parquet",
        "basic_financials_history_panel": paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet",
        "historical_backfill_symbol_manifest": paths.data_dir / "equity_data_quality" / "a_share_historical_backfill_symbol_manifest.json",
        "coverage_audit": paths.data_dir / "equity_data_quality" / "a_share_historical_panel_coverage_audit.json",
        "readiness_audit": paths.data_dir / "equity_data_quality" / "a_share_feature_readiness_audit.json",
    }
    return {
        "manifest_id": "A-SHARE-TRADABLE-UNIVERSE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": config_payload["as_of_date"],
        "created_at": created_at,
        "counts": counts,
        "config_path": relative(data_dir / "filter_config.json", paths.project_root),
        "artifacts": {key: relative(Path(value), paths.project_root) for key, value in artifacts.items()},
        "artifact_hashes": {key: sha256_file(Path(value)) for key, value in artifacts.items()},
        "source_artifacts": {
            key: {
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "sha256": sha256_file(path),
            }
            for key, path in source_artifacts.items()
        },
        "input_data_from_v0_7_1_2": bool(
            inputs.coverage_audit.get("target_version") == "v0.7.1.2-a-share-historical-data-provider-expansion"
            and inputs.readiness_audit.get("target_version") == "v0.7.1.2-a-share-historical-data-provider-expansion"
        ),
        "daily_basic_snapshot_market_cap_fallback_used": config_payload["daily_basic_snapshot_market_cap_fallback_used"],
        "boundary": dict(TRADABLE_UNIVERSE_BOUNDARY),
    }


def _latest_by_symbol(frame: pd.DataFrame, date_column: str, as_of_date: str) -> dict[str, dict[str, Any]]:
    if frame.empty or "symbol" not in frame.columns:
        return {}
    data = frame.copy()
    data["symbol"] = data["symbol"].map(normalize_symbol)
    if date_column in data.columns:
        data = data[data[date_column].astype(str) <= as_of_date]
        data = data.sort_values(["symbol", date_column])
    return {row["symbol"]: row for row in data.drop_duplicates("symbol", keep="last").to_dict(orient="records")}


def _row_counts(frame: pd.DataFrame, date_column: str) -> dict[str, int]:
    if frame.empty or "symbol" not in frame.columns or date_column not in frame.columns:
        return {}
    data = frame.copy()
    data["symbol"] = data["symbol"].map(normalize_symbol)
    return {symbol: int(count) for symbol, count in data.groupby("symbol")[date_column].nunique().items()}


def _trading_dates(calendar: pd.DataFrame, as_of_date: str) -> list[str]:
    if calendar.empty:
        return []
    cal = calendar.copy()
    if "is_trading_day" in cal.columns:
        cal = cal[cal["is_trading_day"].fillna(False).astype(bool)]
    return sorted(set(cal.loc[cal["date"].astype(str) <= as_of_date, "date"].astype(str)))


def _has_market_cap(frame: pd.DataFrame) -> bool:
    return not frame.empty and "total_mv" in frame.columns and "circ_mv" in frame.columns and bool((frame["total_mv"].notna() | frame["circ_mv"].notna()).any())


def _warnings(config_payload: dict[str, Any], counts: dict[str, Any]) -> list[str]:
    warnings = []
    if config_payload["daily_basic_snapshot_market_cap_fallback_used"]:
        warnings.append("daily_basic_history market cap fields unavailable; used daily_basic_panel as-of fallback")
    if counts["caution_count"] > 0:
        warnings.append("caution universe contains observation-only symbols")
    if counts["unknown_status_count"] > 0:
        warnings.append("unknown status universe contains symbols with incomplete critical fields")
    return warnings


def _source_text(price_row: dict[str, Any], market_cap_row: dict[str, Any]) -> str:
    sources = ["equity_master", "daily_price_history_panel", "daily_basic_history_panel"]
    if market_cap_row.get("used_daily_basic_snapshot_fallback"):
        sources.append("daily_basic_panel_fallback")
    if price_row.get("source"):
        sources.append(str(price_row["source"]))
    if market_cap_row.get("source"):
        sources.append(str(market_cap_row["source"]))
    return "+".join(dict.fromkeys(sources))


def _bool_or_none(value: Any) -> bool | None:
    if value in (None, "", "-", "--") or pd.isna(value):
        return None
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
    return bool(value)


def _date_text(value: Any) -> str:
    if value in (None, "", "-", "--") or pd.isna(value):
        return ""
    return str(value)[:10]


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--") or pd.isna(value):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _finite_or_none(value: Any) -> float | None:
    number = _number(value)
    return number if number is not None and math.isfinite(number) else None


def _write_json_any(path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, ensure_ascii=False), encoding="utf-8")
