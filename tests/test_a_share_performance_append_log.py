from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_append_mode_is_idempotent_for_identical_current_date(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    build_performance_package(paths)
    result = build_performance_package(paths, mode="append_from_existing_tracking")
    append_log = result["performance_append_log"]
    assert append_log["append_only"] is True
    assert append_log["prior_dates_rewritten"] is False
    assert "2026-06-26" in append_log["existing_dates"]
    assert append_log["idempotent_dates"]
