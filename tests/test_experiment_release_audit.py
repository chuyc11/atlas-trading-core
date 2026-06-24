"""Tests for v0.4 experiment system release audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.experiment_release_audit import audit_experiment_system
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def audit_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    root = workspace / "work" / "trading-core"
    (root / "data" / "experiments").mkdir(parents=True)
    (root / "data" / "shadow").mkdir(parents=True)
    (root / "outputs" / "experiments").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _seed_complete_artifacts(paths: ProjectPaths) -> None:
    exp = paths.data_dir / "experiments"
    shadow = paths.data_dir / "shadow"
    out = paths.outputs_dir / "experiments"
    sweep = _write_json(exp / "parameter_sweep-EXP-a.json", {"experiment_id": "EXP-a", "runs": []})
    ml = _write_json(shadow / "ml_shadow_leaderboard-a.json", {"model_id": "ML-a", "prediction_count": 10})
    comparison = _write_json(
        exp / "strategy_comparison-20260624-000000.json",
        {"comparison_id": "CMP-a", "input_paths": [str(sweep), str(ml)], "items": []},
    )
    simulation = _write_json(
        exp / "promotion_simulation-20260624-000000.json",
        {
            "simulation_id": "PROMO-a",
            "input_path": str(comparison),
            "items": [],
            "boundary": {"strategy_state_changed": False, "write_main_ledger": False},
        },
    )
    _write_json(exp / "experiment_registry.json", {"experiments": [{"experiment_id": "EXP-a", "mode": "shadow"}]})
    _write_json(
        exp / "experiment_dashboard.json",
        {
            "registry": {"experiment_count": 1},
            "parameter_sweeps": [{}],
            "ml_shadow_results": [{}],
            "strategy_comparisons": [{}],
        },
    )
    _write_json(
        exp / "mistake_pattern_library.json",
        {
            "inputs": [str(simulation)],
            "patterns": [],
            "boundary": {"diagnostic_only": True, "promotion_triggered": False, "write_main_ledger": False},
        },
    )
    _write(out / "PARAMETER_SWEEP-EXP-a.md", "not an admission gate\nno orders/trades/portfolio written\noffline research only\n")
    _write(out / "STRATEGY_COMPARISON-a.md", "not an admission gate\nno orders/trades/portfolio/accounts written\nno active promotion\n")
    _write(out / "EXPERIMENT_DASHBOARD.md", "not an admission gate\ndashboard is read-only\nno active promotion\nno orders/trades/portfolio writes\n")
    _write(out / "PROMOTION_SIMULATION-a.md", "This is a simulation only.\nNo strategy state was changed.\nNo active strategy was promoted.\nNo orders were written.\nThis is not an admission gate.\nThis report is offline research only.\n")
    _write(out / "MISTAKE_PATTERN_LIBRARY.md", "This pattern library is diagnostic only.\nNo strategy was modified.\nNo parameter was modified.\nNo promotion was triggered.\nNo accounts were written.\nThis is not an admission gate.\nThis report is offline research only.\n")


def test_audit_fails_when_required_artifacts_are_missing(audit_paths: ProjectPaths) -> None:
    result = audit_experiment_system(audit_paths)

    assert result["passed"] is False
    assert any(check["name"] == "experiment_registry_exists" and not check["passed"] for check in result["checks"])


def test_audit_passes_complete_fixture(audit_paths: ProjectPaths) -> None:
    _seed_complete_artifacts(audit_paths)

    result = audit_experiment_system(audit_paths)

    assert result["passed"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_audit_detects_missing_markdown_boundary(audit_paths: ProjectPaths) -> None:
    _seed_complete_artifacts(audit_paths)
    (audit_paths.outputs_dir / "experiments" / "EXPERIMENT_DASHBOARD.md").write_text("not an admission gate\n", encoding="utf-8")

    result = audit_experiment_system(audit_paths)

    assert result["passed"] is False
    assert any(check["name"] == "experiment_dashboard_boundary_phrases" and not check["passed"] for check in result["checks"])


def test_audit_cli_smoke_does_not_call_run_daily(
    audit_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    _seed_complete_artifacts(audit_paths)
    monkeypatch.setattr(cli, "project_paths", lambda: audit_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(["audit-experiment-system"])

    captured = capsys.readouterr()
    assert result == 0
    assert "passed" in captured.out
