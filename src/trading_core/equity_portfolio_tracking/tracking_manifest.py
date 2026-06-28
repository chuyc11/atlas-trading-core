"""Manifest and source trace helpers for virtual portfolio tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_portfolio_tracking.tracking_config import PORTFOLIO_KEYS, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, TRACKING_BOUNDARY, TRACKING_FLAGS
from trading_core.equity_portfolio_tracking.tracking_inputs import TrackingInputs
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_tracking_manifest(
    *,
    paths: ProjectPaths,
    inputs: TrackingInputs,
    artifacts: dict[str, Path],
    generated_at: str,
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "input_portfolio_manifest_path": relative(inputs.portfolio_manifest_path, paths.project_root),
        "input_briefing_manifest_path": relative(inputs.briefing_manifest_path, paths.project_root),
        "tracking_config_path": relative(artifacts["tracking_config"], paths.project_root),
        "paper_ledgers": {key: relative(artifacts[f"{key}_paper_ledger"], paths.project_root) for key in PORTFOLIO_KEYS},
        "holdings_snapshots": {key: relative(artifacts[f"{key}_holdings_snapshot"], paths.project_root) for key in PORTFOLIO_KEYS},
        "performance_snapshot_path": relative(artifacts["portfolio_performance_snapshot"], paths.project_root),
        "benchmark_comparison_path": relative(artifacts["benchmark_comparison_snapshot"], paths.project_root),
        "virtual_tracking_generated": True,
        "paper_ledger_generated": True,
        "real_portfolio_generated": False,
        "buy_sell_signals_generated": False,
        "order_preview_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
        "artifacts": _artifact_records(paths, artifacts),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_tracking_source_trace(
    *,
    paths: ProjectPaths,
    inputs: TrackingInputs,
    artifacts: dict[str, Path],
    generated_at: str,
) -> dict[str, Any]:
    portfolio_sources = {
        key: relative(inputs.portfolio_dir / f"{key}_virtual_portfolio.json", paths.project_root)
        for key in PORTFOLIO_KEYS
    }
    source_paths = [
        *[inputs.portfolio_dir / f"{key}_virtual_portfolio.json" for key in PORTFOLIO_KEYS],
        inputs.candidate_manifest_path,
        inputs.score_manifest_path,
        inputs.briefing_manifest_path,
        inputs.daily_price_history_path,
        inputs.adjusted_price_history_path,
    ]
    return {
        "trace_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "virtual_portfolio_source_paths": portfolio_sources,
        "candidate_manifest_source_path": relative(inputs.candidate_manifest_path, paths.project_root),
        "score_manifest_source_path": relative(inputs.score_manifest_path, paths.project_root),
        "briefing_manifest_source_path": relative(inputs.briefing_manifest_path, paths.project_root),
        "price_source_path": {
            "daily_price_history": relative(inputs.daily_price_history_path, paths.project_root),
            "adjusted_price_history": relative(inputs.adjusted_price_history_path, paths.project_root),
        },
        "valuation_price_policy": "adjusted_close_then_close",
        "benchmark_source_path": None,
        "benchmark_gap_reason": "local benchmark price series not available for CSI300/CSI500/CSI1000 in v0.7.8 inputs",
        "audit_source_path": relative(paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json", paths.project_root),
        "tracking_artifact_paths": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "sources": [_source_record(paths, path) for path in source_paths],
        "source_trace_complete": all(path.exists() for path in source_paths),
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }


def _artifact_records(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "sha256": None if key == "tracking_manifest" else sha256_file(path),
        }
        for key, path in artifacts.items()
    }


def _source_record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path),
    }
