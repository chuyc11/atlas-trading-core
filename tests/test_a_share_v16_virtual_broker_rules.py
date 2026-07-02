from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_virtual_broker_and_paper_ledger_rules(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    broker = v16_json(paths, "v16_virtual_broker_rule_hardening_result")
    ledger = v16_json(paths, "v16_paper_ledger_replay_consistency_result")

    assert result["virtual_broker_rule_hardening_result_generated"] is True
    assert result["virtual_broker_rule_audit_passed"] is True
    assert broker["real_broker_connection_required"] is False
    assert ledger["paper_ledger_replay_passed"] is True
    assert ledger["ledger_is_virtual_only"] is True
