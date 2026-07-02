from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_virtual_broker_lifecycle_remains_simulation_only(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    broker = v11_json(paths, "v11_virtual_broker_lifecycle_result")

    assert result["virtual_broker_lifecycle_checked"] is True
    assert "submitted_to_virtual_broker" in broker["simulated_order_intent_lifecycle"]
    assert broker["simulated_fill_lifecycle_checked"] is True
    assert broker["broker_connected"] is False
    assert broker["real_orders_placed"] is False
    assert broker["real_order_preview_generated"] is False
