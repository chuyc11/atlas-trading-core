"""Health score baseline calculations."""

from __future__ import annotations

from statistics import mean, median
from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_health_score_baseline(*, as_of_date: str, health_history: dict[str, Any], minimum_required_observations: int, baseline_window_observations: int | None = None) -> dict[str, Any]:
    rows = health_history.get("records", [])
    scores = [int(row["score"]) for row in rows if row.get("score") is not None]
    enough = len(scores) >= minimum_required_observations
    latest = rows[-1] if rows else {}
    average_score = mean(scores) if enough else None
    return {
        "baseline_id": "A-SHARE-OPS-HEALTH-SCORE-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(rows),
        "minimum_required_observations": minimum_required_observations,
        "baseline_window_observations": baseline_window_observations,
        "baseline_available": enough,
        "baseline_status": "available" if enough else "insufficient_history",
        "latest_score": latest.get("score"),
        "latest_grade": latest.get("grade"),
        "average_score": average_score,
        "mean_score": average_score,
        "median_score": median(scores) if enough else None,
        "min_score": min(scores) if enough else None,
        "max_score": max(scores) if enough else None,
        "score_change_vs_previous": scores[-1] - scores[-2] if enough and len(scores) >= 2 else None,
        "score_trend_status": "available" if enough else "insufficient_history",
    }
