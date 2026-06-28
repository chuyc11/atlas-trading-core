from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_risk_bucket_blocks_risk_downgraded_holdings(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "risk_bucket_contribution_snapshot")
    assert payload["risk_downgraded_symbols_in_portfolio"] == []
    assert payload["risk_downgraded_exposure"] == 0
