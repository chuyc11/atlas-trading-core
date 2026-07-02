from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_paper_ledger_replay_consistency(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    ledger = v16_json(paths, "v16_paper_ledger_replay_consistency_result")

    assert result["paper_ledger_replay_consistency_result_generated"] is True
    assert result["paper_ledger_replay_passed"] is True
    assert ledger["cash_position_invariant_checked"] is True
    assert ledger["fill_to_ledger_reconciliation_checked"] is True
