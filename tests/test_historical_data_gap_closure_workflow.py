from __future__ import annotations

import json

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_gap_closure_workflow import close_historical_data_gaps


def _seed_fixture_manifest(paths) -> None:
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    manifest_path = paths.data_dir / "system" / "historical_data_download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["packages"]:
        if item["package_id"] in {"HIST-POLICY-UNCERTAINTY-EPU-V1", "HIST-OECD-CLI-MACRO-CYCLE-V1"}:
            item.update({"status": "failed", "sha256": None, "provenance_path": None})
    write_json(manifest_path, manifest)


def test_gap_closure_workflow_repairs_gaps_rebuilds_proxy_and_generates_artifacts(tmp_path) -> None:
    paths = make_paths(tmp_path)
    _seed_fixture_manifest(paths)
    result = close_historical_data_gaps(
        start_date="2024-01-02",
        end_date="2024-01-08",
        replay_start_date="2024-01-02",
        replay_end_date="2024-01-08",
        min_coverage=0.60,
        paths=paths,
    )
    assert result["overall_status"] == "passed"
    assert result["blocking_reasons"] == []
    assert result["current"]["available_packages"] >= 8
    assert result["current"]["epu_status"] in {"downloaded", "partial_downloaded", "loaded_from_local"}
    assert result["current"]["oecd_status"] in {"downloaded", "partial_downloaded", "loaded_from_local"}
    assert result["current"]["proxy_replay_grouped_warnings"] <= result["current"]["proxy_replay_raw_warnings"]
    assert (paths.data_dir / "system" / "historical_warning_inventory.json").exists()
    assert (paths.data_dir / "global_briefing" / "authorized" / "packages" / "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.jsonl").exists()
    assert (paths.data_dir / "global_briefing" / "normalized" / "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl").exists()
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)


def test_gap_closure_workflow_cli_smoke(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _seed_fixture_manifest(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["close-historical-data-gaps", "--start-date", "2024-01-02", "--end-date", "2024-01-08", "--replay-start-date", "2024-01-02", "--replay-end-date", "2024-01-08", "--min-coverage", "0.60"]) == 0
