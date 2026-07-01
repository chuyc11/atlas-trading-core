from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_v09_daily_platform


def test_v09_daily_platform_run_and_dry_run(tmp_path):
    paths = seed_v09_inputs(tmp_path)

    dry = run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True, dry_run=True)
    assert dry["overall_passed"] is True
    assert dry["public_data_refresh_status"] == "skipped"

    result = run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    workflow = platform_json(paths, "v09_daily_workflow_result")
    assert result["run_status"] == "passed"
    assert workflow["daily_platform_run"] is True
    assert workflow["public_data_refresh_status"] == "passed"
    assert workflow["research_pipeline_status"] == "passed"
    assert workflow["owner_readiness_gate_rerun"] is False


def test_v09_daily_platform_requires_simulation_only(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    result = run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=False)
    assert result["overall_passed"] is False
    assert result["blocking_reasons"] == ["simulation_only_flag_required"]
