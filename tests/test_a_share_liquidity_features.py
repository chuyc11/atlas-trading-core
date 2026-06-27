from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_frame, make_feature_paths


def test_liquidity_features_cover_amount_volume_and_effective_days(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    frame = feature_frame(paths, "liquidity")
    row = frame.set_index("symbol").loc["600001.SH"]

    assert row["avg_amount_20d"] > 0
    assert row["avg_volume_60d"] > 0
    assert row["zero_volume_days_60d"] == 0
    assert row["effective_trading_days_20d"] == 20
    assert row["estimated_slippage_proxy_20d"] > 0
