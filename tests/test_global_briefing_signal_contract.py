from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.signal_contract import build_signal_contract


def test_contract_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_signal_contract(paths)

    assert Path(result["json_path"]).exists()
    assert result["contract_id"] == "GLOBAL-BRIEFING-SIGNAL-CONTRACT-V1"


def test_contract_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_signal_contract(paths)

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "# Global Briefing Signal Contract" in report
    assert "This contract defines historical macro signal packages accepted by trading-core." in report


def test_contract_required_fields_exist(tmp_path: Path) -> None:
    result = build_signal_contract(make_paths(tmp_path))

    for field in ["as_of_date", "generated_at", "region", "signals", "source", "version"]:
        assert field in result["required_fields"]


def test_contract_point_in_time_rules_exist(tmp_path: Path) -> None:
    result = build_signal_contract(make_paths(tmp_path))

    assert result["point_in_time_rules"]
    assert "Future macro signals must be rejected." in result["point_in_time_rules"]


def test_contract_does_not_write_main_ledger(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    build_signal_contract(paths)

    assert_no_protected_paths(paths)


def test_contract_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-contract"]) == 0


def test_contract_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["global-briefing-contract"]) == 0
    assert (paths.data_dir / "system" / "global_briefing_signal_contract.json").exists()
