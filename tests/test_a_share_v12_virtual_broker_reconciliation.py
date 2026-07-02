from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_virtual_broker_reconciliation_stays_virtual(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    broker = v12_json(paths, "v12_virtual_broker_reconciliation_result")

    assert result["virtual_broker_reconciliation_passed"] is True
    assert broker["simulated_fill_reconciliation_passed"] is True
    assert broker["simulated_order_lifecycle_reconciliation_passed"] is True
    assert broker["broker_connected"] is False
    assert broker["real_orders_placed"] is False
    assert broker["real_order_preview_generated"] is False
