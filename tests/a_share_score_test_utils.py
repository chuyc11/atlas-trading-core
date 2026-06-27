from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from a_share_feature_test_utils import AS_OF_DATE, build_feature_package, make_feature_paths
from trading_core.equity_scoring.component_scores import build_a_share_scores
from trading_core.equity_scoring.score_config import SCORE_FILES
from trading_core.storage.file_paths import ProjectPaths


def make_score_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)
    return paths


def build_score_package(paths: ProjectPaths) -> dict:
    return build_a_share_scores(paths=paths, as_of_date=AS_OF_DATE)


def score_frame(paths: ProjectPaths, key: str) -> pd.DataFrame:
    path = paths.data_dir / "equity_scores" / "daily" / AS_OF_DATE / SCORE_FILES[key]
    return pd.read_parquet(path)


def score_json(paths: ProjectPaths, key: str) -> dict:
    path = paths.data_dir / "equity_scores" / "daily" / AS_OF_DATE / SCORE_FILES[key]
    return json.loads(path.read_text(encoding="utf-8"))


def score_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_scores" / "daily" / AS_OF_DATE
