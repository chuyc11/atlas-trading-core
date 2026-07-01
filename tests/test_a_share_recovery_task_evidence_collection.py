from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_recovery_task_evidence_collection_records_missing_without_completion(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    collection = recovery_evidence_data(paths, "recovery_task_evidence_collection.json")
    assert collection["task_count"] == 3
    assert collection["completion_claim_allowed_count"] == 0
    assert collection["task_completion_not_fabricated"] is True
    assert all(item["evidence_quality"] == "none" for item in collection["items"])

