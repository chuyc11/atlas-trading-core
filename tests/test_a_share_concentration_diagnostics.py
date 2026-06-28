from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_concentration_diagnostics_math(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "portfolio_concentration_diagnostics")
    for row in payload["portfolios"].values():
        assert row["herfindahl_index"] > 0
        assert row["effective_number_of_holdings"] > 0
        assert row["top_5_weight"] >= row["max_single_weight"]
