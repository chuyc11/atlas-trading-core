"""Manifest helpers for A-share daily stock selection briefings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_briefings.briefing_config import BRIEFING_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_briefings.briefing_inputs import BriefingInputs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_briefing_manifest(
    *,
    paths: ProjectPaths,
    inputs: BriefingInputs,
    artifacts: dict[str, Path],
    generated_at: str,
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "input_candidate_manifest_path": relative(inputs.candidate_manifest_path, paths.project_root),
        "input_score_manifest_path": relative(inputs.score_manifest_path, paths.project_root),
        "input_feature_manifest_path": relative(inputs.feature_manifest_path, paths.project_root),
        "input_portfolio_manifest_path": relative(inputs.portfolio_manifest_path, paths.project_root),
        "briefing_path": relative(artifacts["daily_stock_selection_briefing"], paths.project_root),
        "briefing_report_path": relative(artifacts["daily_stock_selection_briefing_report"], paths.project_root),
        "briefing_source_trace_path": relative(artifacts["briefing_source_trace"], paths.project_root),
        "briefing_source_trace_report_path": relative(artifacts["briefing_source_trace_report"], paths.project_root),
        "briefing_only": True,
        "scores_regenerated": False,
        "candidates_regenerated": False,
        "virtual_portfolios_regenerated": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        "boundary": dict(BRIEFING_BOUNDARY),
        "artifacts": _artifact_records(paths, artifacts),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_records(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "sha256": sha256_file(path),
        }
        for key, path in artifacts.items()
    }
