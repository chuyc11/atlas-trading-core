from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_text
from trading_core.global_briefing.historical_data_packages import REQUIRED_PACKAGE_IDS
from trading_core.global_briefing.historical_data_source_resolver import resolve_historical_data_sources


def test_every_required_package_has_resolution(tmp_path: Path) -> None:
    result = resolve_historical_data_sources(paths=make_paths(tmp_path))
    assert {row["package_id"] for row in result["packages"]} == set(REQUIRED_PACKAGE_IDS)


def test_missing_secret_not_configured_for_auth_global_briefing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GB_AUTH_TOKEN", raising=False)
    result = resolve_historical_data_sources(packages=["HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"], paths=make_paths(tmp_path))
    assert result["packages"][0]["status"] == "not_configured"


def test_local_file_priority_over_public_fallback(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.data_dir / "global_briefing" / "authorized" / "input" / "HIST-GLOBAL-RISK-VIX-V1.csv", "date,vix_close\n2024-01-02,13\n")
    result = resolve_historical_data_sources(packages=["HIST-GLOBAL-RISK-VIX-V1"], paths=paths)
    assert result["packages"][0]["selected_source"] == "local_authorized_export"


def test_unknown_and_broker_package_blocking(tmp_path: Path) -> None:
    result = resolve_historical_data_sources(packages=["UNKNOWN-PACKAGE", "BROKER-ACCOUNT-ORDERS"], paths=make_paths(tmp_path))
    assert result["overall_passed"] is False
    assert len(result["blocking_reasons"]) == 2


def test_resolution_markdown_and_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = resolve_historical_data_sources(paths=paths)
    text = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "Historical data authorization is not trading authorization." in text
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_source_resolution_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["historical-data-source-resolution"]) == 0
