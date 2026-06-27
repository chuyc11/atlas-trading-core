from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_score_test_utils import make_score_paths


def test_scoring_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_score_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_scores",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "strict_tradable_count": 3,
            "scored_symbols": 3,
            "warnings": [],
            "artifacts": {"score_manifest": "m"},
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_scores",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {"strict_tradable_count": 3, "scored_symbols": 3},
            "score_ranges": {},
            "recommended_next_version": "v0.7.5-a-share-candidate-generation-system",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-scores", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-scores", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-scores", "--as-of-date", AS_OF_DATE]) == 0
