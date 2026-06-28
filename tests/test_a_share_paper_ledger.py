from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json
from trading_core.equity_portfolio_tracking.tracking_config import ALLOWED_LEDGER_RECORD_TYPES, FORBIDDEN_LEDGER_RECORD_TYPES


def test_paper_ledgers_generated_for_long_mid_short(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)

    for key in ["long", "mid", "short"]:
        ledger = tracking_json(paths, f"{key}_paper_ledger")
        assert len(ledger) == 2
        assert {row["record_type"] for row in ledger} == {"virtual_initial_position"}
        assert {row["record_type"] for row in ledger}.issubset(ALLOWED_LEDGER_RECORD_TYPES)
        assert not {row["record_type"] for row in ledger}.intersection(FORBIDDEN_LEDGER_RECORD_TYPES)
        assert all(row["virtual_only"] and row["research_only"] for row in ledger)
        assert all(row["not_real_trade"] and row["not_order_instruction"] for row in ledger)
        assert all(row["fractional_shares_allowed"] is True for row in ledger)
        assert all(row["board_lot_execution_simulated"] is False for row in ledger)
        assert all(row["real_execution_simulated"] is False for row in ledger)
