from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.input_availability import build_input_availability


def test_owner_daily_pack_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)

    assert availability["overall_passed"] is True
    assert availability["build_output_ops_refresh_audit_passed"] is True
    assert availability["build_output_dashboard_audit_passed"] is True
    assert availability["repeatability_audit_passed"] is True
    assert availability["gated_build_audit_passed"] is True


def test_owner_daily_pack_input_availability_fails_closed_without_ops_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    (paths.data_dir / "equity_data_quality" / "a_share_build_output_ops_refresh_audit.json").unlink()

    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)

    assert availability["overall_passed"] is False
    assert "build_output_ops_refresh_audit_not_passed" in availability["blocking_reasons"]
