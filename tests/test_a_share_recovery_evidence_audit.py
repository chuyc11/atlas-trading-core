from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths, seed_recovery_evidence_outputs
from trading_core.equity_owner_recovery_evidence.recovery_evidence_audit import audit_a_share_owner_recovery_evidence


def test_recovery_evidence_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    passed = audit_a_share_owner_recovery_evidence(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    assert passed["evidence_checks"]["new_gate_score_generated"] is False
    (paths.data_dir / "equity_owner_recovery_evidence" / "daily" / AS_OF_DATE / "recovery_evidence_manifest.json").unlink()
    failed = audit_a_share_owner_recovery_evidence(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]

