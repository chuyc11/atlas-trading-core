from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_evidence_insufficiency_lineage_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    lineage = closeout_data(paths, "evidence_insufficiency_lineage.json")
    assert lineage["overall_passed"] is True
    assert lineage["evidence_insufficient"] is True
    assert lineage["blocking_gap_count"] == 5
