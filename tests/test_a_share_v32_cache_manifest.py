from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v32_cache_manifest_is_research_only_and_non_stale(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")
    cache = component_json(paths, "v32", "v32_cache_manifest_result")

    assert result["cache_manifest_result_generated"] is True
    assert result["cache_result_fabricated"] is False
    assert result["cache_reused_stale_artifact"] is False
    assert cache["cache_scope"] == "research_artifacts_only"
    assert "source version" in cache["cache_reproducibility_note"]
