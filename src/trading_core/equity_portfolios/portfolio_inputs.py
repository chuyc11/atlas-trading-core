"""Input loading for v0.7.6 A-share virtual portfolio construction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import read_frame
from trading_core.equity_scoring.score_config import SCORE_FILES
from trading_core.equity_selection.candidate_config import CANDIDATE_FILES, DEFAULT_AS_OF_DATE as DEFAULT_CANDIDATE_AS_OF_DATE
from trading_core.equity_selection.filter_inputs import selection_data_dir
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class PortfolioInputs:
    as_of_date: str
    requested_as_of_date: str
    candidate_dir: Path
    candidate_manifest_path: Path
    candidate_manifest: dict[str, Any]
    score_manifest_path: Path
    score_manifest: dict[str, Any]
    long_candidates: pd.DataFrame
    mid_candidates: pd.DataFrame
    short_candidates: pd.DataFrame
    multi_horizon_candidates: pd.DataFrame
    risk_downgraded_symbols: set[str]
    strict_symbols: set[str]
    excluded_symbols: set[str]
    caution_symbols: set[str]
    unknown_symbols: set[str]
    score_frame: pd.DataFrame


def portfolio_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_portfolios" / "daily" / as_of_date


def portfolio_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_portfolios" / "daily" / as_of_date


def load_portfolio_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_CANDIDATE_AS_OF_DATE,
    allow_latest_candidate_date: bool = False,
) -> PortfolioInputs:
    paths = default_paths(paths)
    selected_date, candidate_dir = _resolve_candidate_dir(paths, as_of_date, allow_latest_candidate_date)
    candidate_manifest_path = candidate_dir / CANDIDATE_FILES["candidate_manifest"]
    candidate_manifest = _load_json(candidate_manifest_path)
    if not candidate_manifest:
        raise ValueError(f"candidate manifest not found: {candidate_manifest_path}")
    score_manifest_path = _resolve_manifest_path(paths, str(candidate_manifest.get("input_score_manifest_path") or ""))
    score_manifest = _load_json(score_manifest_path)
    if not score_manifest:
        raise ValueError(f"score manifest not found: {score_manifest_path}")
    long_candidates = read_frame(candidate_dir / CANDIDATE_FILES["long_candidates_parquet"])
    mid_candidates = read_frame(candidate_dir / CANDIDATE_FILES["mid_candidates_parquet"])
    short_candidates = read_frame(candidate_dir / CANDIDATE_FILES["short_candidates_parquet"])
    if long_candidates.empty or mid_candidates.empty or short_candidates.empty:
        raise ValueError(f"candidate files are missing or empty for {selected_date}")
    multi_horizon = pd.DataFrame(_load_json_list(candidate_dir / CANDIDATE_FILES["multi_horizon_candidates"]))
    risk_downgraded = pd.DataFrame(_load_json_list(candidate_dir / CANDIDATE_FILES["risk_downgraded_candidates"]))
    selection_dir = selection_data_dir(paths, selected_date)
    strict = _load_json_list(selection_dir / "strict_tradable_universe.json")
    excluded = _load_json_list(selection_dir / "excluded_universe.json")
    caution = _load_json_list(selection_dir / "caution_universe.json")
    unknown = _load_json_list(selection_dir / "unknown_status_universe.json")
    score_dir = paths.data_dir / "equity_scores" / "daily" / selected_date
    score_frame = _merge_score_frame(
        read_frame(score_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"]),
        read_frame(score_dir / SCORE_FILES["horizon_scores"]),
        read_frame(score_dir / SCORE_FILES["composite_scores"]),
    )
    return PortfolioInputs(
        as_of_date=selected_date,
        requested_as_of_date=as_of_date,
        candidate_dir=candidate_dir,
        candidate_manifest_path=candidate_manifest_path,
        candidate_manifest=candidate_manifest,
        score_manifest_path=score_manifest_path,
        score_manifest=score_manifest,
        long_candidates=long_candidates,
        mid_candidates=mid_candidates,
        short_candidates=short_candidates,
        multi_horizon_candidates=_enrich_multi_horizon(multi_horizon, score_frame),
        risk_downgraded_symbols={str(row.get("symbol")) for row in risk_downgraded.to_dict("records") if row.get("symbol")},
        strict_symbols={str(row.get("symbol")) for row in strict if row.get("symbol")},
        excluded_symbols={str(row.get("symbol")) for row in excluded if row.get("symbol")},
        caution_symbols={str(row.get("symbol")) for row in caution if row.get("symbol")},
        unknown_symbols={str(row.get("symbol")) for row in unknown if row.get("symbol")},
        score_frame=score_frame,
    )


def _resolve_candidate_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_selection" / "daily"
    exact = base / as_of_date
    if (exact / CANDIDATE_FILES["candidate_manifest"]).exists():
        return as_of_date, exact
    if not allow_latest:
        raise ValueError(f"candidate files not found for as_of_date={as_of_date}")
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / CANDIDATE_FILES["candidate_manifest"]).exists())
    if not candidates:
        raise ValueError(f"no candidate files available on or before {as_of_date}")
    selected = candidates[-1]
    return selected.name, selected


def _resolve_manifest_path(paths: ProjectPaths, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return paths.project_root / path


def _merge_score_frame(base_scores: pd.DataFrame, horizon_scores: pd.DataFrame, composite_scores: pd.DataFrame) -> pd.DataFrame:
    if base_scores.empty or horizon_scores.empty or composite_scores.empty:
        return pd.DataFrame()
    base_columns = [
        "symbol",
        "RiskScore",
        "risk_percentile",
        "risk_confidence",
        "LiquidityScore",
        "liquidity_percentile",
        "liquidity_confidence",
        "IndustryScore",
        "industry_percentile",
        "industry_confidence",
        "FundamentalScore",
        "fundamental_percentile",
        "fundamental_confidence",
    ]
    composite_columns = ["symbol", "CompositeOpportunityScore", "CompositeRank", "CompositePercentile", "CompositeConfidence"]
    frame = horizon_scores.merge(base_scores[base_columns], on="symbol", how="left")
    frame = frame.merge(composite_scores[composite_columns], on="symbol", how="left")
    frame["RiskPercentile"] = frame["risk_percentile"]
    frame["LiquidityPercentile"] = frame["liquidity_percentile"]
    frame["IndustryPercentile"] = frame["industry_percentile"]
    return frame.sort_values("symbol").reset_index(drop=True)


def _enrich_multi_horizon(multi_horizon: pd.DataFrame, score_frame: pd.DataFrame) -> pd.DataFrame:
    if multi_horizon.empty or score_frame.empty:
        return multi_horizon
    score_columns = [
        "symbol",
        "RiskScore",
        "LiquidityScore",
        "IndustryScore",
        "FundamentalScore",
        "LongRank",
        "MidRank",
        "ShortRank",
        "LongPercentile",
        "MidPercentile",
        "ShortPercentile",
        "LongConfidence",
        "MidConfidence",
        "ShortConfidence",
        "CompositeConfidence",
    ]
    add = score_frame[[column for column in score_columns if column in score_frame.columns]].drop_duplicates("symbol")
    existing = [column for column in add.columns if column in multi_horizon.columns and column != "symbol"]
    if existing:
        multi_horizon = multi_horizon.drop(columns=existing)
    return multi_horizon.merge(add, on="symbol", how="left")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []

