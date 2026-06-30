from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, seed_recovery_execution_outputs
from trading_core.equity_owner_readiness_recovery_execution.recovery_execution_audit import audit_a_share_owner_readiness_recovery_execution


def test_recovery_execution_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    passed = audit_a_share_owner_readiness_recovery_execution(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    (paths.data_dir / "equity_owner_readiness_recovery_execution" / "daily" / AS_OF_DATE / "recovery_execution_manifest.json").unlink()
    failed = audit_a_share_owner_readiness_recovery_execution(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]
