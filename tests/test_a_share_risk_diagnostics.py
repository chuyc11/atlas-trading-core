from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_risk_diagnostics_flags(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "risk_diagnostics_snapshot")
    assert payload["risk_downgraded_symbols_in_portfolio"] == []
    assert all("diagnostic_flags" in row for row in payload["portfolios"].values())
