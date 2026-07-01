from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_developer_follow_up_evidence_package_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    package = recovery_evidence_data(paths, "developer_follow_up_evidence_package.json")
    assert package["package_id"] == "A-SHARE-DEVELOPER-FOLLOW-UP-EVIDENCE-PACKAGE"
    assert package["follow_up_count"] == 1
    assert package["items"][0]["status"] == "planned"

