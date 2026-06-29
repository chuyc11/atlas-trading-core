from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_outputs
from trading_core.equity_build_output_dashboard.build_output_dashboard_audit import audit_a_share_build_output_owner_dashboard
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import artifact_paths
from tests.a_share_owner_dashboard_test_utils import write_json


def test_build_output_dashboard_audit_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_outputs(paths)
    audit = audit_a_share_build_output_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True


def test_build_output_dashboard_audit_fails_protected_modification(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_outputs(paths)
    artifacts = artifact_paths(paths, AS_OF_DATE)
    payload = {"target_version": "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh", "protected_path_modifications_detected": True}
    write_json(artifacts["build_output_input_availability"], payload)
    audit = audit_a_share_build_output_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False

