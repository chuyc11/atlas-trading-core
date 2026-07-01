from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_operator_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    manifest = operator_data(paths, "operator_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-OPERATOR-EXPERIENCE-MANIFEST"
    assert manifest["full_pytest_run"] is False
