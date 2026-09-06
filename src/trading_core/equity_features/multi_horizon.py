"""Build A-share multi-horizon feature artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import cast, Any

import numpy as np
import pandas as pd

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_features.feature_config import (
    COMMON_COLUMNS,
    FEATURE_BOUNDARY,
    FEATURE_GROUP_FIELDS,
    TARGET_VERSION,
)
from trading_core.equity_features.feature_inputs import feature_data_dir, load_feature_inputs
from trading_core.equity_features.feature_manifest import build_field_coverage_payload, feature_group_metadata
from trading_core.equity_features.feature_report import write_feature_reports
from trading_core.equity_features.fundamental import build_fundamental_row, latest_daily_basic
from trading_core.equity_features.industry import build_industry_return_map, industry_key, latest_industry_by_symbol
from trading_core.equity_features.liquidity import avg, effective_days, slippage_proxy, stability, zero_days
from trading_core.equity_features.momentum import momentum
from trading_core.equity_features.moving_average import close_to_average, last_value, moving_average, moving_average_slope, trend_consistency
from trading_core.equity_features.returns import annualized_return, pct_return, safe_number
from trading_core.equity_features.risk import calmar_250d, downside_volatility, expected_shortfall, kurtosis, max_drawdown, skewness, value_at_risk, volatility
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


FEATURE_FILES = {
    "short_horizon": "short_horizon_features.parquet",
    "mid_horizon": "mid_horizon_features.parquet",
    "long_horizon": "long_horizon_features.parquet",
    "risk": "risk_features.parquet",
    "liquidity": "liquidity_features.parquet",
    "industry": "industry_features.parquet",
    "fundamental": "fundamental_features.parquet",
}


def build_a_share_multi_horizon_features(
    *,
    as_of_date: str = "2026-06-26",
    allow_latest_tradable_universe: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    inputs = load_feature_inputs(paths=paths, as_of_date=as_of_date, allow_latest_tradable_universe=allow_latest_tradable_universe)
    out_dir = feature_data_dir(paths, inputs.as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    base = _base_frame(inputs.strict_universe, inputs.as_of_date, created_at)
    strict_symbols = set(base["symbol"])
    price = _price_panel(inputs.price_history, inputs.adjusted_price_history, strict_symbols)
    grouped_price: dict[str, pd.DataFrame] = {str(symbol): frame.sort_values("date") for symbol, frame in price.groupby("symbol", sort=False)}
    industry_map = latest_industry_by_symbol(inputs.industry_classification, inputs.as_of_date)
    return_frame = _return_frame(grouped_price)
    market_returns = _market_returns(return_frame)
    industry_returns = build_industry_return_map(return_frame, industry_map)
    return_frame = _attach_industry_rank_inputs(return_frame, industry_map)
    industry_rank_maps = _industry_rank_maps(return_frame)
    basic_rows = latest_daily_basic(inputs.daily_basic_history, inputs.daily_basic_snapshot, inputs.as_of_date)
    # dict(groupby) is not equivalent: GroupBy.keys() makes dict() treat it as a mapping.
    financial_groups: dict[str, pd.DataFrame] = {str(symbol): frame for symbol, frame in inputs.financial_history.groupby("symbol", sort=False)} if not inputs.financial_history.empty else {}  # noqa: C416

    frames = {
        "short_horizon": _short_features(base, grouped_price),
        "mid_horizon": _mid_features(base, grouped_price, market_returns, industry_returns, industry_map),
        "long_horizon": _long_features(base, grouped_price, market_returns, industry_returns, industry_map),
        "risk": _risk_features(base, grouped_price),
        "liquidity": _liquidity_features(base, grouped_price),
        "industry": _industry_features(base, return_frame, market_returns, industry_returns, industry_map, industry_rank_maps),
        "fundamental": _fundamental_features(base, basic_rows, financial_groups, inputs.as_of_date),
    }
    artifact_paths = {group: out_dir / filename for group, filename in FEATURE_FILES.items()}
    for group, frame in frames.items():
        _write_parquet(frame, artifact_paths[group])
    coverage = build_field_coverage_payload(frames, len(base), inputs.as_of_date)
    coverage_path = out_dir / "feature_field_coverage.json"
    write_json(coverage_path, coverage)
    manifest = _manifest(paths, inputs, artifact_paths, coverage_path, len(base), created_at)
    manifest_path = out_dir / "feature_manifest.json"
    write_json(manifest_path, manifest)
    summary = _summary(paths, inputs, artifact_paths, len(base), coverage, created_at)
    summary_path = out_dir / "feature_generation_summary.json"
    write_json(summary_path, summary)
    reports = write_feature_reports(paths, inputs.as_of_date, summary, coverage)
    payload = {
        "builder_id": "A-SHARE-MULTI-HORIZON-FEATURE-BUILDER",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "strict_tradable_count": len(base),
        "feature_groups": summary["feature_groups"],
        "feature_manifest_path": str(manifest_path),
        "feature_field_coverage_path": str(coverage_path),
        "feature_generation_summary_path": str(summary_path),
        "reports": reports,
        "warnings": summary["warnings"],
        "boundary": dict(FEATURE_BOUNDARY),
    }
    return json_safe(payload)


def _price_panel(price: pd.DataFrame, adjusted: pd.DataFrame, symbols: set[str]) -> pd.DataFrame:
    columns = ["date", "symbol", "open", "high", "low", "close", "volume", "amount", "turnover", "pre_close", "pct_change", "source"]
    frame = price[[column for column in columns if column in price.columns]].copy()
    frame = frame[frame["symbol"].isin(symbols)].copy()
    if not adjusted.empty and {"date", "symbol", "adj_close"}.issubset(adjusted.columns):
        adj = adjusted[["date", "symbol", "adj_close"]].copy()
        frame = frame.merge(adj, on=["date", "symbol"], how="left")
    else:
        frame["adj_close"] = np.nan
    frame["feature_close"] = frame["adj_close"].combine_first(frame["close"])
    frame["effective_amount"] = frame["amount"].where(frame["amount"].notna(), frame["volume"] * frame["close"])
    for column in ["feature_close", "open", "high", "low", "close", "volume", "effective_amount", "turnover", "pre_close", "pct_change"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values(["symbol", "date"])


def _base_frame(strict: pd.DataFrame, as_of_date: str, created_at: str) -> pd.DataFrame:
    required = ["symbol", "name", "exchange", "board", "industry_level_1", "industry_level_2"]
    base = strict[required].drop_duplicates("symbol").sort_values("symbol").copy()
    base["as_of_date"] = as_of_date
    base["source"] = "strict_tradable_universe+historical_feature_inputs"
    base["created_at"] = created_at
    return base


def _common(row: pd.Series, feature_group: str) -> dict[str, Any]:
    return {
        "as_of_date": row["as_of_date"],
        "symbol": row["symbol"],
        "name": row.get("name", ""),
        "exchange": row.get("exchange", ""),
        "board": row.get("board", ""),
        "industry_level_1": row.get("industry_level_1", ""),
        "industry_level_2": row.get("industry_level_2", ""),
        "feature_group": feature_group,
        "source": row.get("source", ""),
        "created_at": row.get("created_at", ""),
    }


def _series(frame: pd.DataFrame, column: str) -> np.ndarray:
    if frame.empty or column not in frame.columns:
        return np.array([], dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)


def _short_features(base: pd.DataFrame, grouped: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        frame = grouped.get(row["symbol"], pd.DataFrame())
        close = _series(frame, "feature_close")
        raw_close = _series(frame, "close")
        high = _series(frame, "high")
        low = _series(frame, "low")
        open_ = _series(frame, "open")
        volume = _series(frame, "volume")
        amount = _series(frame, "effective_amount")
        last_close = last_value(close)
        high20 = _window_max(high, 20)
        low20 = _window_min(low, 20)
        result = {
            **_common(row, "short_horizon"),
            "return_1d": pct_return(close, 1),
            "return_3d": pct_return(close, 3),
            "return_5d": pct_return(close, 5),
            "return_10d": pct_return(close, 10),
            "return_20d": pct_return(close, 20),
            "momentum_5d": momentum(close, 5),
            "momentum_10d": momentum(close, 10),
            "momentum_20d": momentum(close, 20),
            "volume_change_5d": _change(volume, 5),
            "amount_change_5d": _change(amount, 5),
            "amount_change_20d": _change(amount, 20),
            "close_to_20d_high": _ratio_minus_one(last_close, high20),
            "close_to_20d_low": _ratio_minus_one(last_close, low20),
            "breakout_20d_high": bool(last_close is not None and high20 is not None and last_close >= high20),
            "drawdown_from_20d_high": _ratio_minus_one(last_close, high20),
            "reversal_from_20d_low": _ratio_minus_one(last_close, low20),
            "gap_1d": _gap(open_, raw_close),
            "intraday_range_1d": _intraday_range(high, low, raw_close),
            "amplitude_5d": _amplitude(high, low, raw_close, 5),
            "amplitude_20d": _amplitude(high, low, raw_close, 20),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("short_horizon"))


def _mid_features(base: pd.DataFrame, grouped: dict[str, pd.DataFrame], market: dict[str, float], industry_returns: dict[str, dict[str, float | None]], industry_map: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        frame = grouped.get(row["symbol"], pd.DataFrame())
        close = _series(frame, "feature_close")
        last_close = last_value(close)
        key = industry_key(industry_map.get(row["symbol"], cast(dict[str, Any], row.to_dict())))
        ret60 = pct_return(close, 60)
        ret120 = pct_return(close, 120)
        vol60 = volatility(close, 60)
        vol120 = volatility(close, 120)
        result = {
            **_common(row, "mid_horizon"),
            "return_20d": pct_return(close, 20),
            "return_60d": ret60,
            "return_120d": ret120,
            "momentum_60d": momentum(close, 60),
            "momentum_120d": momentum(close, 120),
            "ma_20": moving_average(close, 20),
            "ma_60": moving_average(close, 60),
            "ma_120": moving_average(close, 120),
            "close_to_ma_20": close_to_average(last_close, moving_average(close, 20)),
            "close_to_ma_60": close_to_average(last_close, moving_average(close, 60)),
            "close_to_ma_120": close_to_average(last_close, moving_average(close, 120)),
            "ma_20_slope": moving_average_slope(close, 20),
            "ma_60_slope": moving_average_slope(close, 60),
            "ma_120_slope": moving_average_slope(close, 120),
            "trend_consistency_60d": trend_consistency(close, 60),
            "trend_consistency_120d": trend_consistency(close, 120),
            "relative_strength_60d_vs_market": _diff(ret60, market.get("return_60d")),
            "relative_strength_120d_vs_market": _diff(ret120, market.get("return_120d")),
            "relative_strength_60d_vs_industry": _diff(ret60, industry_returns.get(key, {}).get("return_60d")),
            "relative_strength_120d_vs_industry": _diff(ret120, industry_returns.get(key, {}).get("return_120d")),
            "volatility_adjusted_return_60d": _divide(ret60, vol60),
            "volatility_adjusted_return_120d": _divide(ret120, vol120),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("mid_horizon"))


def _long_features(base: pd.DataFrame, grouped: dict[str, pd.DataFrame], market: dict[str, float], industry_returns: dict[str, dict[str, float | None]], industry_map: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        frame = grouped.get(row["symbol"], pd.DataFrame())
        close = _series(frame, "feature_close")
        last_close = last_value(close)
        key = industry_key(industry_map.get(row["symbol"], cast(dict[str, Any], row.to_dict())))
        ret250 = pct_return(close, 250)
        ret3y = pct_return(close, 700)
        result = {
            **_common(row, "long_horizon"),
            "return_250d": ret250,
            "return_3y": ret3y,
            "return_5y": pct_return(close, 1100),
            "ma_250": moving_average(close, 250),
            "close_to_ma_250": close_to_average(last_close, moving_average(close, 250)),
            "ma_250_slope": moving_average_slope(close, 250),
            "max_drawdown_250d": max_drawdown(close, 250),
            "max_drawdown_3y": max_drawdown(close, 700),
            "annualized_return_250d": annualized_return(ret250, 250),
            "annualized_volatility_250d": volatility(close, 250, annualize=True),
            "calmar_250d": calmar_250d(close),
            "relative_strength_250d_vs_market": _diff(ret250, market.get("return_250d")),
            "relative_strength_250d_vs_industry": _diff(ret250, industry_returns.get(key, {}).get("return_250d")),
            "long_trend_consistency_250d": trend_consistency(close, 250),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("long_horizon"))


def _risk_features(base: pd.DataFrame, grouped: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        frame = grouped.get(row["symbol"], pd.DataFrame())
        close = _series(frame, "feature_close")
        pct_change = _series(frame, "pct_change")
        open_ = _series(frame, "open")
        raw_close = _series(frame, "close")
        result = {
            **_common(row, "risk"),
            "volatility_20d": volatility(close, 20),
            "volatility_60d": volatility(close, 60),
            "volatility_120d": volatility(close, 120),
            "volatility_250d": volatility(close, 250),
            "downside_volatility_60d": downside_volatility(close, 60),
            "downside_volatility_120d": downside_volatility(close, 120),
            "max_drawdown_20d": max_drawdown(close, 20),
            "max_drawdown_60d": max_drawdown(close, 60),
            "max_drawdown_120d": max_drawdown(close, 120),
            "max_drawdown_250d": max_drawdown(close, 250),
            "var_95_20d": value_at_risk(close, 20),
            "var_95_60d": value_at_risk(close, 60),
            "expected_shortfall_95_60d": expected_shortfall(close, 60),
            "skewness_60d": skewness(close, 60),
            "kurtosis_60d": kurtosis(close, 60),
            "limit_up_days_60d": _count_condition(pct_change, 60, lambda data: data >= 9.8),
            "limit_down_days_60d": _count_condition(pct_change, 60, lambda data: data <= -9.8),
            "large_drop_days_60d": _count_condition(pct_change, 60, lambda data: data <= -5.0),
            "large_gap_days_60d": _large_gap_days(open_, raw_close, 60),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("risk"))


def _liquidity_features(base: pd.DataFrame, grouped: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        frame = grouped.get(row["symbol"], pd.DataFrame())
        amount = _series(frame, "effective_amount")
        volume = _series(frame, "volume")
        turnover = _series(frame, "turnover")
        result = {
            **_common(row, "liquidity"),
            "avg_amount_5d": avg(amount, 5),
            "avg_amount_20d": avg(amount, 20),
            "avg_amount_60d": avg(amount, 60),
            "avg_volume_20d": avg(volume, 20),
            "avg_volume_60d": avg(volume, 60),
            "turnover_rate_20d_avg": avg(turnover, 20),
            "turnover_rate_60d_avg": avg(turnover, 60),
            "amount_stability_20d": stability(amount, 20),
            "amount_stability_60d": stability(amount, 60),
            "zero_volume_days_60d": zero_days(volume, 60),
            "effective_trading_days_20d": effective_days(volume, 20),
            "effective_trading_days_60d": effective_days(volume, 60),
            "estimated_slippage_proxy_20d": slippage_proxy(amount, 20),
            "estimated_slippage_proxy_60d": slippage_proxy(amount, 60),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("liquidity"))


def _industry_features(
    base: pd.DataFrame,
    return_frame: pd.DataFrame,
    market: dict[str, float],
    industry_returns: dict[str, dict[str, float | None]],
    industry_map: dict[str, dict[str, Any]],
    rank_maps: dict[str, dict[str, dict[str, float | None]]],
) -> pd.DataFrame:
    return_lookup = return_frame.set_index("symbol").to_dict(orient="index") if not return_frame.empty else {}
    rows = []
    for _, row in base.iterrows():
        symbol = row["symbol"]
        item = industry_map.get(symbol, cast(dict[str, Any], row.to_dict()))
        key = industry_key(item)
        _symbol_returns = return_lookup.get(symbol, {})
        result = {
            **_common(row, "industry"),
            "industry_level_1": item.get("industry_level_1") or row.get("industry_level_1", ""),
            "industry_level_2": item.get("industry_level_2") or row.get("industry_level_2", ""),
            "industry_return_5d": industry_returns.get(key, {}).get("return_5d"),
            "industry_return_20d": industry_returns.get(key, {}).get("return_20d"),
            "industry_return_60d": industry_returns.get(key, {}).get("return_60d"),
            "industry_return_120d": industry_returns.get(key, {}).get("return_120d"),
            "industry_return_250d": industry_returns.get(key, {}).get("return_250d"),
            "industry_relative_strength_20d": _diff(industry_returns.get(key, {}).get("return_20d"), market.get("return_20d")),
            "industry_relative_strength_60d": _diff(industry_returns.get(key, {}).get("return_60d"), market.get("return_60d")),
            "industry_relative_strength_120d": _diff(industry_returns.get(key, {}).get("return_120d"), market.get("return_120d")),
            "industry_relative_strength_250d": _diff(industry_returns.get(key, {}).get("return_250d"), market.get("return_250d")),
            "stock_rank_in_industry_by_return_20d": rank_maps.get("return_20d", {}).get(symbol, {}).get("rank"),
            "stock_rank_in_industry_by_return_60d": rank_maps.get("return_60d", {}).get(symbol, {}).get("rank"),
            "stock_rank_in_industry_by_return_120d": rank_maps.get("return_120d", {}).get(symbol, {}).get("rank"),
            "stock_percentile_in_industry_by_return_20d": rank_maps.get("return_20d", {}).get(symbol, {}).get("percentile"),
            "stock_percentile_in_industry_by_return_60d": rank_maps.get("return_60d", {}).get(symbol, {}).get("percentile"),
            "stock_percentile_in_industry_by_return_120d": rank_maps.get("return_120d", {}).get(symbol, {}).get("percentile"),
            "industry_member_count": rank_maps.get("return_20d", {}).get(symbol, {}).get("member_count"),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("industry"))


def _fundamental_features(base: pd.DataFrame, basic_rows: dict[str, dict[str, Any]], financial_groups: dict[str, pd.DataFrame], as_of_date: str) -> pd.DataFrame:
    rows = []
    for _, row in base.iterrows():
        symbol = row["symbol"]
        result = {
            **_common(row, "fundamental"),
            **build_fundamental_row(symbol, basic_rows.get(symbol, {}), financial_groups.get(symbol, pd.DataFrame()), as_of_date),
        }
        rows.append(result)
    return pd.DataFrame(rows, columns=_group_columns("fundamental"))


def _group_columns(group: str) -> list[str]:
    common = list(COMMON_COLUMNS)
    return [*common, *[field for field in FEATURE_GROUP_FIELDS[group] if field not in common]]


def _return_frame(grouped: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for symbol, frame in grouped.items():
        close = _series(frame, "feature_close")
        rows.append(
            {
                "symbol": symbol,
                "return_5d": pct_return(close, 5),
                "return_20d": pct_return(close, 20),
                "return_60d": pct_return(close, 60),
                "return_120d": pct_return(close, 120),
                "return_250d": pct_return(close, 250),
            }
        )
    return pd.DataFrame(rows)


def _market_returns(return_frame: pd.DataFrame) -> dict[str, float]:
    return {column: float(return_frame[column].mean()) for column in return_frame.columns if column.startswith("return_") and return_frame[column].notna().any()}


def _attach_industry_rank_inputs(return_frame: pd.DataFrame, industry_map: dict[str, dict[str, Any]]) -> pd.DataFrame:
    frame = return_frame.copy()
    frame["industry_key"] = frame["symbol"].map(lambda symbol: industry_key(industry_map.get(symbol, {})))
    return frame


def _industry_rank_maps(return_frame: pd.DataFrame) -> dict[str, dict[str, dict[str, float | None]]]:
    result: dict[str, dict[str, dict[str, float | None]]] = {}
    for column in ["return_20d", "return_60d", "return_120d"]:
        column_map: dict[str, dict[str, float | None]] = {}
        for _, group in return_frame.dropna(subset=[column]).groupby("industry_key"):
            ranked = group.sort_values(column, ascending=False).reset_index(drop=True)
            count = len(ranked)
            for position, (_, row) in enumerate(ranked.iterrows(), start=1):
                column_map[row["symbol"]] = {
                    "rank": int(position),
                    "percentile": float(1.0 - (position - 1) / max(count - 1, 1)) if count > 1 else 1.0,
                    "member_count": int(count),
                }
        result[column] = column_map
    return result


def _manifest(paths: ProjectPaths, inputs, artifacts: dict[str, Path], coverage_path: Path, strict_count: int, created_at: str) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-MULTI-HORIZON-FEATURE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "created_at": created_at,
        "input_tradable_universe_path": relative(inputs.tradable_universe_path, paths.project_root),
        "strict_tradable_count": strict_count,
        "feature_groups": feature_group_metadata(paths, artifacts),
        "feature_field_coverage_path": relative(coverage_path, paths.project_root),
        "source_dates": inputs.source_dates,
        "no_future_leakage": _no_future_leakage(inputs.source_dates, inputs.as_of_date),
        "scores_generated": False,
        "candidates_generated": False,
        "watchlist_generated": False,
        "virtual_portfolio_generated": False,
        "boundary": dict(FEATURE_BOUNDARY),
    }


def _summary(paths: ProjectPaths, inputs, artifacts: dict[str, Path], strict_count: int, coverage: dict[str, Any], created_at: str) -> dict[str, Any]:
    warnings = []
    fundamental_coverage = coverage["groups"]["fundamental"]["mandatory_field_coverage"]
    if fundamental_coverage < 0.70:
        warnings.append("fundamental field coverage is partial")
    return {
        "summary_id": "A-SHARE-MULTI-HORIZON-FEATURE-GENERATION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "created_at": created_at,
        "strict_tradable_count": strict_count,
        "feature_groups": feature_group_metadata(paths, artifacts),
        "field_coverage": coverage["groups"],
        "warnings": warnings,
        "boundary": dict(FEATURE_BOUNDARY),
    }


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = frame.replace({np.inf: np.nan, -np.inf: np.nan})
    frame.to_parquet(path, index=False)


def _no_future_leakage(source_dates: dict[str, str], as_of_date: str) -> bool:
    return all(not value or value <= as_of_date for value in source_dates.values())


def _window_max(values: np.ndarray, window: int) -> float | None:
    data = values[-window:] if len(values) >= window else values
    data = data[np.isfinite(data)]
    return float(data.max()) if len(data) else None


def _window_min(values: np.ndarray, window: int) -> float | None:
    data = values[-window:] if len(values) >= window else values
    data = data[np.isfinite(data)]
    return float(data.min()) if len(data) else None


def _change(values: np.ndarray, periods: int) -> float | None:
    return pct_return(values, periods)


def _ratio_minus_one(value: float | None, base: float | None) -> float | None:
    if value is None or base in (None, 0):
        return None
    return value / base - 1.0


def _gap(open_values: np.ndarray, close_values: np.ndarray) -> float | None:
    if len(open_values) == 0 or len(close_values) < 2:
        return None
    return _ratio_minus_one(safe_number(open_values[-1]), safe_number(close_values[-2]))


def _intraday_range(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> float | None:
    if len(high) == 0 or len(low) == 0 or len(close) == 0:
        return None
    close_value = safe_number(close[-1])
    if close_value in (None, 0):
        return None
    high_value = safe_number(high[-1])
    low_value = safe_number(low[-1])
    if high_value is None or low_value is None:
        return None
    return (high_value - low_value) / close_value


def _amplitude(high: np.ndarray, low: np.ndarray, close: np.ndarray, window: int) -> float | None:
    high_value = _window_max(high, window)
    low_value = _window_min(low, window)
    close_value = safe_number(close[-1]) if len(close) else None
    if high_value is None or low_value is None or close_value in (None, 0):
        return None
    return (high_value - low_value) / close_value


def _diff(value: float | None, base: float | None) -> float | None:
    if value is None or base is None:
        return None
    return value - base


def _divide(value: float | None, base: float | None) -> float | None:
    if value is None or base in (None, 0):
        return None
    return value / base


def _count_condition(values: np.ndarray, window: int, condition) -> int:
    data = values[-window:] if len(values) >= window else values
    data = data[np.isfinite(data)]
    return int(condition(data).sum()) if len(data) else 0


def _large_gap_days(open_values: np.ndarray, close_values: np.ndarray, window: int) -> int:
    if len(open_values) < 2 or len(close_values) < 2:
        return 0
    opens = open_values[-window:]
    previous_close = close_values[-window - 1 : -1] if len(close_values) > window else close_values[:-1]
    opens = opens[-len(previous_close) :]
    with np.errstate(divide="ignore", invalid="ignore"):
        gaps = opens / previous_close - 1.0
    gaps = gaps[np.isfinite(gaps)]
    return int((np.abs(gaps) >= 0.03).sum()) if len(gaps) else 0
