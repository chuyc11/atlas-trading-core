from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_test_utils import make_portfolio_paths


def test_virtual_portfolio_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_portfolio_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_virtual_portfolios",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "long_virtual_portfolio": [{}, {}],
            "mid_virtual_portfolio": [{}, {}],
            "short_virtual_portfolio": [{}, {}],
            "warnings": [],
            "recommended_next_version": "v0.7.7-a-share-daily-stock-selection-briefing",
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_virtual_portfolios",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "counts": {"long_holdings": 2, "mid_holdings": 2, "short_holdings": 2},
            "weight_checks": {"long_weight_sum": 1.0, "mid_weight_sum": 1.0, "short_weight_sum": 1.0},
            "recommended_next_version": "v0.7.7-a-share-daily-stock-selection-briefing",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-virtual-portfolios", "--as-of-date", AS_OF_DATE, "--long-holdings", "2", "--mid-holdings", "2", "--short-holdings", "2"]) == 0
    assert cli.main(["audit-a-share-virtual-portfolios", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-virtual-portfolios", "--as-of-date", AS_OF_DATE]) == 0

