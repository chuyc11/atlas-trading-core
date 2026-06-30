from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths, seed_controlled_gate_reevaluation_outputs
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_reevaluation_audit import audit_a_share_owner_controlled_gate_reevaluation


def test_controlled_gate_reevaluation_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_outputs(paths)
    passed = audit_a_share_owner_controlled_gate_reevaluation(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    assert passed["reevaluation_checks"]["controlled_reevaluation_decision"] == "skipped_not_ready"
    (paths.data_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / AS_OF_DATE / "controlled_reevaluation_manifest.json").unlink()
    failed = audit_a_share_owner_controlled_gate_reevaluation(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]

