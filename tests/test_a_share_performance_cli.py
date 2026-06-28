from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_performance_test_utils import make_performance_paths


def test_performance_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_performance_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_multi_day_performance",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "performance_config": {"mode": "current_snapshot"},
            "performance_data_availability": {
                "portfolio_observation_counts": {"long_virtual_portfolio": 1, "mid_virtual_portfolio": 1, "short_virtual_portfolio": 1},
                "sufficient_history": False,
            },
            "performance_summary": {
                "performance_not_yet_observed": True,
                "recommended_next_version": "v0.7.12-a-share-performance-attribution-and-risk-diagnostics",
            },
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_multi_day_performance",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "observation_checks": {"long_virtual_portfolio": 1},
            "series_checks": {"math_checks_passed": True},
            "recommended_next_version": "v0.7.12-a-share-performance-attribution-and-risk-diagnostics",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-multi-day-performance", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-multi-day-performance", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-multi-day-performance", "--as-of-date", AS_OF_DATE]) == 0
