from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_rc_scope_proposal_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    proposal = closeout_data(paths, "v090_rc_scope_proposal.json")
    assert proposal["proposal_id"] == "A-SHARE-V090-RC-SCOPE-PROPOSAL"
    assert proposal["blocked_owner_readiness_state_acceptable_for_rc"] is True
    assert "owner_readiness_remains_blocked" in proposal["known_blocked_states"]
