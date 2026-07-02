from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_strategy_and_experiment_registry_lifecycle(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    experiment = v11_json(paths, "v11_experiment_registry_expansion_result")
    strategy = v11_json(paths, "v11_strategy_registry_expansion_result")

    assert result["experiment_registry_expanded"] is True
    assert result["strategy_registry_expanded"] is True
    assert experiment["experiment_to_strategy_linkage_supported"] is True
    assert strategy["strategy_lineage_generated"] is True
    assert strategy["status_transition_audit_generated"] is True
    assert strategy["real_trading_active_allowed"] is False
