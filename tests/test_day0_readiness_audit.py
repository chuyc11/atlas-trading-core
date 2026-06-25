from __future__ import annotations

from pathlib import Path

import json
import pytest

from day0_test_utils import build_day0_stack, make_day0_paths
from trading_core.forward_dry_run.day0_readiness_audit import RELEASE_CANDIDATE, audit_day0_readiness


def test_day0_readiness_audit_passes_and_recommends_tag(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    result = audit_day0_readiness(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["day0_status"]["manual_confirmation_complete"] is False
    assert RELEASE_CANDIDATE in Path(result["report_path"]).read_text(encoding="utf-8")


def test_day0_readiness_audit_blocks_mutated_artifacts_and_wording(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    (paths.data_dir / "system" / "day0_data_freeze_manifest.json").unlink()
    warning_path = paths.data_dir / "system" / "day0_accepted_warning_register.json"
    warning = json.loads(warning_path.read_text(encoding="utf-8"))
    warning["blocking_count"] = 1
    warning_path.write_text(json.dumps(warning), encoding="utf-8")
    conditions_path = paths.data_dir / "system" / "day0_blocking_conditions.json"
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    conditions["current_blocking_count"] = 1
    conditions_path.write_text(json.dumps(conditions), encoding="utf-8")
    preflight_path = paths.data_dir / "system" / "day0_run_daily_preflight.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    preflight["run_daily_command_preview"]["executed"] = True
    preflight_path.write_text(json.dumps(preflight), encoding="utf-8")
    manual_path = paths.data_dir / "system" / "day0_manual_confirmation_packet.json"
    manual = json.loads(manual_path.read_text(encoding="utf-8"))
    manual["confirmations"]["owner_confirmed_data_freeze"] = True
    manual["manual_confirmation_complete"] = True
    manual["forward_dry_run_start_authorized"] = True
    manual_path.write_text(json.dumps(manual), encoding="utf-8")
    (paths.outputs_dir / "system" / "BAD.md").write_text("live trading ready\nforward dry-run started\n", encoding="utf-8")
    result = audit_day0_readiness(paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    for token in ["data_freeze", "warning_register", "blocking_conditions", "preflight", "manual_confirmation", "wording"]:
        assert token in joined


def test_day0_readiness_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    build_day0_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-day0-readiness"]) == 0
