"""Candidate summary card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_list
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_candidate_summary_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    base = paths.data_dir / "equity_selection" / "daily" / as_of_date
    long_items = load_list(base / "long_candidates.json")
    mid_items = load_list(base / "mid_candidates.json")
    short_items = load_list(base / "short_candidates.json")
    extended = load_list(base / "extended_watch_pool.json")
    multi = load_list(base / "multi_horizon_candidates.json")
    risk = load_list(base / "risk_downgraded_candidates.json")
    return {
        "card_id": "CANDIDATE_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": "available" if long_items or mid_items or short_items else "missing_optional",
        "long_candidate_count": len(long_items),
        "mid_candidate_count": len(mid_items),
        "short_candidate_count": len(short_items),
        "extended_watch_pool_count": len(extended),
        "multi_horizon_candidate_count": len(multi),
        "risk_downgraded_count": len(risk),
        "top10_symbols": {
            "long": _symbols(long_items),
            "mid": _symbols(mid_items),
            "short": _symbols(short_items),
        },
        "safe_wording": ["研究候选", "候选跟踪", "高评分候选", "观察池"],
        "warnings": [] if long_items or mid_items or short_items else ["candidate_inputs_missing_optional"],
    }


def _symbols(items: list[Any]) -> list[str]:
    return [str(row.get("symbol")) for row in items[:10] if isinstance(row, dict) and row.get("symbol")]

