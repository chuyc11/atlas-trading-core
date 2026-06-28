from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_performance_test_utils import make_performance_paths


def test_attribution_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_performance_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_performance_attribution",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "attribution_config": {"mode": "current_exposure_diagnostics"},
            "attribution_data_availability": {"limited_history": True, "structural_diagnostics_available": True, "realized_performance_attribution_available": False},
            "attribution_summary": {"recommended_next_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening"},
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_performance_attribution",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "availability_checks": {},
            "reconciliation_checks": {},
            "risk_checks": {},
            "recommended_next_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening",
            "json_path": "j",
            "report_path": "r",
        },
    )
    assert cli.main(["build-a-share-performance-attribution", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-performance-attribution", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-performance-attribution", "--as-of-date", AS_OF_DATE]) == 0
