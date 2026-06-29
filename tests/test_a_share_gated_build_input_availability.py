from tests.a_share_gated_build_test_utils import seed_gated_build_inputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day_builds.input_availability import build_gated_build_input_availability


def test_gated_build_input_availability_passes_with_required_inputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    result = build_gated_build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["missing_inputs"] == []

