from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, portfolio_json, relaxed_portfolio_config


def test_virtual_portfolio_manifest_records_boundary_and_counts(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    manifest = portfolio_json(paths, "portfolio_manifest")

    assert manifest["manifest_id"] == "A-SHARE-VIRTUAL-PORTFOLIO-MANIFEST"
    assert manifest["portfolios"]["long_virtual_portfolio"]["holdings"] == 2
    assert manifest["portfolios"]["mid_virtual_portfolio"]["weight_sum"] == 1.0
    assert manifest["virtual_portfolio_generated"] is True
    assert manifest["real_portfolio_generated"] is False
    assert manifest["broker_connected"] is False

