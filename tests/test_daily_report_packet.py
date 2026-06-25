from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_report_packet import EXPLICIT_NON_CLAIMS, build_daily_report_packet


def test_daily_report_packet(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_report_packet(as_of_date=AS_OF, paths=paths)
    assert result["signals_summary_by_strategy"]
    assert result["order_preview_summary_by_strategy"]
    assert result["execution_preview_summary"]["execution_mode"] == "isolated_preview"
    assert result["operator_checklist"]
    for claim in EXPLICIT_NON_CLAIMS:
        assert claim in result["explicit_non_claims"]
    text = Path(result["report_path"]).read_text(encoding="utf-8").lower()
    assert "strategy effectiveness proven" not in text
    assert "live trading ready" not in text
    assert result["run_daily_called"] is False
    assert result["main_ledger_written"] is False
    assert_no_protected_paths(paths)


def test_daily_report_packet_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-report-packet", "--as-of-date", AS_OF]) == 0

