from __future__ import annotations

from pathlib import Path

import pytest

from a_share_selection_test_utils import make_tradable_universe_paths


def test_tradable_universe_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_tradable_universe_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_tradable_universe",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": "2026-06-26",
            "counts": {"strict_tradable_count": 2},
            "warnings": [],
            "artifacts": {"tradable_universe_json": "t", "manifest": "m"},
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_tradable_universe",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {"strict_tradable_count": 2},
            "recommended_next_version": "v0.7.3-a-share-multi-horizon-feature-engineering",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-tradable-universe", "--as-of-date", "2026-06-26", "--include-caution", "false"]) == 0
    assert cli.main(["audit-a-share-tradable-universe", "--as-of-date", "2026-06-26"]) == 0
    assert cli.main(["build-and-audit-a-share-tradable-universe", "--as-of-date", "2026-06-26"]) == 0

