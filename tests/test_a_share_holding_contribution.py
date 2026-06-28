from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_holding_contribution_does_not_fabricate_realized_performance(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths, mode="single_day_initialization_attribution")
    payload = attribution_json(paths, "holding_contribution_snapshot")
    assert payload["records"]
    assert {row["contribution_status"] for row in payload["records"]} == {"insufficient_history"}
    assert all(row["not_order_instruction"] is True for row in payload["records"])
