from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_history_refresh_does_not_fabricate_dates(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    payload = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_history_refresh.json")
    assert payload["ops_history_refresh_performed"] is True
    assert payload["synthetic_history_used"] is False
    assert payload["future_dates_used"] is False
    assert payload["observation_dates"] == [AS_OF_DATE]

