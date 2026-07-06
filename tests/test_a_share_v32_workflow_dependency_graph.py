from a_share_v3x_release_test_utils import assert_common_boundary, build_through, component_json, make_v3x_paths


def test_v32_workflow_dependency_graph_generated(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")
    graph = component_json(paths, "v32", "v32_workflow_dependency_graph")

    assert result["v31_baseline_verified"] is True
    assert result["workflow_dependency_graph_generated"] is True
    assert graph["artifact_generated"] is True
    assert graph["semantic_outputs_changed"] is False
    assert_common_boundary(result)
