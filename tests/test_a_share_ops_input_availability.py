from tests.a_share_ops_center_test_utils import seed_ops_inputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_ops_center.input_availability import build_ops_input_availability


def test_ops_input_availability_passes_seeded_inputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_ops_inputs(paths)
    result = build_ops_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["required_modules_available"] is True


def test_ops_input_availability_fails_missing_inputs(tmp_path):
    paths = make_paths(tmp_path)
    result = build_ops_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
    assert result["blocking_reasons"]
