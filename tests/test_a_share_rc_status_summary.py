from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_rc_status_summary_uses_v090_truth(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    summary = operator_data(paths, "rc_status_summary.json")
    assert summary["v090_rc_audit_passed"] is True
    assert summary["known_owner_readiness_state"] == "blocked"
