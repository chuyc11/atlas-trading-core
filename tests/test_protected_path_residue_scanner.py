from pathlib import Path
import subprocess

import pytest

from daily_workflow_test_utils import make_daily_workflow_paths
from trading_core.daily_workflow.protected_path_residue_scanner import scan_protected_path_residue


def test_protected_path_residue_scan_no_residue(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = scan_protected_path_residue(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocker_count"] == 0
    assert all(not value for value in result["scanner_actions"].values())


def test_protected_path_residue_scan_ignored_runtime_warning(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    residue = paths.project_root / "data" / "orders" / "ignored.jsonl"
    residue.parent.mkdir(parents=True, exist_ok=True)
    residue.write_text("{}\n", encoding="utf-8")
    result = scan_protected_path_residue(paths=paths)
    assert result["overall_passed"] is True
    assert result["warning_count"] == 1
    assert residue.exists()


def test_protected_path_residue_scan_tracked_and_modified_block(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    subprocess.run(["git", "init"], cwd=paths.project_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=paths.project_root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=paths.project_root, check=True)
    tracked = paths.project_root / "data" / "orders" / "tracked.jsonl"
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "add", "-f", "data/orders/tracked.jsonl"], cwd=paths.project_root, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=paths.project_root, check=True, capture_output=True)
    result = scan_protected_path_residue(paths=paths)
    assert result["overall_passed"] is False
    assert result["blocker_count"] == 1
    tracked.write_text('{"changed":true}\n', encoding="utf-8")
    modified = scan_protected_path_residue(paths=paths)
    assert modified["overall_passed"] is False
    assert "modified_protected_artifact" in str(modified["blocking_reasons"])


def test_protected_path_residue_scan_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["protected-path-residue-scan"]) == 0

