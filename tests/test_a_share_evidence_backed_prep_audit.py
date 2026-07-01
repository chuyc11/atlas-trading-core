from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_outputs
from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_backed_prep_audit import audit_a_share_owner_evidence_backed_reevaluation_prep


def test_evidence_backed_prep_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_outputs(paths)
    passed = audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    assert passed["prep_checks"]["reevaluation_input_package_generated"] is True
    assert passed["prep_checks"]["new_gate_decision_generated"] is False
    (paths.data_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / AS_OF_DATE / "evidence_backed_prep_manifest.json").unlink()
    failed = audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]

