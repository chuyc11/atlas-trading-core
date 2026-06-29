from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_inputs
from trading_core.equity_build_output_dashboard.input_availability import build_input_availability


def test_build_output_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_inputs(paths)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["repeatability_audit_passed"] is True


def test_build_output_input_availability_fails_missing(tmp_path):
    paths = make_paths(tmp_path)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False

