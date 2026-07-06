from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v34_factor_sector_attribution_records_limitations(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")
    factor = component_json(paths, "v34", "v34_factor_sector_industry_attribution_result")

    assert result["factor_sector_industry_attribution_generated"] is True
    assert result["factor_attribution_fabricated"] is False
    assert factor["unsupported_metrics_recorded_as_limitations"] is True
