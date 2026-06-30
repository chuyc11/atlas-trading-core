"""Candidate tracking digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_candidate_tracking_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    card = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_candidate_summary_card.json")
    return {
        "digest_id": "A-SHARE-CANDIDATE-TRACKING-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "candidate_tracking_available": card.get("available", bool(card)),
        "candidate_count": card.get("candidate_count") or card.get("row_count"),
        "preferred_wording": "研究候选 / 候选跟踪",
        "not_recommendation": True,
        "not_trade_instruction": True,
    }

