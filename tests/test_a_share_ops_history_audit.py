from tests.a_share_ops_history_test_utils import build_ops_history_artifacts
from tests.a_share_owner_dashboard_test_utils import make_paths


def test_ops_history_audit_passes_for_single_real_run(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_ops_history_artifacts(paths)
    assert audit["overall_passed"] is True
    assert audit["trend_sufficiency"]["run_history_observation_count"] == 1
    assert audit["trend_sufficiency"]["baseline_status"] == "insufficient_history"

