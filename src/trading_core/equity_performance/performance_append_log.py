"""Append-only performance ledger metadata."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PerformanceConfig


def build_performance_append_log(
    *,
    config: PerformanceConfig,
    existing_dates: list[str],
    appended_dates: list[str],
    duplicate_dates: list[str],
    idempotent_dates: list[str],
    rebuilt_dates: list[str],
    generated_at: str,
) -> dict[str, Any]:
    return {
        "append_log_id": "A-SHARE-MULTI-DAY-PERFORMANCE-APPEND-LOG",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "generated_at": generated_at,
        "mode": config.mode,
        "append_only": config.append_only,
        "allow_rebuild": config.allow_rebuild,
        "allow_idempotent_append": config.allow_idempotent_append,
        "allow_historical_reconstruction": config.allow_historical_reconstruction,
        "existing_dates": sorted(set(existing_dates)),
        "appended_dates": sorted(set(appended_dates)),
        "duplicate_dates": sorted(set(duplicate_dates)),
        "idempotent_dates": sorted(set(idempotent_dates)),
        "rebuilt_dates": sorted(set(rebuilt_dates)),
        "prior_dates_rewritten": False,
        "historical_reconstruction_used": bool(rebuilt_dates) and config.mode == "rebuild_virtual_performance_series",
        "historical_reconstruction_labeled_separately": config.label_historical_reconstruction_separately,
        **PERFORMANCE_FLAGS,
    }
