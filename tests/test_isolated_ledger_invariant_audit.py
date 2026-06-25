from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.isolated_ledger_invariant_audit import audit_isolated_ledger_invariants


def test_isolated_ledger_invariant_audit_passes(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    result = audit_isolated_ledger_invariants(paths=paths)
    assert result["overall_passed"] is True
    assert result["orders"] >= 1
    assert result["trades"] >= 1
    assert "data/replays/global_briefing" in result["ledger_dir"]
    assert_no_protected_paths(paths)


def test_isolated_ledger_invariant_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_planning_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-isolated-ledger-invariants"]) == 0

