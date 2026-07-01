from __future__ import annotations

from pathlib import Path

from tests.a_share_operator_experience_test_utils import AS_OF_DATE, make_paths as make_operator_paths, seed_operator_outputs, write_json
from test_a_share_data_freshness_refresh import TARGET_DATE, fake_provider, make_paths
from trading_core.cli import build_parser, main
from trading_core.equity_data_freshness import refresh_a_share_data_freshness


def test_data_freshness_cli_command_registered() -> None:
    args = build_parser().parse_args(["refresh-a-share-data-freshness", "--target-as-of-date", TARGET_DATE, "--dry-run"])
    assert args.command == "refresh-a-share-data-freshness"
    assert args.target_as_of_date == TARGET_DATE
    assert args.dry_run is True


def test_data_freshness_cli_smoke_does_not_call_run_daily(tmp_path: Path, monkeypatch, capsys) -> None:
    import trading_core.cli as cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "refresh_a_share_data_freshness",
        lambda **kwargs: {
            "builder_id": "A-SHARE-DATA-FRESHNESS-REFRESH",
            "overall_passed": True,
            "requested_target_as_of_date": kwargs["target_as_of_date"],
            "resolved_actual_data_date": kwargs["target_as_of_date"],
            "date_resolution_reason": "target_date_available_in_local_trading_calendar",
            "dry_run": kwargs["dry_run"],
            "provider_status": "passed",
            "coverage_ratio": 1.0,
            "coverage_passed": True,
            "data_refresh_executed": not kwargs["dry_run"],
            "blocking_reasons": [],
            "warnings": [],
            "recommended_next_version": "v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data",
        },
    )
    assert main(["refresh-a-share-data-freshness", "--target-as-of-date", TARGET_DATE, "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-DATA-FRESHNESS-REFRESH" in out
    assert "coverage_passed" in out


def test_owner_daily_status_reads_v093_freshness_without_gate_rerun(tmp_path: Path, monkeypatch, capsys) -> None:
    paths = make_operator_paths(tmp_path)
    seed_operator_outputs(paths, AS_OF_DATE)
    write_json(
        paths.data_dir / "equity_data_quality" / "a_share_owner_operator_experience_audit.json",
        {"as_of_date": AS_OF_DATE, "overall_passed": True, "blocking_reasons": []},
    )
    refresh_a_share_data_freshness(paths=paths, target_as_of_date=TARGET_DATE, provider_fetcher=fake_provider)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["owner-daily-status", "--as-of-date", TARGET_DATE]) == 0
    out = capsys.readouterr().out
    assert "OWNER-READINESS: BLOCKED" in out
    assert "source data date: 2026-07-01" in out
    assert "v0.9.3 public data refresh executed" in out
    assert "owner_operationally_acceptable = false" in out
