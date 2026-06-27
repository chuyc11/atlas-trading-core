from __future__ import annotations

from pathlib import Path

import pytest

from a_share_historical_test_utils import make_history_paths


def test_a_share_historical_backfill_cli_smoke_no_network_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_history_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(cli, "backfill_a_share_daily_price_history", lambda **_: {"manifest_id": "m", "rows": 1, "symbol_count": 1, "date_count": 1, "min_date": "2023-01-01", "max_date": "2023-01-01", "parquet_path": "p", "manifest_path": "m"})
    monkeypatch.setattr(cli, "backfill_a_share_adjusted_price_history", lambda **_: {"manifest_id": "m", "rows": 1, "symbol_count": 1, "adjustment_types": ["raw"], "parquet_path": "p", "manifest_path": "m"})
    monkeypatch.setattr(cli, "backfill_a_share_daily_basic_history", lambda **_: {"manifest_id": "m", "rows": 1, "symbol_count": 1, "parquet_path": "p", "manifest_path": "m"})
    monkeypatch.setattr(cli, "backfill_a_share_financial_history", lambda **_: {"manifest_id": "m", "rows": 1, "symbol_count": 1, "report_date_coverage": 1, "parquet_path": "p", "manifest_path": "m"})
    monkeypatch.setattr(cli, "audit_a_share_historical_panel_coverage", lambda **_: {"audit_id": "a", "overall_passed": True, "blocking_reasons": [], "warnings": [], "coverage": {}, "json_path": "j", "report_path": "r"})
    monkeypatch.setattr(cli, "audit_a_share_feature_readiness", lambda **_: {"audit_id": "a", "overall_passed": True, "blocking_reasons": [], "warnings": [], "readiness": {}, "json_path": "j", "report_path": "r"})

    assert cli.main(["a-share-historical-backfill-plan"]) == 0
    assert cli.main(["backfill-a-share-daily-price-history", "--start-date", "2023-01-01", "--end-date", "2026-06-26"]) == 0
    assert cli.main(["backfill-a-share-adjusted-price-history", "--start-date", "2023-01-01", "--end-date", "2026-06-26"]) == 0
    assert cli.main(["backfill-a-share-daily-basic-history", "--start-date", "2023-01-01", "--end-date", "2026-06-26"]) == 0
    assert cli.main(["backfill-a-share-financial-history", "--start-date", "2021-01-01", "--end-date", "2026-06-26"]) == 0
    assert cli.main(["audit-a-share-historical-panel-coverage"]) == 0
    assert cli.main(["audit-a-share-feature-readiness"]) == 0


def test_a_share_historical_provider_expansion_cli_smoke_no_network_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_history_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "diagnose_a_share_historical_backfill_coverage",
        lambda **_: {
            "diagnostic_id": "d",
            "overall_diagnosis_passed": True,
            "confirmed_root_causes": ["sample"],
            "historical_price_symbols": 10,
            "backfill_input_symbols": 10,
            "json_path": "j",
            "report_path": "r",
        },
    )
    monkeypatch.setattr(
        cli,
        "build_a_share_historical_backfill_symbol_queue",
        lambda **_: {"queue_id": "q", "queue_total_symbols": 6, "eligible_price_backfill_symbols": 4, "json_path": "j", "report_path": "r"},
    )
    monkeypatch.setattr(
        cli,
        "backfill_a_share_historical_panels_full_market",
        lambda **_: {
            "scheduler_id": "s",
            "overall_passed": True,
            "release_eligible": True,
            "queue": {},
            "coverage_audit": {"overall_passed": True},
            "feature_readiness_audit": {"overall_passed": True, "blocking_reasons": []},
        },
    )

    assert cli.main(["diagnose-a-share-historical-backfill-coverage"]) == 0
    assert cli.main(["build-a-share-historical-backfill-symbol-queue"]) == 0
    assert (
        cli.main(
            [
                "backfill-a-share-historical-panels-full-market",
                "--target-start-date",
                "2021-01-01",
                "--minimum-start-date",
                "2023-01-01",
                "--end-date",
                "2026-06-26",
                "--max-symbols",
                "0",
                "--resume",
            ]
        )
        == 0
    )
