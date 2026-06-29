from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_remediation_test_utils import build_remediation_artifacts, seed_remediation_inputs
from trading_core.equity_owner_remediation.remediation_audit import audit_a_share_owner_remediation


def test_owner_remediation_audit_passes_generated_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_remediation_artifacts(paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["remediation_checks"]["automatic_action_count"] == 0


def test_owner_remediation_audit_fails_without_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    seed_remediation_inputs(paths)
    audit = audit_a_share_owner_remediation(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert audit["blocking_reasons"]
