from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v33_report_query_index_uses_real_report_links_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v33")
    report = component_json(paths, "v33", "v33_report_query_index_result")

    assert result["v32_baseline_verified"] is True
    assert result["report_query_index_generated"] is True
    assert result["report_links_fabricated"] is False
    assert report["artifact_generated"] is True
