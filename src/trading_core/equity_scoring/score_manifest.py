"""Score manifest, distribution, and summary helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_scoring.component_scores import ScoringInputs
from trading_core.equity_scoring.normalization import score_range
from trading_core.equity_scoring.score_config import RECOMMENDED_NEXT_VERSION, SCORE_BOUNDARY, SCORE_COLUMNS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_score_distribution(base_scores: pd.DataFrame, horizon_scores: pd.DataFrame, composite_scores: pd.DataFrame, as_of_date: str) -> dict[str, Any]:
    frame = _score_frame(base_scores, horizon_scores, composite_scores)
    distributions = {}
    for column in SCORE_COLUMNS:
        values = pd.to_numeric(frame[column], errors="coerce").dropna() if column in frame.columns else pd.Series(dtype=float)
        if values.empty:
            distributions[column] = {"count": 0, "min": None, "max": None, "mean": None, "deciles": {}}
            continue
        distributions[column] = {
            "count": int(len(values)),
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "deciles": _deciles(values),
        }
    return {
        "distribution_id": "A-SHARE-SCORE-DISTRIBUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "percentile_convention": "0_to_100",
        "confidence_convention": "0_to_1",
        "scores": distributions,
        "boundary": dict(SCORE_BOUNDARY),
    }


def build_score_manifest(
    paths: ProjectPaths,
    inputs: ScoringInputs,
    config: dict[str, Any],
    artifacts: dict[str, Path],
    created_at: str,
) -> dict[str, Any]:
    ranges = {}
    for key in ["risk_liquidity_industry_fundamental_scores", "horizon_scores", "composite_scores"]:
        path = artifacts.get(key)
        frame = pd.read_parquet(path) if path and path.exists() else pd.DataFrame()
        for column in SCORE_COLUMNS:
            if column in frame.columns:
                ranges[column] = score_range(frame, column)
    return {
        "manifest_id": "A-SHARE-SCORING-MANIFEST",
        "target_version": TARGET_VERSION,
        "score_version": config["score_version"],
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "created_at": created_at,
        "input_feature_manifest_path": relative(inputs.feature_manifest_path, paths.project_root),
        "strict_tradable_universe_path": relative(inputs.strict_universe_path, paths.project_root),
        "strict_tradable_count": int(len(inputs.strict_universe)),
        "score_artifacts": _artifact_records(paths, artifacts),
        "score_ranges": ranges,
        "no_future_leakage": bool(inputs.feature_manifest.get("no_future_leakage") is True),
        "source_dates": inputs.feature_manifest.get("source_dates", {}),
        "normalization_method": config["normalization_method"],
        "winsorization_limits": config["winsorization_limits"],
        "percentile_convention": config["percentile_convention"],
        "confidence_convention": config["confidence_convention"],
        "boundary": dict(SCORE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_scoring_summary(
    paths: ProjectPaths,
    inputs: ScoringInputs,
    base_scores: pd.DataFrame,
    horizon_scores: pd.DataFrame,
    composite_scores: pd.DataFrame,
    distribution: dict[str, Any],
    manifest: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    warnings = []
    fundamental_confidence = pd.to_numeric(base_scores.get("fundamental_confidence"), errors="coerce").mean()
    if pd.notna(fundamental_confidence) and float(fundamental_confidence) < 0.75:
        warnings.append("fundamental score confidence is partial")
    return {
        "summary_id": "A-SHARE-SCORING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "created_at": created_at,
        "strict_tradable_count": int(len(inputs.strict_universe)),
        "scored_symbols": int(composite_scores["symbol"].nunique()),
        "counts": {
            "risk_liquidity_industry_fundamental_rows": int(len(base_scores)),
            "horizon_score_rows": int(len(horizon_scores)),
            "composite_score_rows": int(len(composite_scores)),
        },
        "score_ranges": manifest["score_ranges"],
        "distribution": distribution["scores"],
        "warnings": warnings,
        "boundary": dict(SCORE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _score_frame(base_scores: pd.DataFrame, horizon_scores: pd.DataFrame, composite_scores: pd.DataFrame) -> pd.DataFrame:
    frame = base_scores[["symbol", "RiskScore", "LiquidityScore", "IndustryScore", "FundamentalScore"]].merge(
        horizon_scores[["symbol", "LongScore", "MidScore", "ShortScore"]],
        on="symbol",
        how="outer",
    )
    return frame.merge(composite_scores[["symbol", "CompositeOpportunityScore"]], on="symbol", how="outer")


def _deciles(values: pd.Series) -> dict[str, int]:
    clipped = values.clip(0, 100)
    labels = [f"{index * 10}-{index * 10 + 10}" for index in range(10)]
    buckets = pd.cut(clipped, bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], labels=labels, include_lowest=True)
    counts = buckets.value_counts().sort_index()
    return {str(label): int(counts.get(label, 0)) for label in labels}


def _artifact_records(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    records = {}
    for key, path in artifacts.items():
        records[key] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "rows": int(len(pd.read_parquet(path))) if path.exists() and path.suffix == ".parquet" else None,
            "sha256": sha256_file(path),
        }
    return records
