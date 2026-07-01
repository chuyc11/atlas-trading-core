from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_closeout_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    manifest = closeout_data(paths, "closeout_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-CLOSEOUT-REVIEW-MANIFEST"
    assert manifest["v090_full_regression_plan_generated"] is True
    assert manifest["full_pytest_run"] is False
