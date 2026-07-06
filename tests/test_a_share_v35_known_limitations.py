from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v35_known_limitations_are_not_hidden_or_waived(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")

    assert result["known_limitations_refresh_generated"] is True
    assert result["known_limitations_hidden"] is False
    assert result["waiver_applied"] is False
    assert result["threshold_lowered"] is False
