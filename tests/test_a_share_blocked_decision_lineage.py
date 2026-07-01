from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_blocked_decision_lineage_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    lineage = closeout_data(paths, "blocked_decision_lineage.json")
    assert lineage["overall_passed"] is True
    assert lineage["blocked_decision_preserved"] is True
    assert all(row["source_gate_decision"] == "blocked" for row in lineage["stages"])
