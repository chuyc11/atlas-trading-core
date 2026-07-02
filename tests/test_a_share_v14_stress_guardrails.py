from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_stress_scenarios_and_guardrails_are_simulated(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    stress = v14_json(paths, "v14_stress_scenario_result")
    guardrail = v14_json(paths, "v14_risk_limit_guardrail_result")

    assert result["stress_scenario_result_generated"] is True
    assert result["risk_limit_guardrail_result_generated"] is True
    assert stress["risk_off_trigger_simulation"] is True
    assert stress["freeze_trigger_simulation"] is True
    assert stress["rollback_trigger_simulation"] is True
    assert stress["real_world_prediction_claimed"] is False
    assert guardrail["blocked_allocation_decision"] is True
    assert guardrail["blocked_rebalance_decision"] is True
    assert guardrail["guard_action_is_simulated"] is True
    assert guardrail["guard_action_triggers_real_trading"] is False
