from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json
from test_historical_data_gap_closure_workflow import _seed_fixture_manifest
from trading_core.global_briefing.historical_data_gap_closure_audit import RELEASE_CANDIDATE, audit_historical_data_gap_closure
from trading_core.global_briefing.historical_data_gap_closure_report import build_historical_data_gap_closure_report
from trading_core.global_briefing.historical_data_gap_closure_workflow import close_historical_data_gaps


def _closure_stack(paths) -> None:
    _seed_fixture_manifest(paths)
    close_historical_data_gaps(start_date="2024-01-02", end_date="2024-01-08", replay_start_date="2024-01-02", replay_end_date="2024-01-08", min_coverage=0.60, paths=paths)
    build_historical_data_gap_closure_report(paths=paths)


def test_gap_closure_audit_passes_and_recommends_release(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _closure_stack(paths)
    result = audit_historical_data_gap_closure(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert RELEASE_CANDIDATE in open(result["report_path"], encoding="utf-8").read()
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)

    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-historical-data-gap-closure"]) == 0


def test_gap_closure_audit_blocks_mutated_release_conditions(tmp_path) -> None:
    paths = make_paths(tmp_path)
    _closure_stack(paths)

    manifest_path = paths.data_dir / "system" / "historical_data_download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["packages"]:
        if item["package_id"] == "HIST-POLICY-UNCERTAINTY-EPU-V1":
            item["status"] = "failed_soft"
            item["sha256"] = None
        if item["package_id"] == "HIST-OECD-CLI-MACRO-CYCLE-V1":
            item["source"] = "authorized_macro_cycle_proxy"
            item["not_official_oecd_cli"] = False
    write_json(manifest_path, manifest)

    normalization_path = paths.data_dir / "system" / "historical_package_normalization_summary.json"
    normalization = json.loads(normalization_path.read_text(encoding="utf-8"))
    Path(normalization["proxy_package"]["normalized_path"]).unlink()
    write_json(normalization_path, normalization)

    inventory_path = paths.data_dir / "system" / "historical_warning_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["unknown_warning_count"] = 1
    write_json(inventory_path, inventory)

    workflow_path = paths.data_dir / "system" / "historical_data_gap_closure_workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    replay_path = Path(workflow["artifacts"]["proxy_replay"])
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay.pop("grouped_warnings", None)
    replay["blocking_reasons"] = ["future leakage detected"]
    replay["boundary"]["main_ledger_written"] = True
    replay["boundary"]["run_daily_called"] = True
    write_json(replay_path, replay)

    report_path = paths.data_dir / "system" / "historical_data_gap_closure_report.json"
    report_path.unlink()
    (paths.outputs_dir / "system" / "BAD.md").write_text("live trading ready\n", encoding="utf-8")

    result = audit_historical_data_gap_closure(paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    for token in [
        "epu_repair",
        "oecd_repair",
        "proxy_rebuild",
        "warning_inventory",
        "replay_warning_reduction",
        "future_leakage",
        "wording",
        "report",
    ]:
        assert token in joined
