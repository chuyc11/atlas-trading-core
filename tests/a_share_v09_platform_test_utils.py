from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from trading_core.storage.file_paths import ProjectPaths

AS_OF_DATE = "2026-07-01"


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    (project / "data").mkdir(parents=True, exist_ok=True)
    (project / "outputs").mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def seed_v09_inputs(tmp_path: Path) -> ProjectPaths:
    paths = make_paths(tmp_path)
    _write_json(paths.data_dir / "equity_data_quality" / "a_share_historical_backfill_and_refresh_planning_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    _write_json(paths.data_dir / "equity_reevaluation_readiness_closeout" / "daily" / AS_OF_DATE / "reevaluation_readiness_boundary_check.json", {"owner_readiness_gate_rerun": False, "controlled_reevaluation_executed": False})
    _write_json(paths.data_dir / "equity_research_evidence_recomputed" / "daily" / AS_OF_DATE / "recomputed_evidence_result.json", {"eligible_day_count": 2, "blocker_coverage_ratio": 0.5})
    _write_json(paths.data_dir / "equity_data_freshness" / "daily" / AS_OF_DATE / "data_freshness_refresh_result.json", {"overall_passed": True})
    _write_json(paths.data_dir / "equity_research_pipeline_rerun" / "daily" / AS_OF_DATE / "research_pipeline_rerun_result.json", {"overall_passed": True})
    _seed_calendar(paths)
    _seed_market(paths)
    _seed_portfolio(paths)
    return paths


def platform_json(paths: ProjectPaths, name: str) -> dict:
    return read_json(paths.data_dir / "equity_v09_platform" / "daily" / AS_OF_DATE / f"{name}.json")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _seed_calendar(paths: ProjectPaths) -> None:
    frame = pd.DataFrame([{"date": AS_OF_DATE, "is_trading_day": True}, {"date": "2026-07-04", "is_trading_day": False}])
    path = paths.data_dir / "equity_universe" / "trading_calendar.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def _seed_market(paths: ProjectPaths) -> None:
    frame = pd.DataFrame(
        [
            {"date": AS_OF_DATE, "symbol": "000001.SZ", "close": 10.0},
            {"date": AS_OF_DATE, "symbol": "000002.SZ", "close": 20.0},
        ]
    )
    path = paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def _seed_portfolio(paths: ProjectPaths) -> None:
    rows = [
        {"as_of_date": AS_OF_DATE, "portfolio_id": "long_virtual_portfolio", "symbol": "000001.SZ", "target_weight": 0.1},
        {"as_of_date": AS_OF_DATE, "portfolio_id": "long_virtual_portfolio", "symbol": "000002.SZ", "target_weight": 0.2},
    ]
    _write_json(paths.data_dir / "equity_portfolios" / "daily" / AS_OF_DATE / "long_virtual_portfolio.json", rows)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
