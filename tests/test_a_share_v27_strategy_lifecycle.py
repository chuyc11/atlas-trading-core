from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v27_strategy_lifecycle_remains_simulated_only(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v27")
    spec, result, audit = build_release(paths, "v27")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v26_baseline_verified"] is True
    assert result["strategy_lifecycle_registry_generated"] is True
    assert result["real_trading_active_state_present"] is False
    assert result["promotion_generates_real_trade"] is False
    assert result["demotion_generates_sell_signal"] is False
    assert result["simulation_active_generates_real_order"] is False
    assert result["full_pytest_run"] is False
    assert len(spec["markdown_names"]) == 6
