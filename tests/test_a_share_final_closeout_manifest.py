from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_final_closeout_manifest_generated_with_hashes(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    manifest = final_json(paths, "final_closeout_manifest")

    assert manifest["selected_branch"] == "final_not_ready_closeout"
    assert manifest["final_closeout_decision"] == "not_ready_additional_evidence_required"
    assert manifest["overall_passed"] is True
    assert manifest["source_version"].startswith("v0.9.5")
    assert "closeout_request" in manifest["output_artifacts"]
    assert isinstance(manifest["artifact_hashes"], dict)
