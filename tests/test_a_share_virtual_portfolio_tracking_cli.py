from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_tracking_test_utils import make_tracking_paths


def test_virtual_portfolio_tracking_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_tracking_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_virtual_portfolio_tracking",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "tracking_summary": {
                "counts": {
                    "long_holdings": 2,
                    "mid_holdings": 2,
                    "short_holdings": 2,
                    "long_ledger_records": 2,
                    "mid_ledger_records": 2,
                    "short_ledger_records": 2,
                },
                "first_day_initialization": True,
                "performance_not_yet_observed": True,
            },
            "recommended_next_version": "v0.7.9-a-share-daily-workflow-orchestration",
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_virtual_portfolio_tracking",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {
                "long_holdings": 2,
                "mid_holdings": 2,
                "short_holdings": 2,
                "long_ledger_records": 2,
                "mid_ledger_records": 2,
                "short_ledger_records": 2,
            },
            "nav_checks": {"long_nav": 1_000_000.0, "mid_nav": 1_000_000.0, "short_nav": 1_000_000.0},
            "recommended_next_version": "v0.7.9-a-share-daily-workflow-orchestration",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-virtual-portfolio-tracking", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-virtual-portfolio-tracking", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-virtual-portfolio-tracking", "--as-of-date", AS_OF_DATE]) == 0
