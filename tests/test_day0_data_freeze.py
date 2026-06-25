from __future__ import annotations

from pathlib import Path

import pytest

from day0_test_utils import make_day0_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.forward_dry_run.day0_data_freeze import build_day0_data_freeze


def test_day0_data_freeze_generates_manifest_and_accepts_known_limitations(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    result = build_day0_data_freeze(paths=paths)
    assert result["overall_passed"] is True
    assert "HIST-ETF-OHLCV-CN-HK-V1" in result["packages"]
    assert "missing us_epu/europe_epu" in result["packages"]["HIST-POLICY-UNCERTAINTY-EPU-V1"]["accepted_limitations"]
    assert "not official OECD CLI" in result["packages"]["HIST-OECD-CLI-MACRO-CYCLE-V1"]["accepted_limitations"]
    assert result["packages"]["HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"]["status"] == "not_configured"
    assert result["proxy_package"]["is_internal_global_briefing_signal"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert "Day-0 Data Freeze Manifest" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_day0_data_freeze_blocks_missing_critical_package(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    manifest = paths.data_dir / "system" / "historical_data_download_manifest.json"
    import json

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["packages"] = [item for item in payload["packages"] if item["package_id"] != "HIST-ETF-OHLCV-CN-HK-V1"]
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    result = build_day0_data_freeze(paths=paths)
    assert result["overall_passed"] is False
    assert any("HIST-ETF-OHLCV-CN-HK-V1" in item for item in result["blocking_reasons"])


def test_day0_data_freeze_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-data-freeze"]) == 0
