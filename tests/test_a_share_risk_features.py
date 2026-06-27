from __future__ import annotations

from pathlib import Path

import numpy as np

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_risk_features_are_finite_and_past_window_based(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "risk")
    row = frame.set_index("symbol").loc["600001.SH"]
    numeric = frame.select_dtypes(include=["number"]).to_numpy(dtype=float)

    assert row["volatility_20d"] > 0
    assert row["max_drawdown_120d"] == 0
    assert row["large_drop_days_60d"] == 0
    assert np.isfinite(numeric[~np.isnan(numeric)]).all()
