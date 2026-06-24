"""Tests for the read-only experiment dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.experiment_dashboard import (
    build_dashboard_markdown,
    build_experiment_dashboard,
)
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def dashboard_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    (project_root / "data" / "experiments").mkdir(parents=True)
    (project_root / "data" / "shadow").mkdir(parents=True)
    (project_root / "outputs" / "experiments").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_registry(paths: ProjectPaths) -> None:
    _write_json(
        paths.data_dir / "experiments" / "experiment_registry.json",
        {
            "experiments": [
                {
                    "experiment_id": "EXP-sweep-momentum-20260624",
                    "strategy_id": "momentum_strategy_v1",
                    "experiment_type": "parameter_sweep",
                    "status": "registered",
                    "mode": "shadow",
                }
            ]
        },
    )


def _seed_sweep(paths: ProjectPaths, experiment_id: str = "EXP-sweep-a") -> None:
    _write_json(
        paths.data_dir / "experiments" / f"parameter_sweep-{experiment_id}.json",
        {
            "experiment_id": experiment_id,
            "runs": [{"run_id": f"{experiment_id}-RUN-001", "score": 1.2}],
            "best_shadow_candidate": {"run_id": f"{experiment_id}-RUN-001", "score": 1.2},
            "warnings": [],
        },
    )


def _seed_leaderboard(paths: ProjectPaths, model_id: str = "MLSHADOW-test") -> None:
    _write_json(
        paths.data_dir / "shadow" / f"ml_shadow_leaderboard-2024-01-01-2024-01-31-{model_id}.json",
        {
            "model_id": model_id,
            "prediction_count": 100,
            "signal_count": 25,
            "mean_rank_ic": 0.01,
            "shadow_recommendation": "watch",
        },
    )


def _seed_comparison(paths: ProjectPaths, comparison_id: str = "CMP-test") -> None:
    _write_json(
        paths.data_dir / "experiments" / f"strategy_comparison-{comparison_id}.json",
        {
            "comparison_id": comparison_id,
            "items": [
                {"strategy_id": "strategy_a", "score": 1.0, "excess_return": 0.01},
                {"strategy_id": "strategy_b", "score": 2.0, "excess_return": 0.02},
            ],
            "warnings": [],
        },
    )


def test_dashboard_generates_json_and_markdown(dashboard_paths: ProjectPaths) -> None:
    _seed_registry(dashboard_paths)
    _seed_sweep(dashboard_paths)
    _seed_leaderboard(dashboard_paths)
    _seed_comparison(dashboard_paths)

    result = build_experiment_dashboard(paths=dashboard_paths)

    json_path = Path(result["json_path"])
    report_path = Path(result["report_path"])
    assert json_path.exists()
    assert report_path.exists()
    assert json.loads(json_path.read_text(encoding="utf-8"))["dashboard_id"].startswith("EXPDASH-")
    assert "# Experiment Dashboard" in report_path.read_text(encoding="utf-8")


def test_missing_inputs_do_not_crash(dashboard_paths: ProjectPaths) -> None:
    result = build_experiment_dashboard(paths=dashboard_paths)

    assert result["registry"]["experiment_count"] == 0
    assert result["parameter_sweeps"] == []
    assert result["ml_shadow_results"] == []
    assert result["strategy_comparisons"] == []
    assert "experiment_registry.json not found" in result["warnings"]
    assert "no parameter sweep results found" in result["warnings"]
    assert "no ML shadow leaderboard found" in result["warnings"]
    assert "no strategy comparison found" in result["warnings"]

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "No registered experiments." in report
    assert "No parameter sweep results found." in report
    assert "No ML shadow leaderboard found." in report
    assert "No strategy comparison found." in report


def test_multiple_sweeps_and_comparisons_are_summarized(dashboard_paths: ProjectPaths) -> None:
    _seed_sweep(dashboard_paths, "EXP-sweep-a")
    _seed_sweep(dashboard_paths, "EXP-sweep-b")
    _seed_comparison(dashboard_paths, "CMP-a")
    _seed_comparison(dashboard_paths, "CMP-b")

    result = build_experiment_dashboard(paths=dashboard_paths)

    assert len(result["parameter_sweeps"]) == 2
    assert len(result["strategy_comparisons"]) == 2
    assert {item["experiment_id"] for item in result["parameter_sweeps"]} == {"EXP-sweep-a", "EXP-sweep-b"}
    assert {item["comparison_id"] for item in result["strategy_comparisons"]} == {"CMP-a", "CMP-b"}


def test_unknown_json_is_warned_and_skipped(dashboard_paths: ProjectPaths) -> None:
    _write_json(paths := dashboard_paths.data_dir / "experiments" / "unknown-artifact.json", {"x": 1})

    result = build_experiment_dashboard(paths=dashboard_paths)

    assert f"unknown JSON skipped: {paths.name}" in result["warnings"]


def test_safety_boundary_written_to_report(dashboard_paths: ProjectPaths) -> None:
    result = build_experiment_dashboard(paths=dashboard_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "shadow_only=true" in report
    assert "write_main_ledger=false" in report
    assert "allow_active=false" in report
    assert "no live trading" in report
    assert "no broker" in report
    assert "no active promotion" in report
    assert "no main ledger writes" in report
    assert "not an admission gate" in report
    assert "dashboard is read-only" in report


def test_report_does_not_describe_shadow_recommendations_as_live(dashboard_paths: ProjectPaths) -> None:
    _seed_leaderboard(dashboard_paths, "MLSHADOW-watch")
    result = build_experiment_dashboard(paths=dashboard_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8").lower()

    assert "watch" in report
    assert "promising_shadow" in report
    assert "observation labels only" in report
    assert "no active promotion" in report


def test_dashboard_does_not_write_orders_trades_or_portfolio(dashboard_paths: ProjectPaths) -> None:
    build_experiment_dashboard(paths=dashboard_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = dashboard_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_dashboard_does_not_modify_registry(dashboard_paths: ProjectPaths) -> None:
    _seed_registry(dashboard_paths)
    registry_path = dashboard_paths.data_dir / "experiments" / "experiment_registry.json"
    before = registry_path.read_text(encoding="utf-8")

    build_experiment_dashboard(paths=dashboard_paths)

    assert registry_path.read_text(encoding="utf-8") == before


def test_build_markdown_empty_sections() -> None:
    markdown = build_dashboard_markdown(
        {
            "dashboard_id": "EXPDASH-test",
            "created_at": "2026-06-24T00:00:00Z",
            "registry": {"experiment_count": 0, "experiments": []},
            "parameter_sweeps": [],
            "ml_shadow_results": [],
            "strategy_comparisons": [],
            "warnings": [],
        }
    )

    assert "No registered experiments." in markdown
    assert "No parameter sweep results found." in markdown
    assert "No ML shadow leaderboard found." in markdown
    assert "No strategy comparison found." in markdown


def test_experiment_dashboard_cli_smoke(
    dashboard_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    _seed_sweep(dashboard_paths)
    monkeypatch.setattr(cli, "project_paths", lambda: dashboard_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(
        [
            "experiment-dashboard",
            "--experiments-dir",
            "data/experiments",
            "--shadow-dir",
            "data/shadow",
            "--output-dir",
            "outputs/experiments",
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert "dashboard_id" in captured.out
    assert "parameter_sweep_count" in captured.out
    assert (dashboard_paths.data_dir / "experiments" / "experiment_dashboard.json").exists()

