from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_center_refresh_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    payload = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_center_refresh.json")
    assert payload["ops_center_refresh_performed"] is True
    assert payload["automatic_action_count"] == 0

