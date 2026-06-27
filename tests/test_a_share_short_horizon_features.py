from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_short_horizon_features_include_recent_returns_without_scores(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "short_horizon")
    row = frame.set_index("symbol").loc["600001.SH"]

    assert len(frame) == 3
    assert row["feature_group"] == "short_horizon"
    assert row["return_20d"] == pytest.approx(row["momentum_20d"])
    assert row["effective_trading_days_20d"] if "effective_trading_days_20d" in frame.columns else True
    assert not any("score" in column.lower() or "signal" in column.lower() for column in frame.columns)
