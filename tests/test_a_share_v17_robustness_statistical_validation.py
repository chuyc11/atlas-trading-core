from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_robustness_and_statistical_validation_are_limited_not_fabricated(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    robustness = v17_json(paths, "v17_robustness_sensitivity_validation_result")
    stats = v17_json(paths, "v17_statistical_false_discovery_result")

    assert result["robustness_sensitivity_validation_result_generated"] is True
    assert robustness["parameter_sensitivity_validation"] == "generated_policy_grid"
    assert robustness["transaction_cost_sensitivity_validation"] == "generated_policy_grid"
    assert robustness["slippage_sensitivity_validation"] == "generated_policy_grid"
    assert stats["multiple_testing_warning"] is True
    assert stats["data_snooping_warning"] is True
    assert stats["statistical_significance_fabricated"] is False
    assert stats["p_value_placeholder_used_as_real_conclusion"] is False
