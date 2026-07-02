from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_simulated_account_cash_position_and_paper_ledger_reconcile(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    account = v11_json(paths, "v11_simulated_account_reconciliation_result")
    ledger = v11_json(paths, "v11_paper_ledger_invariant_check")

    assert result["simulated_account_reconciled"] is True
    assert account["cash_reconciliation"]["passed"] is True
    assert account["positions_reconciliation"]["passed"] is True
    assert account["commission_slippage_attribution"]["attribution_generated"] is True
    assert account["turnover"]["calculation_generated"] is True
    assert ledger["paper_ledger_invariant_passed"] is True
