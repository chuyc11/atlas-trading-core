from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.day1_prompt_eligibility_report import build_forward_dry_run_day1_prompt_eligibility
from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import build_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.owner_authorization_packet import build_forward_dry_run_owner_authorization_packet
from trading_core.forward_dry_run.start_gate_validator import validate_forward_dry_run_start_gate_v062


def test_day1_prompt_eligibility_defaults_not_eligible(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    build_forward_dry_run_owner_authorization_packet(paths=paths)
    validate_forward_dry_run_start_gate_v062(paths=paths)
    result = build_forward_dry_run_day1_prompt_eligibility(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["day1_prompt_eligible"] is False
    assert result["day1_prompt_generated"] is False
    for reason in ["manual_confirmation_complete=false", "forward_dry_run_start_authorized=false", "start_gate_day1_start_allowed=false"]:
        assert reason in result["deny_reasons"]
    assert not (paths.outputs_dir / "system" / "DAY1_EXECUTION_PROMPT.md").exists()
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_prompt_eligibility_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    build_forward_dry_run_owner_authorization_packet(paths=paths)
    validate_forward_dry_run_start_gate_v062(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-prompt-eligibility"]) == 0

