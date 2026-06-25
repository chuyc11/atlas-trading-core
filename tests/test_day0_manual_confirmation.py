from __future__ import annotations

from pathlib import Path

import pytest

from day0_test_utils import make_day0_paths
from trading_core.forward_dry_run.day0_manual_confirmation import build_day0_manual_confirmation_packet


def test_day0_manual_confirmation_defaults_false_and_documents_limits(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    result = build_day0_manual_confirmation_packet(paths=paths)
    assert all(value is False for value in result["confirmations"].values())
    assert result["manual_confirmation_complete"] is False
    assert result["forward_dry_run_start_authorized"] is False
    assert result["boundary"]["auto_confirmation"] is False
    assert any("EPU partial" in item for item in result["accepted_limitations"])
    assert any("not live trading readiness" in item for item in result["explicit_non_claims"])
    assert "All confirmation fields default to false" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_day0_manual_confirmation_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-manual-confirmation-packet"]) == 0
