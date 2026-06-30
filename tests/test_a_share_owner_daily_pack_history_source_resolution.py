from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_inputs
from trading_core.equity_owner_daily_pack_history.input_availability import build_input_availability
from trading_core.equity_owner_daily_pack_history.source_resolution import build_source_resolution


def test_owner_daily_pack_history_source_resolution_prefers_daily_pack(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["primary_sources"]["daily_pack_manifest"]["source_role"] == "primary_owner_daily_pack"


def test_owner_daily_pack_history_source_resolution_blocks_missing_source(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_inputs(paths)
    (paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "daily_pack_manifest.json").unlink()
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert resolution["overall_passed"] is False
    assert "missing_required_history_source:daily_pack_manifest" in resolution["blocking_reasons"]
