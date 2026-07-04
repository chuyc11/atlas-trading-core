from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v25_quality_closeout_full_regression_flags_and_safety(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v25")
    spec, result, audit = build_release(paths, "v25")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v24_baseline_verified"] is True
    assert result["full_regression_evidence_generated"] is True
    assert result["full_pytest_run"] is True
    assert result["full_pytest_passed"] is True
    assert result["fabricated_test_result"] is False
    assert result["live_trading_ready"] is False
    assert len(spec["json_names"]) == 12
    assert len(spec["markdown_names"]) == 7
