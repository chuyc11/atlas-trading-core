from pathlib import Path

import json
import pytest

from execution_test_utils import build_execution_stack, make_execution_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.execution.ashare_execution_rules_audit import RELEASE_CANDIDATE, audit_ashare_execution_rules


def test_ashare_execution_rules_audit_passes(tmp_path: Path) -> None:
    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    result = audit_ashare_execution_rules(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["baseline_day1_blocker_count"] == 3
    assert result["summary"]["updated_day1_blocker_count"] == 0
    assert RELEASE_CANDIDATE in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_ashare_execution_rules_audit_blocks_mutations_and_wording(tmp_path: Path) -> None:
    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    calendar = paths.data_dir / "system" / "ashare_trading_calendar_audit.json"
    payload = json.loads(calendar.read_text(encoding="utf-8"))
    payload["overall_passed"] = False
    calendar.write_text(json.dumps(payload), encoding="utf-8")
    (paths.outputs_dir / "system" / "BAD.md").write_text("live trading ready\nML approved for trading\n", encoding="utf-8")
    result = audit_ashare_execution_rules(paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    assert "calendar" in joined
    assert "wording" in joined


def test_ashare_execution_rules_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_execution_paths(tmp_path)
    build_execution_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-ashare-execution-rules"]) == 0

