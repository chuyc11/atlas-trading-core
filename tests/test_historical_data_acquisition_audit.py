from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json
from trading_core.global_briefing.full_historical_proxy_workflow import run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_acquisition_audit import RELEASE_CANDIDATE, audit_historical_data_acquisition
from trading_core.global_briefing.historical_data_acquisition_report import build_historical_data_acquisition_report
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_quality_audit import audit_historical_data_quality
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages


def _stack(paths):
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    audit_historical_data_quality(paths=paths)
    run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    build_historical_data_acquisition_report(paths=paths)


def test_acquisition_audit_json_markdown_and_recommend_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_historical_data_acquisition(paths=paths)
    assert Path(result["json_path"]).exists()
    assert RELEASE_CANDIDATE in Path(result["report_path"]).read_text(encoding="utf-8")
    assert result["overall_passed"] is True


def test_missing_manifest_checksum_secret_and_critical_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    manifest_path = paths.data_dir / "system" / "historical_data_download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["packages"] = [item for item in manifest["packages"] if item["package_id"] != "HIST-ETF-OHLCV-CN-HK-V1"]
    manifest["packages"][0]["sha256"] = None
    monkeypatch.setenv("TEST_SECRET_TOKEN", "SECRET_VALUE")
    Path(manifest["packages"][0]["path"]).write_text("SECRET_VALUE\n", encoding="utf-8")
    write_json(manifest_path, manifest)
    result = audit_historical_data_acquisition(paths=paths)
    assert result["overall_passed"] is False
    assert any("download_manifest" in item for item in result["blocking_reasons"])


def test_proxy_future_and_boundary_and_wording_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    workflow_path = next((paths.data_dir / "replays" / "global_briefing").glob("full_historical_proxy_workflow-*.json"))
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["boundary"]["main_ledger_written"] = True
    workflow["boundary"]["run_daily_called"] = True
    workflow["boundary"]["labels_used"] = True
    workflow["boundary"]["ml_shadow_used"] = True
    workflow["boundary"]["experiments_used"] = True
    workflow["boundary"]["promotion_triggered"] = True
    write_json(workflow_path, workflow)
    (paths.outputs_dir / "system" / "HISTORICAL_DATA_ACQUISITION_REPORT.md").write_text("live trading ready\n", encoding="utf-8")
    result = audit_historical_data_acquisition(paths=paths)
    assert result["overall_passed"] is False
    assert any("proxy_replay" in item or "wording" in item for item in result["blocking_reasons"])


def test_acquisition_audit_cli_smoke_and_boundaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-historical-data-acquisition"]) == 0
    result = audit_historical_data_acquisition(paths=paths)
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)
