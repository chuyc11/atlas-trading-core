"""Portfolio manifest helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_portfolios.industry_constraints import max_industry_weight
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_portfolio_manifest(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    candidate_manifest_path: Path,
    score_manifest_path: Path,
    portfolio_records: dict[str, list[dict[str, Any]]],
    artifacts: dict[str, Path],
    created_at: str,
) -> dict[str, Any]:
    portfolios = {}
    for portfolio_id, rows in portfolio_records.items():
        key = f"{portfolio_id}_parquet"
        weights = [float(row.get("target_weight") or 0.0) for row in rows]
        portfolios[portfolio_id] = {
            "path": relative(artifacts[key], paths.project_root) if key in artifacts else "",
            "holdings": len(rows),
            "weight_sum": round(sum(weights), 6),
            "max_single_weight": round(max(weights or [0.0]), 6),
            "max_industry_weight": round(max_industry_weight(rows), 6),
        }
    return {
        "manifest_id": "A-SHARE-VIRTUAL-PORTFOLIO-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "created_at": created_at,
        "input_candidate_manifest_path": relative(candidate_manifest_path, paths.project_root),
        "input_score_manifest_path": relative(score_manifest_path, paths.project_root),
        "portfolios": portfolios,
        "virtual_portfolio_generated": True,
        "real_portfolio_generated": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        "boundary": dict(PORTFOLIO_BOUNDARY),
        "artifacts": _artifact_records(paths, artifacts),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_records(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    records = {}
    for key, path in artifacts.items():
        rows = None
        if path.exists() and path.suffix == ".parquet":
            rows = int(len(pd.read_parquet(path)))
        records[key] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "rows": rows,
            "sha256": sha256_file(path),
        }
    return records
