from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, relaxed_portfolio_config
from trading_core.equity_briefings.briefing_config import BRIEFING_FILES
from trading_core.equity_briefings.daily_stock_selection_briefing import build_a_share_daily_stock_selection_briefing
from trading_core.equity_features.feature_audit import audit_a_share_multi_horizon_features
from trading_core.equity_portfolios.virtual_portfolio_audit import audit_a_share_virtual_portfolios
from trading_core.equity_scoring.scoring_audit import audit_a_share_scores
from trading_core.equity_selection.candidate_generation_audit import audit_a_share_candidates
from trading_core.storage.file_paths import ProjectPaths


def make_briefing_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    audit_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE)
    audit_a_share_scores(paths=paths, as_of_date=AS_OF_DATE)
    audit_a_share_candidates(paths=paths, as_of_date=AS_OF_DATE)
    audit_a_share_virtual_portfolios(paths=paths, as_of_date=AS_OF_DATE)
    return paths


def build_briefing_package(paths: ProjectPaths) -> dict:
    return build_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)


def briefing_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_briefings" / "daily" / AS_OF_DATE


def briefing_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_briefings" / "daily" / AS_OF_DATE


def briefing_json(paths: ProjectPaths, key: str = "daily_stock_selection_briefing"):
    return json.loads((briefing_data_dir(paths) / BRIEFING_FILES[key]).read_text(encoding="utf-8"))
