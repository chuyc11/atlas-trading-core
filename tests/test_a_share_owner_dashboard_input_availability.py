from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.input_availability import build_dashboard_input_availability


def test_input_availability_passes_for_seeded_inputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    result = build_dashboard_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert {row["input_group"] for row in result["input_groups"]} >= {"current_day_run", "data_refresh", "workflow"}
