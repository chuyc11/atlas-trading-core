from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_warning_mapping_evidence_package_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    package = recovery_evidence_data(paths, "warning_mapping_evidence_package.json")
    assert package["package_id"] == "A-SHARE-WARNING-MAPPING-EVIDENCE-PACKAGE"
    assert package["warning_count"] == 2
    assert package["known_non_blocking_warning_count"] == 2

