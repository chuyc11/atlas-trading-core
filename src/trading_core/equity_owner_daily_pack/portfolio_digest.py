"""Virtual portfolio digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_virtual_portfolio_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    card = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_portfolio_summary_card.json")
    return {
        "digest_id": "A-SHARE-VIRTUAL-PORTFOLIO-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "virtual_portfolio_available": card.get("available", bool(card)),
        "portfolio_count": card.get("portfolio_count") or card.get("row_count"),
        "paper_ledger_only": True,
        "not_real_portfolio": True,
        "not_trade_instruction": True,
    }

