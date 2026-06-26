from pathlib import Path
import json

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_materialization_stack, build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.authorization_materialization_audit import audit_forward_dry_run_authorization_materialization
from trading_core.forward_dry_run.completed_manual_confirmation_checklist_v2 import complete_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.day1_prompt_eligibility_revalidation_v0621 import revalidate_forward_dry_run_day1_prompt_eligibility
from trading_core.forward_dry_run.owner_manual_confirmation_record import build_owner_manual_confirmation_record
from trading_core.forward_dry_run.start_gate_revalidation_v0621 import revalidate_forward_dry_run_start_gate_v0621
from trading_core.forward_dry_run.updated_owner_authorization_packet import update_forward_dry_run_owner_authorization_packet


def test_authorization_materialization_audit_passes(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_materialization_stack(paths)
    result = audit_forward_dry_run_authorization_materialization(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["manual_confirmation_complete"] is True
    assert result["summary"]["forward_dry_run_start_authorized"] is True
    assert result["summary"]["day1_prompt_eligible"] is True
    assert result["summary"]["day1_prompt_generated"] is False
    assert result["summary"]["day1_start_allowed"] is False


def test_authorization_materialization_audit_blocks_bad_boundaries_and_wording(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    build_owner_manual_confirmation_record(paths=paths)
    complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    update_forward_dry_run_owner_authorization_packet(paths=paths)
    revalidate_forward_dry_run_start_gate_v0621(paths=paths)
    revalidate_forward_dry_run_day1_prompt_eligibility(paths=paths)
    preview_path = paths.data_dir / "system" / "forward_dry_run_run_daily_command_preview.json"
    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    preview["executed"] = True
    preview_path.write_text(json.dumps(preview), encoding="utf-8")
    gate_path = paths.data_dir / "system" / "forward_dry_run_start_gate_v0621.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["day1_start_allowed"] = True
    gate["boundary"]["forward_dry_run_started"] = True
    gate_path.write_text(json.dumps(gate), encoding="utf-8")
    (paths.outputs_dir / "system" / "FORWARD_DRY_RUN_START_GATE_V0621.md").write_text("forward dry-run started\nlive trading ready\n", encoding="utf-8")
    result = audit_forward_dry_run_authorization_materialization(paths=paths)
    joined = "\n".join(result["blocking_reasons"])
    for expected in ["day1_start_allowed=true", "executed=true", "forward_dry_run_started=true", "forward dry-run started", "live trading ready"]:
        assert expected in joined


def test_authorization_materialization_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_materialization_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-forward-dry-run-authorization-materialization"]) == 0

