from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import build_a_share_experiment_registry, run_a_share_v09_daily_platform


def test_v09_experiment_and_strategy_registry_exclude_real_trading_active(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    build = build_a_share_experiment_registry(paths=paths, as_of_date=AS_OF_DATE)
    assert build["overall_passed"] is True
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)

    experiments = platform_json(paths, "v09_experiment_registry")
    strategies = platform_json(paths, "v09_strategy_registry")
    assert experiments["experiment_count"] >= 1
    assert all(item["status"] == "pending_experiment" for item in experiments["experiments"])
    assert "real_trading_active" in strategies["forbidden_statuses"]
    assert all(item["status"] != "real_trading_active" for item in strategies["strategies"])
