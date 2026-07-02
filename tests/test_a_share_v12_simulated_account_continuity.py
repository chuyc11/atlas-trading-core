from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_simulated_account_and_paper_ledger_continuity(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    history = v12_json(paths, "v12_simulated_account_history_result")
    account = v12_json(paths, "v12_simulated_account_continuity_check")
    ledger = v12_json(paths, "v12_paper_ledger_continuity_check")

    assert result["simulated_account_history_generated"] is True
    assert history["nav_history"]
    assert history["cash_history"]
    assert history["position_history"]
    assert history["pnl_history"]
    assert history["turnover_history"]
    assert account["simulated_account_continuity_passed"] is True
    assert account["nav_identity_check_passed"] is True
    assert account["impossible_cash_balance_detected"] is False
    assert account["impossible_position_quantity_detected"] is False
    assert ledger["paper_ledger_continuity_passed"] is True
    assert ledger["duplicate_ledger_entry_detected"] is False
