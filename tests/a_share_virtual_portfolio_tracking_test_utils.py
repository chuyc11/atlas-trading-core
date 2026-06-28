from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from a_share_daily_stock_selection_briefing_test_utils import build_briefing_package, make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_portfolio_tracking.tracking_audit import audit_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolio_tracking.tracking_builder import build_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolio_tracking.tracking_config import TRACKING_FILES
from trading_core.storage.file_paths import ProjectPaths


def make_tracking_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_briefing_paths(tmp_path)
    _write_calendar(paths)
    build_briefing_package(paths)
    return paths


def build_tracking_package(paths: ProjectPaths) -> dict:
    return build_a_share_virtual_portfolio_tracking(paths=paths, as_of_date=AS_OF_DATE)


def audit_tracking_package(paths: ProjectPaths) -> dict:
    return audit_a_share_virtual_portfolio_tracking(paths=paths, as_of_date=AS_OF_DATE)


def tracking_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_portfolio_tracking" / "daily" / AS_OF_DATE


def tracking_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_portfolio_tracking" / "daily" / AS_OF_DATE


def tracking_json(paths: ProjectPaths, key: str):
    return json.loads((tracking_data_dir(paths) / TRACKING_FILES[key]).read_text(encoding="utf-8"))


def _write_calendar(paths: ProjectPaths) -> None:
    path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "date": AS_OF_DATE,
                "exchange": "SSE",
                "is_trading_day": True,
                "previous_trading_day": "2026-06-25",
                "next_trading_day": "2026-06-29",
                "source": "fixture_calendar",
                "source_timestamp": "2026-06-26T00:00:00Z",
            }
        ]
    ).to_parquet(path, index=False)
