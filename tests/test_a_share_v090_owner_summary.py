from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_owner_summary_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    summary = v090_data(paths, "v090_owner_release_summary.json")
    assert summary["summary_id"] == "A-SHARE-OWNER-V090-RC-RELEASE-SUMMARY"
    assert summary["known_owner_readiness_state"] == "blocked"
    assert summary["new_gate_score_generated"] is False
