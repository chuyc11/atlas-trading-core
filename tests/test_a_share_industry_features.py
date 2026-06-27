from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_industry_features_keep_allowed_industry_rank_as_atomic_feature(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "industry")
    finance = frame.set_index("symbol").loc["600001.SH"]
    rank_columns = [column for column in frame.columns if "rank" in column.lower()]

    assert finance["industry_level_1"] == "Finance"
    assert finance["industry_member_count"] == 2
    assert finance["stock_rank_in_industry_by_return_20d"] in {1, 2}
    assert set(rank_columns) == {
        "stock_rank_in_industry_by_return_20d",
        "stock_rank_in_industry_by_return_60d",
        "stock_rank_in_industry_by_return_120d",
    }
