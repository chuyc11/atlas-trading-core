from tests.a_share_gated_build_test_utils import seed_gated_build_inputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.date_alignment import build_gated_build_date_alignment


def test_gated_build_date_alignment_blocks_mismatch(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    write_json(paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json", {"overall_passed": True, "as_of_date": "2026-06-25"})
    result = build_gated_build_date_alignment(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
    assert result["blocking_reasons"]

