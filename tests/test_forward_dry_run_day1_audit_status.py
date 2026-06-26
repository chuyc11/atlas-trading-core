from __future__ import annotations

import json
from pathlib import Path

import pytest

from forward_dry_run_day1_test_utils import build_day1_execution_stack, make_day1_paths
from trading_core.forward_dry_run.day1_post_execution_audit import audit_forward_dry_run_day1
from trading_core.forward_dry_run.forward_dry_run_status import build_forward_dry_run_status
from trading_core.planning.day1_blocker_reclassification_v063 import reclassify_day1_blockers_after_forward_dry_run_day1


def test_day1_post_execution_audit_status_and_reclassification_pass(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    build_day1_execution_stack(paths)
    audit = audit_forward_dry_run_day1(paths=paths)
    status = build_forward_dry_run_status(paths=paths)
    reclass = reclassify_day1_blockers_after_forward_dry_run_day1(paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["warnings"] == []
    assert audit["summary"]["forward_dry_run_days_completed"] == 1
    assert status["forward_dry_run_started"] is True
    assert status["forward_dry_run_days_completed"] == 1
    assert status["next_day_index"] == 2
    assert reclass["remaining_day1_blocker_count"] == 0
    assert reclass["day2_blocker_count"] == 0


def test_day1_post_execution_audit_blocks_real_execution_flag(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    build_day1_execution_stack(paths)
    execution_path = paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_execution_result.json"
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    execution["real_execution"] = True
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    result = audit_forward_dry_run_day1(paths=paths)
    assert result["overall_passed"] is False
    assert "real_execution=true" in result["blocking_reasons"]


def test_day1_status_and_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_paths(tmp_path)
    build_day1_execution_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-forward-dry-run-day1"]) == 0
    assert cli.main(["forward-dry-run-status"]) == 0
    assert cli.main(["reclassify-day1-blockers-after-forward-dry-run-day1"]) == 0
