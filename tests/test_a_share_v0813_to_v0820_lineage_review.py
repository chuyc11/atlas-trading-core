from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v0813_to_v0820_lineage_review_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    lineage = closeout_data(paths, "v0813_to_v0820_lineage_review.json")
    assert lineage["stage_count"] == 8
    assert lineage["blocked_state_visible"] is True
    assert lineage["readiness_score_visible"] is True
    assert lineage["minimum_threshold_visible"] is True
