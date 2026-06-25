from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import build_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.owner_authorization_packet import build_forward_dry_run_owner_authorization_packet
from trading_core.forward_dry_run.start_gate_validator import evaluate_start_gate, validate_forward_dry_run_start_gate_v062


def test_start_gate_validator_fails_closed(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    build_forward_dry_run_owner_authorization_packet(paths=paths)
    result = validate_forward_dry_run_start_gate_v062(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["manual_confirmation_complete"] is False
    assert result["forward_dry_run_start_authorized"] is False
    assert result["day1_start_allowed"] is False
    assert result["deny_reasons"] == ["manual_confirmation_complete=false", "forward_dry_run_start_authorized=false"]
    assert result["run_daily_command_preview"]["preview_only"] is True
    assert result["run_daily_command_preview"]["executed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_start_gate_evaluator_all_true_allows_without_running_day1() -> None:
    result = evaluate_start_gate(
        plan_alignment_passed=True,
        ashare_execution_rules_passed=True,
        baseline_strategy_pack_passed=True,
        daily_workflow_audit_passed=True,
        protected_path_blocker_count=0,
        updated_day1_blocker_count=0,
        manual_confirmation_complete=True,
        forward_dry_run_start_authorized=True,
        git_status_clean=True,
        latest_release_tag_exists=True,
        run_daily_called=False,
        forward_dry_run_started=False,
        main_ledger_written=False,
        no_broker_live_config=True,
        no_rl_llm_trading_decision_enabled=True,
    )
    assert result["day1_start_allowed"] is True
    assert result["deny_reasons"] == []


def test_start_gate_validator_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    build_forward_dry_run_owner_authorization_packet(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["validate-forward-dry-run-start-gate-v062"]) == 0

