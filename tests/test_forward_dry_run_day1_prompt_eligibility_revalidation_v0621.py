from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.completed_manual_confirmation_checklist_v2 import complete_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.day1_prompt_eligibility_revalidation_v0621 import revalidate_forward_dry_run_day1_prompt_eligibility
from trading_core.forward_dry_run.owner_manual_confirmation_record import build_owner_manual_confirmation_record
from trading_core.forward_dry_run.start_gate_revalidation_v0621 import revalidate_forward_dry_run_start_gate_v0621
from trading_core.forward_dry_run.updated_owner_authorization_packet import update_forward_dry_run_owner_authorization_packet


def test_day1_prompt_eligibility_revalidation_v0621(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    build_owner_manual_confirmation_record(paths=paths)
    complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    update_forward_dry_run_owner_authorization_packet(paths=paths)
    revalidate_forward_dry_run_start_gate_v0621(paths=paths)
    result = revalidate_forward_dry_run_day1_prompt_eligibility(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["day1_prompt_eligible"] is True
    assert result["day1_prompt_generated"] is False
    assert result["next_required_action"] == "owner_requests_day1_prompt"
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_prompt_eligibility_revalidation_v0621_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    build_owner_manual_confirmation_record(paths=paths)
    complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    update_forward_dry_run_owner_authorization_packet(paths=paths)
    revalidate_forward_dry_run_start_gate_v0621(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["revalidate-forward-dry-run-day1-prompt-eligibility"]) == 0

