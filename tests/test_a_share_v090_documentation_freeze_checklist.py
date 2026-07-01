from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_documentation_freeze_checklist_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    checklist = closeout_data(paths, "v090_documentation_freeze_checklist.json")
    items = {item["item"] for item in checklist["items"]}
    assert "owner-readiness blocked state documented" in items
    assert "no live trading claims" in items
