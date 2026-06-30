from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.input_availability import build_input_availability
from trading_core.equity_owner_daily_pack.source_resolution import build_source_resolution


def test_owner_daily_pack_source_resolution_prefers_ops_refresh(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)

    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)

    assert resolution["overall_passed"] is True
    assert resolution["fallback_used"] is False
    assert resolution["primary_sources"]["build_output_ops_refresh_audit"]["source_role"] == "primary_build_output_ops_refresh"


def test_owner_daily_pack_source_resolution_blocks_missing_required_source(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    (paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_summary.json").unlink()
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)

    resolution = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)

    assert resolution["overall_passed"] is False
    assert "missing_required_daily_pack_source:build_output_ops_summary" in resolution["blocking_reasons"]
