"""Tests for Issue 69 v0.4 experiment system audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.experiment_system_audit import (
    RELEASE_CANDIDATE,
    audit_experiment_system,
)
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def system_audit_paths(tmp_path: Path) -> ProjectPaths:
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


def _seed_complete(paths: ProjectPaths, registry: bool = True, dashboard: bool = True) -> dict[str, Path]:
    exp = paths.data_dir / "experiments"
    shadow = paths.data_dir / "shadow"
    out = paths.outputs_dir / "experiments"
    sweep = _write_json(
        exp / "parameter_sweep-EXP-a.json",
        {
            "experiment_id": "EXP-a",
            "strategy_id": "momentum_strategy_v1",
            "runs": [{"run_id": "RUN-a", "status": "shadow_result", "score": -1}],
            "constraints": {"write_main_ledger": False},
        },
    )
    ml = _write_json(
        shadow / "ml_shadow_leaderboard-a.json",
        {"model_id": "ML-a", "prediction_count": 100, "shadow_recommendation": "watch"},
    )
    comparison = _write_json(
        exp / "strategy_comparison-20260624-000001.json",
        {
            "comparison_id": "CMP-a",
            "input_paths": [str(sweep), str(ml)],
            "items": [{"item_id": "RUN-a", "current_recommendation": "reject"}],
            "best_by_score": "RUN-a",
            "best_by_excess_return": "RUN-a",
        },
    )
    simulation = _write_json(
        exp / "promotion_simulation-20260624-000001.json",
        {
            "simulation_id": "PROMO-a",
            "input_path": str(comparison),
            "items": [{"item_id": "RUN-a", "simulated_status": "reject"}],
            "boundary": {"strategy_state_changed": False, "write_main_ledger": False},
        },
    )
    if registry:
        _write_json(
            exp / "experiment_registry.json",
            {
                "experiments": [
                    {
                        "experiment_id": "EXP-a",
                        "strategy_id": "momentum_strategy_v1",
                        "experiment_type": "parameter_sweep",
                        "mode": "shadow",
                        "constraints": {"write_main_ledger": False, "allow_active": False, "shadow_only": True},
                    }
                ]
            },
        )
    if dashboard:
        _write_json(exp / "experiment_dashboard.json", {"registry": {"experiment_count": 1}})
        _write(out / "EXPERIMENT_DASHBOARD.md", "not an admission gate\nno active promotion\n")
    _write_json(
        exp / "mistake_pattern_library.json",
        {
            "patterns": [{"pattern_type": "benchmark_underperformance", "suggested_action": "compare_benchmark"}],
            "boundary": {"diagnostic_only": True, "promotion_triggered": False, "write_main_ledger": False},
        },
    )
    _write(out / "PARAMETER_SWEEP-EXP-a.md", "not an admission gate\nno orders/trades/portfolio written\noffline research only\n")
    _write(out / "STRATEGY_COMPARISON-a.md", "not an admission gate\nno active promotion\nno orders/trades/portfolio/accounts written\n")
    _write(
        out / "PROMOTION_SIMULATION-a.md",
        "This is a simulation only.\nNo strategy state was changed.\nNo active strategy was promoted.\nNo orders were written.\nThis is not an admission gate.\nThis report is offline research only.\n",
    )
    _write(
        out / "MISTAKE_PATTERN_LIBRARY.md",
        "This pattern library is diagnostic only.\nNo strategy was modified.\nNo parameter was modified.\nNo promotion was triggered.\nNo accounts were written.\nThis is not an admission gate.\nThis report is offline research only.\n",
    )
    return {"sweep": sweep, "comparison": comparison, "simulation": simulation}


def test_audit_json_and_markdown_generate(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths)

    result = audit_experiment_system(paths=system_audit_paths)

    assert Path(result["json_path"]).name == "experiment_system_audit.json"
    assert Path(result["report_path"]).name == "EXPERIMENT_SYSTEM_AUDIT.md"
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_required_artifact_missing_blocks_overall(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths)
    (system_audit_paths.data_dir / "experiments" / "parameter_sweep-EXP-a.json").unlink()
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False

    _seed_complete(system_audit_paths)
    (system_audit_paths.data_dir / "experiments" / "strategy_comparison-20260624-000001.json").unlink()
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False

    _seed_complete(system_audit_paths)
    (system_audit_paths.data_dir / "experiments" / "promotion_simulation-20260624-000001.json").unlink()
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False

    _seed_complete(system_audit_paths)
    (system_audit_paths.data_dir / "experiments" / "mistake_pattern_library.json").unlink()
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False


def test_registry_and_dashboard_missing_are_warnings_not_blocking(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths, registry=False, dashboard=False)

    result = audit_experiment_system(paths=system_audit_paths)

    assert result["overall_passed"] is True
    assert any("experiment_registry.json missing" in warning for warning in result["warnings"])
    assert any("experiment_dashboard.json missing" in warning for warning in result["warnings"])
    assert result["sections"]["registry"]["passed"] is False
    assert result["sections"]["experiment_dashboard"]["passed"] is False


def test_forbidden_statuses_and_write_main_ledger_are_blocking(system_audit_paths: ProjectPaths) -> None:
    artifacts = _seed_complete(system_audit_paths)
    payload = json.loads(artifacts["simulation"].read_text(encoding="utf-8"))
    payload["items"][0]["simulated_status"] = "active_normal"
    artifacts["simulation"].write_text(json.dumps(payload), encoding="utf-8")
    result = audit_experiment_system(paths=system_audit_paths)
    assert result["overall_passed"] is False

    artifacts = _seed_complete(system_audit_paths)
    payload = json.loads(artifacts["simulation"].read_text(encoding="utf-8"))
    payload["items"][0]["simulated_status"] = "live"
    artifacts["simulation"].write_text(json.dumps(payload), encoding="utf-8")
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False

    artifacts = _seed_complete(system_audit_paths)
    payload = json.loads(artifacts["sweep"].read_text(encoding="utf-8"))
    payload["constraints"]["write_main_ledger"] = True
    artifacts["sweep"].write_text(json.dumps(payload), encoding="utf-8")
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False


def test_invalid_recommendation_and_pattern_action_are_blocking(system_audit_paths: ProjectPaths) -> None:
    artifacts = _seed_complete(system_audit_paths)
    payload = json.loads(artifacts["comparison"].read_text(encoding="utf-8"))
    payload["items"][0]["current_recommendation"] = "approved_for_trading"
    artifacts["comparison"].write_text(json.dumps(payload), encoding="utf-8")
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False

    _seed_complete(system_audit_paths)
    library = system_audit_paths.data_dir / "experiments" / "mistake_pattern_library.json"
    payload = json.loads(library.read_text(encoding="utf-8"))
    payload["patterns"][0]["suggested_action"] = "deploy_live"
    library.write_text(json.dumps(payload), encoding="utf-8")
    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False


def test_boundary_promotion_triggered_blocks(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths)
    library = system_audit_paths.data_dir / "experiments" / "mistake_pattern_library.json"
    payload = json.loads(library.read_text(encoding="utf-8"))
    payload["boundary"]["promotion_triggered"] = True
    library.write_text(json.dumps(payload), encoding="utf-8")

    assert audit_experiment_system(paths=system_audit_paths)["overall_passed"] is False


def test_main_ledger_snapshot_not_modified(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths)
    orders = system_audit_paths.data_dir / "orders" / "existing.jsonl"
    orders.parent.mkdir(parents=True)
    orders.write_text("existing\n", encoding="utf-8")
    before = orders.read_text(encoding="utf-8")

    result = audit_experiment_system(paths=system_audit_paths)

    assert result["sections"]["main_ledger_pollution"]["passed"] is True
    assert orders.read_text(encoding="utf-8") == before


def test_report_contains_required_safety_boundary_and_recommendation(system_audit_paths: ProjectPaths) -> None:
    _seed_complete(system_audit_paths)

    result = audit_experiment_system(paths=system_audit_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This is not an admission gate." in report
    assert "This does not validate forward 30d dry-run." in report
    assert f"Recommended release tag:\n{RELEASE_CANDIDATE}" in report


def test_failing_audit_does_not_recommend_tag(system_audit_paths: ProjectPaths) -> None:
    result = audit_experiment_system(paths=system_audit_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert "Recommended release tag:" not in report


def test_cli_smoke_and_run_daily_not_called(
    system_audit_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    _seed_complete(system_audit_paths)
    monkeypatch.setattr(cli, "project_paths", lambda: system_audit_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(["audit-experiment-system"])

    captured = capsys.readouterr()
    assert result == 0
    assert "overall_passed" in captured.out


def test_empty_directory_generates_failed_report(system_audit_paths: ProjectPaths) -> None:
    result = audit_experiment_system(paths=system_audit_paths)

    assert result["overall_passed"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_artifact_inventory_lists_files(system_audit_paths: ProjectPaths) -> None:
    artifacts = _seed_complete(system_audit_paths)

    result = audit_experiment_system(paths=system_audit_paths)

    inventory = result["artifact_inventory"]
    assert str(artifacts["sweep"]) in inventory["parameter_sweeps"]
    assert str(artifacts["comparison"]) in inventory["strategy_comparisons"]
    assert str(artifacts["simulation"]) in inventory["promotion_simulations"]

