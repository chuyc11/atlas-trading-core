from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.build_output_ops_audit import audit_a_share_build_output_ops_refresh


def test_build_output_ops_audit_pass_and_fail(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    result = audit_a_share_build_output_ops_refresh(as_of_date=AS_OF_DATE, paths=paths)
    assert result["overall_passed"] is True
    assert result["refresh_checks"]["automatic_action_count"] == 0
    (paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_monitoring_refresh.json").unlink()
    failed = audit_a_share_build_output_ops_refresh(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]

