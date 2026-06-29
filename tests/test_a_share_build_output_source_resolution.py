from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_inputs
from trading_core.equity_build_output_dashboard.input_availability import build_input_availability
from trading_core.equity_build_output_dashboard.source_resolution import build_source_resolution


def test_source_resolution_prefers_build_output(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["source_workflow_mode"] == "build_from_existing_data"
    assert result["required_validate_fallback_used"] is False


def test_source_resolution_blocks_required_fallback(tmp_path):
    paths = make_paths(tmp_path)
    availability = {"overall_passed": False}
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["overall_passed"] is False

