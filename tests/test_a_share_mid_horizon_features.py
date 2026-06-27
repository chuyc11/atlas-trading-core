from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_mid_horizon_features_cover_ma_trend_and_relative_strength(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "mid_horizon")
    row = frame.set_index("symbol").loc["600002.SH"]

    assert row["ma_60"] > 0
    assert row["close_to_ma_60"] > 0
    assert row["trend_consistency_120d"] == 1.0
    assert row["relative_strength_60d_vs_market"] is not None
    assert row["volatility_adjusted_return_120d"] > 0
