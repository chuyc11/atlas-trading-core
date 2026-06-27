from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_long_horizon_features_cover_250d_and_5y_windows(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "long_horizon")
    row = frame.set_index("symbol").loc["600001.SH"]

    assert row["return_250d"] > 0
    assert row["return_3y"] > 0
    assert row["return_5y"] > 0
    assert row["max_drawdown_250d"] == 0
    assert row["long_trend_consistency_250d"] == 1.0
