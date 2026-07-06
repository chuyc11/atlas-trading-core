from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v33_warning_blocker_limitation_search_keeps_blockers_visible(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v33")

    assert result["warning_blocker_limitation_search_generated"] is True
    assert result["knowledge_base_fabricated"] is False
    assert result["blocking_reasons"] == []
    assert result["warnings"] == []
