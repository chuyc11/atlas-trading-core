from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import evaluate_a_share_simulated_strategy_promotion, run_a_share_v09_daily_platform


def test_v09_shadow_canary_promotion_is_simulated_only_and_blocks_real_path(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    result = evaluate_a_share_simulated_strategy_promotion(paths=paths, as_of_date=AS_OF_DATE)
    promotion = platform_json(paths, "v09_shadow_canary_promotion_result")

    assert result["overall_passed"] is True
    assert promotion["shadow_canary_promotion_evaluated"] is True
    assert promotion["real_trading_promotion"] is False
    assert promotion["rejection_reason"] == "cooldown_not_satisfied"
    assert promotion["forbidden_workflow"] == ["simulated_active", "real trading"]
