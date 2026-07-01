from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_automated_experiments, run_a_share_v09_daily_platform


def test_v09_automated_experiments_are_simulation_only(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    result = run_a_share_automated_experiments(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    artifact = platform_json(paths, "v09_automated_experiment_result")

    assert result["overall_passed"] is True
    assert artifact["automated_experiments_run"] is True
    assert artifact["auto_promoted_to_real_trading"] is False
    assert artifact["not_real_order"] is True
