from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from a_share_feature_test_utils import AS_OF_DATE
from a_share_score_test_utils import build_score_package, make_score_paths
from trading_core.equity_selection.candidate_config import CANDIDATE_FILES, CandidateGenerationConfig
from trading_core.equity_selection.candidate_generator import generate_a_share_candidates
from trading_core.storage.file_paths import ProjectPaths


def relaxed_candidate_config(**overrides) -> CandidateGenerationConfig:
    values = {
        "as_of_date": AS_OF_DATE,
        "long_count": 2,
        "mid_count": 2,
        "short_count": 2,
        "extended_count": 2,
        "long_percentile_min": 0.0,
        "mid_percentile_min": 0.0,
        "short_percentile_min": 0.0,
        "multi_horizon_percentile_min": 0.0,
        "composite_percentile_min": 0.0,
        "long_risk_percentile_min": 0.0,
        "long_risk_score_min": 0.0,
        "long_liquidity_percentile_min": 0.0,
        "long_liquidity_score_min": 0.0,
        "mid_risk_percentile_min": 0.0,
        "mid_risk_score_min": 0.0,
        "mid_liquidity_percentile_min": 0.0,
        "mid_liquidity_score_min": 0.0,
        "mid_industry_score_min_percentile": 0.0,
        "short_risk_percentile_min": 0.0,
        "short_risk_score_min": 0.0,
        "short_liquidity_percentile_min": 0.0,
        "short_liquidity_score_min": 0.0,
        "severe_overheat_component_max": 0.0,
        "minimum_fundamental_confidence": 0.0,
        "minimum_candidate_confidence": 0.0,
    }
    values.update(overrides)
    return CandidateGenerationConfig(**values)


def make_candidate_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)
    return paths


def build_candidate_package(paths: ProjectPaths, config: CandidateGenerationConfig | None = None) -> dict:
    return generate_a_share_candidates(paths=paths, config=config or relaxed_candidate_config())


def candidate_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE


def candidate_json(paths: ProjectPaths, key: str):
    return json.loads((candidate_data_dir(paths) / CANDIDATE_FILES[key]).read_text(encoding="utf-8"))


def candidate_frame(paths: ProjectPaths, key: str) -> pd.DataFrame:
    return pd.read_parquet(candidate_data_dir(paths) / CANDIDATE_FILES[key])
