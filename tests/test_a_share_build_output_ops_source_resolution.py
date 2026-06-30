from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.input_availability import build_input_availability
from trading_core.equity_build_output_ops_refresh.source_resolution import build_source_resolution


def test_build_output_ops_source_resolution_prefers_build_output_and_blocks_missing(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["overall_passed"] is True
    assert result["primary_sources"]["build_output_dashboard_summary"]["source_workflow_mode"] == "build_from_existing_data"
    (paths.data_dir / "equity_build_output_dashboard" / "daily" / AS_OF_DATE / "build_output_dashboard_summary.json").unlink()
    failed = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert failed["overall_passed"] is False

