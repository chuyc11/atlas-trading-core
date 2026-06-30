from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.input_availability import build_input_availability


def test_build_output_ops_input_availability_pass_and_fail(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["build_output_dashboard_audit_passed"] is True
    (paths.data_dir / "equity_data_quality" / "a_share_owner_monitoring_audit.json").unlink()
    failed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "missing_required_input:monitoring_audit" in failed["blocking_reasons"]

