from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from a_share_candidate_test_utils import build_candidate_package, make_candidate_paths, relaxed_candidate_config
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_FILES, PortfolioConstructionConfig
from trading_core.equity_portfolios.virtual_portfolio_builder import build_a_share_virtual_portfolios
from trading_core.storage.file_paths import ProjectPaths


def relaxed_portfolio_config(**overrides) -> PortfolioConstructionConfig:
    values = {
        "as_of_date": AS_OF_DATE,
        "long_holdings": 2,
        "mid_holdings": 2,
        "short_holdings": 2,
        "long_max_single_weight": 0.80,
        "mid_max_single_weight": 0.80,
        "short_max_single_weight": 0.80,
        "long_max_industry_weight": 1.0,
        "mid_max_industry_weight": 1.0,
        "short_max_industry_weight": 1.0,
        "long_min_risk_score": 0.0,
        "long_min_liquidity_score": 0.0,
        "mid_min_risk_score": 0.0,
        "mid_min_liquidity_score": 0.0,
        "short_min_risk_score": 0.0,
        "short_min_liquidity_score": 0.0,
    }
    values.update(overrides)
    return PortfolioConstructionConfig(**values)


def make_portfolio_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config())
    return paths


def build_portfolio_package(paths: ProjectPaths, config: PortfolioConstructionConfig | None = None) -> dict:
    return build_a_share_virtual_portfolios(paths=paths, config=config or relaxed_portfolio_config())


def portfolio_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_portfolios" / "daily" / AS_OF_DATE


def portfolio_json(paths: ProjectPaths, key: str):
    return json.loads((portfolio_data_dir(paths) / PORTFOLIO_FILES[key]).read_text(encoding="utf-8"))


def portfolio_frame(paths: ProjectPaths, key: str) -> pd.DataFrame:
    return pd.read_parquet(portfolio_data_dir(paths) / PORTFOLIO_FILES[key])

