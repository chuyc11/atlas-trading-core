from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_industry_contribution_weights_reconcile(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    holding = attribution_json(paths, "holding_contribution_snapshot")
    industry = attribution_json(paths, "industry_contribution_snapshot")
    for portfolio_id, expected in holding["portfolio_weight_sums"].items():
        assert abs(sum(row["weight"] for row in industry["portfolios"][portfolio_id]) - expected) < 1e-6
