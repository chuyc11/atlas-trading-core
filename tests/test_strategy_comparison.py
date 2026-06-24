"""Tests for read-only strategy comparison artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.strategy_comparison import (
    StrategyComparisonInputError,
    build_strategy_comparison,
)
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def comparison_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    (project_root / "data" / "experiments").mkdir(parents=True)
    (project_root / "data" / "shadow").mkdir(parents=True)
    (project_root / "outputs" / "experiments").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _sweep_path(paths: ProjectPaths) -> Path:
    return _write_json(
        paths.data_dir / "experiments" / "parameter_sweep-EXP-test.json",
        {
            "experiment_id": "EXP-test",
            "strategy_id": "momentum_strategy_v1",
            "runs": [
                {
                    "run_id": "RUN-001",
                    "strategy_id": "momentum_strategy_v1",
                    "excess_return_vs_equal_etf": -0.01,
                    "max_drawdown": 0.04,
                    "trade_count": 12,
                    "score": -2.0,
                    "cost_ratio": 0.001,
                },
                {
                    "run_id": "RUN-002",
                    "strategy_id": "momentum_strategy_v1",
                    "excess_return_vs_equal_etf": 0.03,
                    "max_drawdown": 0.02,
                    "trade_count": 20,
                    "score": 7.0,
                    "cost_ratio": 0.001,
                },
            ],
            "best_shadow_candidate": {"run_id": "RUN-002", "score": 7.0},
        },
    )


def _leaderboard_path(paths: ProjectPaths) -> Path:
    return _write_json(
        paths.data_dir / "shadow" / "ml_shadow_leaderboard-test.json",
        {
            "model_id": "MLSHADOW-test",
            "prediction_count": 100,
            "signal_count": 25,
            "mean_rank_ic": 0.02,
            "shadow_recommendation": "watch",
        },
    )


def test_compare_strategy_inputs_generates_json_and_markdown(comparison_paths: ProjectPaths) -> None:
    result = build_strategy_comparison([_sweep_path(comparison_paths), _leaderboard_path(comparison_paths)], comparison_paths)

    assert result["comparison_id"].startswith("CMP-")
    assert result["item_count"] == 3
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert "STRATEGY_COMPARISON-" in Path(result["report_path"]).name


def test_parameter_sweep_runs_become_comparable_items(comparison_paths: ProjectPaths) -> None:
    result = build_strategy_comparison([_sweep_path(comparison_paths)], comparison_paths)
    items = {item["item_id"]: item for item in result["items"]}

    assert items["RUN-001"]["source_type"] == "parameter_sweep"
    assert items["RUN-001"]["current_recommendation"] == "reject"
    assert items["RUN-002"]["current_recommendation"] == "promising_shadow"
    assert items["RUN-002"]["metrics"]["excess_return"] == 0.03
    assert result["best_by_score"] == "RUN-002"


def test_ml_shadow_leaderboard_becomes_watch_item(comparison_paths: ProjectPaths) -> None:
    result = build_strategy_comparison([_leaderboard_path(comparison_paths)], comparison_paths)

    item = result["items"][0]
    assert item["source_type"] == "ml_shadow_leaderboard"
    assert item["model_id"] == "MLSHADOW-test"
    assert item["current_recommendation"] == "watch"
    assert item["metrics"]["score"] == 0.02


def test_compare_strategies_does_not_write_trading_state(comparison_paths: ProjectPaths) -> None:
    build_strategy_comparison([_sweep_path(comparison_paths)], comparison_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts", "strategy_versions"]:
        directory = comparison_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_compare_strategies_cli_smoke(
    comparison_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    sweep = _sweep_path(comparison_paths)
    monkeypatch.setattr(cli, "project_paths", lambda: comparison_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(["compare-strategies", "--inputs", str(sweep)])

    captured = capsys.readouterr()
    assert result == 0
    assert "comparison_id" in captured.out
    assert (comparison_paths.outputs_dir / "experiments").exists()


def test_compare_strategies_missing_input_is_clear(comparison_paths: ProjectPaths) -> None:
    with pytest.raises(StrategyComparisonInputError, match="input artifact not found"):
        build_strategy_comparison(["data/experiments/missing.json"], comparison_paths)

