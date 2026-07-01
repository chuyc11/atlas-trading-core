from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_quality_issue_evidence_package_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    package = recovery_evidence_data(paths, "quality_issue_evidence_package.json")
    assert package["package_id"] == "A-SHARE-QUALITY-ISSUE-EVIDENCE-PACKAGE"
    assert package["quality_issue_count"] == 3
    assert any(item["requires_developer_follow_up"] for item in package["items"])

