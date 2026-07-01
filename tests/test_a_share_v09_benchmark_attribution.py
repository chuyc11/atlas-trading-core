from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_v09_daily_platform


def test_v09_benchmark_attribution_records_missing_benchmark_warning_without_fabrication(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    benchmark = platform_json(paths, "v09_benchmark_attribution_result")

    assert benchmark["benchmark_attribution_status"] == "warning"
    assert benchmark["benchmark_data_present"] is False
    assert benchmark["excess_return"] is None
    assert "benchmark_data_missing_recorded_without_fabrication" in benchmark["warnings"]
    assert benchmark["not_buy_sell_signal"] is True
