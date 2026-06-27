"""Manifest and coverage helpers for A-share feature engineering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_features.feature_config import FEATURE_BOUNDARY, FEATURE_GROUP_FIELDS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def feature_group_metadata(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    result = {}
    for group, path in artifacts.items():
        frame = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        result[group] = {
            "path": relative(path, paths.project_root),
            "symbols": int(frame["symbol"].nunique()) if not frame.empty and "symbol" in frame.columns else 0,
            "fields": len([column for column in frame.columns if column not in {"as_of_date", "symbol", "name", "exchange", "board", "industry_level_1", "industry_level_2", "feature_group", "source", "created_at"}]),
            "rows": int(len(frame)),
            "sha256": sha256_file(path),
        }
    return result


def build_field_coverage_payload(frames: dict[str, pd.DataFrame], strict_count: int, as_of_date: str) -> dict[str, Any]:
    groups = {}
    for group, frame in frames.items():
        fields = FEATURE_GROUP_FIELDS[group]
        field_coverage = {}
        for field in fields:
            field_coverage[field] = round(float(frame[field].notna().mean()), 6) if field in frame.columns and len(frame) else 0.0
        symbol_coverage = round(float(frame["symbol"].nunique() / strict_count), 6) if strict_count else 0.0
        groups[group] = {
            "symbols": int(frame["symbol"].nunique()) if "symbol" in frame.columns else 0,
            "symbol_coverage": symbol_coverage,
            "field_coverage": field_coverage,
            "mandatory_field_coverage": round(sum(field_coverage.values()) / len(fields), 6) if fields else 0.0,
        }
    return {
        "coverage_id": "A-SHARE-MULTI-HORIZON-FEATURE-FIELD-COVERAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strict_tradable_count": strict_count,
        "groups": groups,
        "boundary": dict(FEATURE_BOUNDARY),
    }

