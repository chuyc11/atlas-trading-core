from tests.a_share_v0820_test_utils import make_paths, seed_v0820_outputs, v0820_data


def test_v0820_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_outputs(paths)
    manifest = v0820_data(paths, "v0820_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-V0820-GATE-OUTCOME-MANIFEST"
    assert manifest["selected_branch"] == "final_blocked_closeout"
    assert manifest["full_pytest_run"] is False

