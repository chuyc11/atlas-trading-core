from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import make_feature_paths


def test_multi_horizon_feature_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_feature_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_multi_horizon_features",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": "2026-06-26",
            "strict_tradable_count": 3,
            "feature_groups": {},
            "warnings": [],
            "feature_manifest_path": "m",
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_multi_horizon_features",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {"strict_tradable_count": 3},
            "coverage": {},
            "recommended_next_version": "v0.7.4-a-share-long-mid-short-scoring-system",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-multi-horizon-features", "--as-of-date", "2026-06-26"]) == 0
    assert cli.main(["audit-a-share-multi-horizon-features", "--as-of-date", "2026-06-26"]) == 0
    assert cli.main(["build-and-audit-a-share-multi-horizon-features", "--as-of-date", "2026-06-26"]) == 0
