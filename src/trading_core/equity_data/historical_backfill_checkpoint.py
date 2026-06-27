"""Checkpoint helpers for full-market A-share historical backfill."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import data_quality_dir, read_json, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths


CHECKPOINT_ID = "A-SHARE-HISTORICAL-BACKFILL-CHECKPOINT"


def checkpoint_path(paths: ProjectPaths):
    return data_quality_dir(paths) / "a_share_historical_backfill_checkpoint.json"


def load_backfill_checkpoint(paths: ProjectPaths) -> dict[str, Any]:
    return read_json(checkpoint_path(paths))


def write_backfill_checkpoint(
    paths: ProjectPaths,
    *,
    target_version: str,
    symbols_total: int,
    symbols_completed: list[str],
    symbols_failed: list[str],
    current_batch: int,
    complete: bool,
    sample_mode: bool = False,
) -> dict[str, Any]:
    payload = {
        "checkpoint_id": CHECKPOINT_ID,
        "target_version": target_version,
        "updated_at": utc_now(),
        "symbols_total": symbols_total,
        "symbols_completed": sorted(set(symbols_completed)),
        "symbols_failed": sorted(set(symbols_failed)),
        "symbols_completed_count": len(set(symbols_completed)),
        "symbols_failed_count": len(set(symbols_failed)),
        "current_batch": current_batch,
        "complete": complete,
        "sample_mode": sample_mode,
    }
    write_json(checkpoint_path(paths), payload)
    return payload
