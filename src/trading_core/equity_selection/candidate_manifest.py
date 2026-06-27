"""Candidate manifest helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_selection.candidate_config import CANDIDATE_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_candidate_manifest(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    score_manifest_path: Path,
    strict_tradable_count: int,
    scored_symbols: int,
    candidate_counts: dict[str, int],
    artifacts: dict[str, Path],
    created_at: str,
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-CANDIDATE-GENERATION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "created_at": created_at,
        "input_score_manifest_path": relative(score_manifest_path, paths.project_root),
        "strict_tradable_count": strict_tradable_count,
        "scored_symbols": scored_symbols,
        "candidate_counts": candidate_counts,
        "candidate_generation_only": True,
        "scores_generated_upstream": True,
        "virtual_portfolio_generated": False,
        "buy_sell_signals_generated": False,
        "order_instructions_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        "boundary": dict(CANDIDATE_BOUNDARY),
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
