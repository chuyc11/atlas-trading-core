from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_original_ops_vs_build_output_ops_comparison_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    payload = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "original_ops_vs_build_output_ops_comparison.json")
    assert payload["comparison_completed"] is True
    assert payload["build_output_source_workflow_mode"] == "build_from_existing_data"

