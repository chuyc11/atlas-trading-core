from __future__ import annotations

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json
from trading_core.global_briefing.historical_warning_inventory import build_historical_warning_inventory


def _write_inputs(paths, *, unknown: bool = False, future: bool = False) -> None:
    quality_warnings = [
        "HIST-POLICY-UNCERTAINTY-EPU-V1 unavailable: EPU download failed",
        "HIST-OECD-CLI-MACRO-CYCLE-V1 unavailable: OECD download failed",
    ]
    if future:
        quality_warnings.append("future leakage detected in point-in-time package")
    if unknown:
        quality_warnings.append("unclassified custom warning pattern")
    write_json(paths.data_dir / "system" / "historical_data_quality_audit.json", {"warnings": quality_warnings})
    write_json(
        paths.data_dir / "system" / "historical_data_download_manifest.json",
        {"packages": [{"package_id": "HIST-POLICY-UNCERTAINTY-EPU-V1"}, {"package_id": "HIST-OECD-CLI-MACRO-CYCLE-V1"}]},
    )
    write_json(
        paths.data_dir / "replays" / "global_briefing" / "full_historical_proxy_workflow-2024-01-02-2024-01-08.json",
        {
            "raw_warning_count": 665,
            "grouped_warnings": [
                {
                    "category": "lot_size_constraint",
                    "severity": "medium",
                    "raw_count": 420,
                    "message_pattern": "target delta below lot size",
                    "first_seen_date": "2024-01-02",
                    "last_seen_date": "2024-01-08",
                    "recommended_action": "review lot size and target-weight settings",
                },
                {
                    "category": "missing_price",
                    "severity": "high",
                    "raw_count": 245,
                    "message_pattern": "missing replay price for symbol",
                    "first_seen_date": "2024-01-02",
                    "last_seen_date": "2024-01-08",
                    "recommended_action": "fill historical price gap or reduce replay universe",
                },
            ],
        },
    )


def test_warning_inventory_groups_replay_warnings_and_generates_reports(tmp_path) -> None:
    paths = make_paths(tmp_path)
    _write_inputs(paths)
    result = build_historical_warning_inventory(paths=paths)
    assert result["raw_warning_count"] == 667
    assert result["grouped_warning_count"] < result["raw_warning_count"]
    assert result["unknown_warning_count"] == 0
    assert result["by_category"]["missing_signal_component"] >= 2
    assert result["by_category"]["lot_size_constraint"] == 1
    assert result["by_category"]["missing_price"] == 1
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert "Historical Warning Inventory" in open(result["report_path"], encoding="utf-8").read()
    assert_no_protected_paths(paths)


def test_warning_inventory_records_unknown_and_future_blocker(tmp_path) -> None:
    paths = make_paths(tmp_path)
    _write_inputs(paths, unknown=True, future=True)
    result = build_historical_warning_inventory(paths=paths)
    assert result["unknown_warning_count"] == 1
    assert result["by_category"]["future_leakage"] == 1
    assert any(group["category"] == "future_leakage" and group["severity"] == "high" for group in result["production_blockers"])


def test_warning_inventory_cli_smoke(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _write_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["historical-warning-inventory"]) == 0
