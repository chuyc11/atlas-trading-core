from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_readiness_score_lineage_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    lineage = closeout_data(paths, "readiness_score_lineage.json")
    assert lineage["overall_passed"] is True
    assert lineage["score_gap"] == lineage["minimum_owner_readiness_score"] - lineage["previous_readiness_score"]
