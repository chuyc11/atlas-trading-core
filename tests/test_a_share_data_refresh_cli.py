from __future__ import annotations

from pathlib import Path

import pytest

from a_share_feature_test_utils import AS_OF_DATE
from a_share_data_refresh_test_utils import make_data_refresh_paths


def test_data_refresh_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_data_refresh_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_daily_data_refresh",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "data_refresh_config": {"mode": "validate_existing_data"},
            "date_resolution": {"resolved_as_of_date": AS_OF_DATE},
            "dataset_schema_validation": {"schema_validation_status": "passed"},
            "dataset_freshness_validation": {"freshness_validation_status": "passed"},
            "dataset_coverage_summary": {"coverage_validation_status": "passed"},
            "data_refresh_summary": {"recommended_next_version": "v0.8.1-a-share-current-day-research-workflow-runner"},
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_daily_data_refresh",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "dataset_checks": {},
            "provider_checks": {},
            "validation_checks": {},
            "recommended_next_version": "v0.8.1-a-share-current-day-research-workflow-runner",
            "json_path": "j",
            "report_path": "r",
        },
    )
    assert cli.main(["build-a-share-daily-data-refresh", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-daily-data-refresh", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-daily-data-refresh", "--as-of-date", AS_OF_DATE]) == 0
