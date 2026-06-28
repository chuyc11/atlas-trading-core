"""Input loading for v0.7.8 A-share virtual portfolio tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_briefings.briefing_config import BRIEFING_FILES
from trading_core.equity_data_quality.common import read_frame
from trading_core.equity_portfolio_tracking.tracking_config import DEFAULT_AS_OF_DATE, PORTFOLIO_KEYS, PORTFOLIO_IDS
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_FILES
from trading_core.equity_scoring.score_config import SCORE_FILES
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class TrackingInputs:
    as_of_date: str
    requested_as_of_date: str
    portfolio_dir: Path
    score_dir: Path
    briefing_dir: Path
    market_history_dir: Path
    universe_dir: Path
    portfolio_construction_config_path: Path
    portfolio_manifest_path: Path
    candidate_manifest_path: Path
    score_manifest_path: Path
    briefing_manifest_path: Path
    daily_price_history_path: Path
    adjusted_price_history_path: Path
    trading_calendar_path: Path
    portfolio_construction_config: dict[str, Any]
    portfolio_manifest: dict[str, Any]
    candidate_manifest: dict[str, Any]
    score_manifest: dict[str, Any]
    briefing_manifest: dict[str, Any]
    briefing: dict[str, Any]
    portfolio_weight_summary: dict[str, Any]
    portfolio_industry_exposure: dict[str, Any]
    portfolio_risk_liquidity_summary: dict[str, Any]
    portfolios: dict[str, list[dict[str, Any]]]
    composite_scores: pd.DataFrame
    horizon_scores: pd.DataFrame
    risk_liquidity_scores: pd.DataFrame
    score_frame: pd.DataFrame
    daily_prices: pd.DataFrame
    adjusted_prices: pd.DataFrame
    trading_calendar: pd.DataFrame
    risk_downgraded_symbols: set[str]
    excluded_symbols: set[str]


def tracking_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date


def tracking_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_portfolio_tracking" / "daily" / as_of_date


def load_tracking_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> TrackingInputs:
    paths = default_paths(paths)
    portfolio_dir = paths.data_dir / "equity_portfolios" / "daily" / as_of_date
    score_dir = paths.data_dir / "equity_scores" / "daily" / as_of_date
    briefing_dir = paths.data_dir / "equity_briefings" / "daily" / as_of_date
    market_history_dir = paths.data_dir / "equity_market" / "history"
    universe_dir = paths.data_dir / "equity_universe"

    direct_required = _direct_required_paths(portfolio_dir, score_dir, briefing_dir, market_history_dir, universe_dir)
    missing = [str(path) for path in direct_required if not path.exists()]
    if missing:
        raise ValueError("tracking inputs missing: " + "; ".join(missing))

    portfolio_manifest_path = portfolio_dir / PORTFOLIO_FILES["portfolio_manifest"]
    portfolio_manifest = _load_dict(portfolio_manifest_path)
    candidate_manifest_path = _resolve_project_path(paths, str(portfolio_manifest.get("input_candidate_manifest_path") or ""))
    score_manifest_path = _resolve_project_path(paths, str(portfolio_manifest.get("input_score_manifest_path") or score_dir / SCORE_FILES["score_manifest"]))
    linked_required = [candidate_manifest_path, score_manifest_path]
    linked_missing = [str(path) for path in linked_required if not path.exists()]
    if linked_missing:
        raise ValueError("tracking linked manifests missing: " + "; ".join(linked_missing))

    portfolios = {
        "long": _load_list(portfolio_dir / PORTFOLIO_FILES["long_virtual_portfolio_json"]),
        "mid": _load_list(portfolio_dir / PORTFOLIO_FILES["mid_virtual_portfolio_json"]),
        "short": _load_list(portfolio_dir / PORTFOLIO_FILES["short_virtual_portfolio_json"]),
    }
    if any(not portfolios[key] for key in PORTFOLIO_KEYS):
        raise ValueError(f"tracking portfolios are missing or empty for as_of_date={as_of_date}")

    symbols = sorted({str(row.get("symbol")) for rows in portfolios.values() for row in rows if row.get("symbol")})
    daily_price_history_path = market_history_dir / "daily_price_history_panel.parquet"
    adjusted_price_history_path = market_history_dir / "adjusted_price_history_panel.parquet"
    return TrackingInputs(
        as_of_date=as_of_date,
        requested_as_of_date=as_of_date,
        portfolio_dir=portfolio_dir,
        score_dir=score_dir,
        briefing_dir=briefing_dir,
        market_history_dir=market_history_dir,
        universe_dir=universe_dir,
        portfolio_construction_config_path=portfolio_dir / PORTFOLIO_FILES["portfolio_construction_config"],
        portfolio_manifest_path=portfolio_manifest_path,
        candidate_manifest_path=candidate_manifest_path,
        score_manifest_path=score_manifest_path,
        briefing_manifest_path=briefing_dir / BRIEFING_FILES["briefing_manifest"],
        daily_price_history_path=daily_price_history_path,
        adjusted_price_history_path=adjusted_price_history_path,
        trading_calendar_path=universe_dir / "trading_calendar.parquet",
        portfolio_construction_config=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_construction_config"]),
        portfolio_manifest=portfolio_manifest,
        candidate_manifest=_load_dict(candidate_manifest_path),
        score_manifest=_load_dict(score_manifest_path),
        briefing_manifest=_load_dict(briefing_dir / BRIEFING_FILES["briefing_manifest"]),
        briefing=_load_dict(briefing_dir / BRIEFING_FILES["daily_stock_selection_briefing"]),
        portfolio_weight_summary=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_weight_summary"]),
        portfolio_industry_exposure=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_industry_exposure"]),
        portfolio_risk_liquidity_summary=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_risk_liquidity_summary"]),
        portfolios=portfolios,
        composite_scores=read_frame(score_dir / SCORE_FILES["composite_scores"]),
        horizon_scores=read_frame(score_dir / SCORE_FILES["horizon_scores"]),
        risk_liquidity_scores=read_frame(score_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"]),
        score_frame=_merge_score_frame(
            read_frame(score_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"]),
            read_frame(score_dir / SCORE_FILES["horizon_scores"]),
            read_frame(score_dir / SCORE_FILES["composite_scores"]),
        ),
        daily_prices=_read_price_slice(daily_price_history_path, as_of_date, symbols),
        adjusted_prices=_read_price_slice(adjusted_price_history_path, as_of_date, symbols),
        trading_calendar=read_frame(universe_dir / "trading_calendar.parquet"),
        risk_downgraded_symbols=_symbols_from_json(paths.data_dir / "equity_selection" / "daily" / as_of_date / "risk_downgraded_candidates.json"),
        excluded_symbols=_symbols_from_json(paths.data_dir / "equity_selection" / "daily" / as_of_date / "excluded_universe.json"),
    )


def _direct_required_paths(
    portfolio_dir: Path,
    score_dir: Path,
    briefing_dir: Path,
    market_history_dir: Path,
    universe_dir: Path,
) -> list[Path]:
    return [
        portfolio_dir / PORTFOLIO_FILES["portfolio_construction_config"],
        portfolio_dir / PORTFOLIO_FILES["long_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["mid_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["short_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_manifest"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_weight_summary"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_industry_exposure"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_risk_liquidity_summary"],
        score_dir / SCORE_FILES["composite_scores"],
        score_dir / SCORE_FILES["horizon_scores"],
        score_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"],
        market_history_dir / "daily_price_history_panel.parquet",
        market_history_dir / "adjusted_price_history_panel.parquet",
        universe_dir / "trading_calendar.parquet",
        briefing_dir / BRIEFING_FILES["daily_stock_selection_briefing"],
        briefing_dir / BRIEFING_FILES["briefing_manifest"],
    ]


def _merge_score_frame(base_scores: pd.DataFrame, horizon_scores: pd.DataFrame, composite_scores: pd.DataFrame) -> pd.DataFrame:
    if base_scores.empty or horizon_scores.empty or composite_scores.empty:
        return pd.DataFrame()
    base_columns = [
        "symbol",
        "RiskScore",
        "LiquidityScore",
        "IndustryScore",
        "FundamentalScore",
        "risk_percentile",
        "liquidity_percentile",
        "industry_percentile",
        "fundamental_percentile",
    ]
    horizon_columns = [
        "symbol",
        "name",
        "exchange",
        "board",
        "industry_level_1",
        "industry_level_2",
        "LongScore",
        "LongRank",
        "LongPercentile",
        "MidScore",
        "MidRank",
        "MidPercentile",
        "ShortScore",
        "ShortRank",
        "ShortPercentile",
    ]
    composite_columns = ["symbol", "CompositeOpportunityScore", "CompositeRank", "CompositePercentile", "CompositeConfidence"]
    frame = horizon_scores[[column for column in horizon_columns if column in horizon_scores.columns]].merge(
        base_scores[[column for column in base_columns if column in base_scores.columns]],
        on="symbol",
        how="left",
    )
    frame = frame.merge(
        composite_scores[[column for column in composite_columns if column in composite_scores.columns]],
        on="symbol",
        how="left",
    )
    return frame.drop_duplicates("symbol").sort_values("symbol").reset_index(drop=True)


def _read_price_slice(path: Path, as_of_date: str, symbols: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path, filters=[("date", "==", as_of_date), ("symbol", "in", symbols)])
    except Exception:
        frame = read_frame(path)
        if frame.empty:
            return frame
        return frame[(frame["date"].astype(str) == as_of_date) & frame["symbol"].astype(str).isin(symbols)].reset_index(drop=True)


def _resolve_project_path(paths: ProjectPaths, value: str) -> Path:
    if not value:
        return Path("")
    path = Path(value)
    if path.is_absolute():
        return path
    return paths.project_root / path


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _load_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def _symbols_from_json(path: Path) -> set[str]:
    rows = _load_list(path)
    return {str(row.get("symbol")) for row in rows if row.get("symbol")}
