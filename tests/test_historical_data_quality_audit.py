from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_quality_audit import audit_historical_data_quality
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages


def _stack(paths):
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)


def test_all_packages_available_passed(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    result = audit_historical_data_quality(paths=paths)
    assert result["overall_passed"] is True


def test_missing_critical_checksum_and_secret_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = make_paths(tmp_path)
    _stack(paths)
    manifest_path = paths.data_dir / "system" / "historical_data_download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["packages"] = [item for item in manifest["packages"] if item["package_id"] != "HIST-ETF-OHLCV-CN-HK-V1"]
    manifest["packages"][0]["sha256"] = None
    monkeypatch.setenv("TEST_SECRET_TOKEN", "SECRET_VALUE")
    Path(manifest["packages"][0]["path"]).write_text("SECRET_VALUE\n", encoding="utf-8")
    write_json(manifest_path, manifest)
    result = audit_historical_data_quality(paths=paths)
    assert result["overall_passed"] is False
    assert any("critical" in item.lower() or "checksum" in item.lower() or "secret" in item.lower() for item in result["blocking_reasons"])


def test_quality_audit_boundaries_and_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-historical-data-quality"]) == 0
    result = audit_historical_data_quality(paths=paths)
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)
