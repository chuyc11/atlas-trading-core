from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_rl_simulated_strategy_lab, run_a_share_v09_daily_platform


def test_v09_rl_simulated_strategy_lab_targets_only_simulated_objects(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    result = run_a_share_rl_simulated_strategy_lab(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    lab = platform_json(paths, "v09_rl_simulated_strategy_lab_result")

    assert result["overall_passed"] is True
    assert lab["market_environment"] == "offline_a_share_public_data_simulation"
    assert set(lab["allowed_targets"]) == {"rl_shadow_strategy", "rl_simulated_account", "rl_virtual_portfolio"}
    assert lab["real_account_action_generated"] is False
    assert lab["not_live_trading_ready"] is True
