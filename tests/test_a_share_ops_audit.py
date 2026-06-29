from tests.a_share_ops_center_test_utils import build_ops_artifacts, seed_ops_inputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_ops_center.ops_audit import audit_a_share_daily_ops_center


def test_ops_audit_passes_generated_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_ops_artifacts(paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []


def test_ops_audit_fails_without_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    seed_ops_inputs(paths)
    audit = audit_a_share_daily_ops_center(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert audit["blocking_reasons"]
