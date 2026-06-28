from __future__ import annotations

from pathlib import Path

import pytest

from a_share_daily_stock_selection_briefing_test_utils import make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE


def test_daily_stock_selection_briefing_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_briefing_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_daily_stock_selection_briefing",
        lambda **_: {
            "briefing_id": "b",
            "as_of_date": AS_OF_DATE,
            "long_candidates_top10": [{}],
            "mid_candidates_top10": [{}],
            "short_candidates_top10": [{}],
            "source_trace_complete": True,
            "recommended_next_version": "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger",
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_daily_stock_selection_briefing",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "required_sections": {"executive_summary": True},
            "checks": {"source_trace_complete": True},
            "recommended_next_version": "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-daily-stock-selection-briefing", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-daily-stock-selection-briefing", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-daily-stock-selection-briefing", "--as-of-date", AS_OF_DATE]) == 0
