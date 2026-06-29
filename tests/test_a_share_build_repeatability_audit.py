from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, seed_repeatability_outputs
from trading_core.equity_build_repeatability.repeatability_audit import audit_a_share_build_repeatability
from trading_core.equity_build_repeatability.repeatability_config import repeatability_artifact_paths


def test_repeatability_audit_passes_for_seeded_outputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_repeatability_outputs(paths)
    result = audit_a_share_build_repeatability(as_of_date=AS_OF_DATE, paths=paths)
    assert result["overall_passed"] is True


def test_repeatability_audit_fails_protected_modification(tmp_path):
    paths = make_paths(tmp_path)
    seed_repeatability_outputs(paths)
    artifacts = repeatability_artifact_paths(paths, AS_OF_DATE)
    payload = {"protected_path_modifications_detected": True, "new_protected_paths_created": [], "protected_files_modified": ["data/orders/x"], "protected_files_created": [], "protected_files_deleted": []}
    from tests.a_share_owner_dashboard_test_utils import write_json
    write_json(artifacts["protected_path_modification_check"], payload)
    result = audit_a_share_build_repeatability(as_of_date=AS_OF_DATE, paths=paths)
    assert result["overall_passed"] is False

