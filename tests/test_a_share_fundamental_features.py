from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_fundamental_features_cover_market_cap_and_financial_history(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "fundamental")
    row = frame.set_index("symbol").loc["600001.SH"]

    assert row["pe_ttm"] > 0
    assert row["total_mv"] > row["circ_mv"]
    assert row["revenue_growth_yoy"] > 0
    assert row["net_profit_growth_yoy"] > 0
    assert row["financial_quarters_available"] >= 20
    assert row["financial_report_age_days"] > 0
