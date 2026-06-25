from pathlib import Path
import json

import pytest

from forward_dry_run_authorization_test_utils import build_authorization_pack, make_authorization_paths
from trading_core.forward_dry_run.start_authorization_audit import audit_forward_dry_run_start_authorization


def test_start_authorization_audit_passes_release_default(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    result = audit_forward_dry_run_start_authorization(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["recommended_next_action"] == "owner_manual_confirmation"
    assert result["summary"]["manual_confirmation_complete"] is False
    assert result["summary"]["forward_dry_run_start_authorized"] is False
    assert result["summary"]["day1_start_allowed"] is False
    assert result["summary"]["day1_prompt_eligible"] is False
    assert result["summary"]["day1_prompt_generated"] is False


def test_start_authorization_audit_blocks_missing_and_bad_defaults(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    (paths.data_dir / "system" / "forward_dry_run_authorization_scope_plan.json").unlink()
    (paths.data_dir / "system" / "forward_dry_run_start_prerequisite_inventory.json").unlink()
    (paths.data_dir / "system" / "forward_dry_run_manual_confirmation_checklist_v2.json").unlink()
    owner = paths.data_dir / "system" / "forward_dry_run_owner_authorization_packet.json"
    owner_payload = json.loads(owner.read_text(encoding="utf-8"))
    owner_payload["forward_dry_run_start_authorized"] = True
    owner.write_text(json.dumps(owner_payload), encoding="utf-8")
    gate = paths.data_dir / "system" / "forward_dry_run_start_gate_v062.json"
    gate_payload = json.loads(gate.read_text(encoding="utf-8"))
    gate_payload["day1_start_allowed"] = True
    gate_payload["boundary"]["run_daily_called"] = True
    gate.write_text(json.dumps(gate_payload), encoding="utf-8")
    eligibility = paths.data_dir / "system" / "forward_dry_run_day1_prompt_eligibility.json"
    eligibility_payload = json.loads(eligibility.read_text(encoding="utf-8"))
    eligibility_payload["day1_prompt_generated"] = True
    eligibility.write_text(json.dumps(eligibility_payload), encoding="utf-8")
    preview = paths.data_dir / "system" / "forward_dry_run_run_daily_command_preview.json"
    preview_payload = json.loads(preview.read_text(encoding="utf-8"))
    preview_payload["executed"] = True
    preview.write_text(json.dumps(preview_payload), encoding="utf-8")
    result = audit_forward_dry_run_start_authorization(paths=paths)
    joined = "\n".join(result["blocking_reasons"])
    for expected in ["missing scope_plan", "missing inventory", "missing manual_confirmation", "forward_dry_run_start_authorized=true", "day1_start_allowed=true", "day1_prompt_generated=true", "executed=true", "run_daily_called=true"]:
        assert expected in joined


def test_start_authorization_audit_blocks_forbidden_positive_wording(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    (paths.outputs_dir / "system" / "FORWARD_DRY_RUN_START_GATE_V062.md").write_text("forward dry-run started\nlive trading ready\n", encoding="utf-8")
    result = audit_forward_dry_run_start_authorization(paths=paths)
    joined = "\n".join(result["blocking_reasons"])
    assert "forward dry-run started" in joined
    assert "live trading ready" in joined


def test_start_authorization_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    build_authorization_pack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-forward-dry-run-start-authorization"]) == 0

