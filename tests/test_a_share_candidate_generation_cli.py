from __future__ import annotations

from pathlib import Path

import pytest

from a_share_candidate_test_utils import make_candidate_paths
from a_share_feature_test_utils import AS_OF_DATE


def test_candidate_generation_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_candidate_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "generate_a_share_candidates",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "candidate_counts": {"long_candidates": 1, "mid_candidates": 1, "short_candidates": 1},
            "warnings": [],
            "recommended_next_version": "v0.7.6-a-share-virtual-portfolio-construction",
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_candidates",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {"long_candidates": 1, "mid_candidates": 1, "short_candidates": 1},
            "recommended_next_version": "v0.7.6-a-share-virtual-portfolio-construction",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["generate-a-share-candidates", "--as-of-date", AS_OF_DATE, "--long-count", "1", "--mid-count", "1", "--short-count", "1"]) == 0
    assert cli.main(["audit-a-share-candidates", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["generate-and-audit-a-share-candidates", "--as-of-date", AS_OF_DATE]) == 0
