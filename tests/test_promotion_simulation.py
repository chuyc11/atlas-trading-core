"""Tests for promotion simulation v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.promotion_simulation import (
    PromotionSimulationInputError,
    evaluate_simulation_item,
    run_promotion_simulation,
)
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def sim_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    (project_root / "data" / "experiments").mkdir(parents=True)
    (project_root / "outputs" / "experiments").mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_comparison(paths: ProjectPaths, payload: dict[str, Any]) -> Path:
    path = paths.data_dir / "experiments" / "strategy_comparison-test.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _item(**overrides: Any) -> dict[str, Any]:
    item = {
        "item_id": "RUN-001",
        "source_type": "parameter_sweep",
        "strategy_id": "momentum_strategy_v1",
        "current_recommendation": "watch",
        "metrics": {
            "excess_return": 0.02,
            "max_drawdown": 0.04,
            "trade_count": 12,
            "score": 6.0,
            "cost_ratio": 0.003,
        },
    }
    item.update(overrides)
    return item


def _evaluate(item: dict[str, Any], threshold: float = 5.0, strict: bool = False) -> dict[str, Any]:
    return evaluate_simulation_item(item, score_threshold=threshold, strict=strict, warnings=[])


def test_poor_parameter_sweep_item_rejects() -> None:
    result = _evaluate(_item(metrics={"excess_return": -0.01, "max_drawdown": 0.05, "trade_count": 12, "score": -2.5}))

    assert result["simulated_status"] == "reject"
    assert "negative_excess_return" in result["reason_codes"]


def test_excess_return_non_positive_rejects() -> None:
    result = _evaluate(_item(metrics={"excess_return": 0.0, "max_drawdown": 0.01, "trade_count": 20, "score": 20.0}))

    assert result["simulated_status"] == "reject"
    assert "negative_excess_return" in result["reason_codes"]


def test_excessive_drawdown_rejects() -> None:
    result = _evaluate(_item(metrics={"excess_return": 0.02, "max_drawdown": 0.081, "trade_count": 20, "score": 20.0}))

    assert result["simulated_status"] == "reject"
    assert "excessive_drawdown" in result["reason_codes"]


def test_insufficient_trade_count_rejects() -> None:
    result = _evaluate(_item(metrics={"excess_return": 0.02, "max_drawdown": 0.03, "trade_count": 9, "score": 20.0}))

    assert result["simulated_status"] == "reject"
    assert "insufficient_trade_count" in result["reason_codes"]


def test_general_positive_but_low_score_watches() -> None:
    result = _evaluate(_item(metrics={"excess_return": 0.02, "max_drawdown": 0.04, "trade_count": 12, "score": 4.9}))

    assert result["simulated_status"] == "watch"
    assert "positive_but_score_insufficient" in result["reason_codes"]


def test_good_item_becomes_shadow_candidate() -> None:
    result = _evaluate(_item(metrics={"excess_return": 0.03, "max_drawdown": 0.04, "trade_count": 12, "score": 6.5}))

    assert result["simulated_status"] == "shadow_candidate"
    assert "shadow_only_candidate" in result["reason_codes"]


def test_extremely_good_item_becomes_active_small_candidate_only() -> None:
    result = _evaluate(
        _item(
            current_recommendation="promising_shadow",
            metrics={
                "excess_return": 0.08,
                "max_drawdown": 0.02,
                "trade_count": 25,
                "score": 12.0,
                "cost_ratio": 0.002,
            },
        )
    )

    assert result["simulated_status"] == "active_small_candidate"
    assert "simulation_only_no_state_change" in result["reason_codes"]


def test_active_small_candidate_does_not_modify_strategy_state(sim_paths: ProjectPaths) -> None:
    strategy_state_path = sim_paths.data_dir / "strategy_versions" / "strategy_state.json"
    strategy_state_path.parent.mkdir(parents=True)
    strategy_state_path.write_text('{"momentum_strategy_v1":"shadow"}', encoding="utf-8")
    before = strategy_state_path.read_text(encoding="utf-8")
    comparison = _write_comparison(
        sim_paths,
        {
            "comparison_id": "CMP-test",
            "items": [
                _item(
                    current_recommendation="promising_shadow",
                    metrics={
                        "excess_return": 0.08,
                        "max_drawdown": 0.02,
                        "trade_count": 25,
                        "score": 12.0,
                        "cost_ratio": 0.002,
                    },
                )
            ],
        },
    )

    result = run_promotion_simulation(comparison, paths=sim_paths)

    assert result["summary"]["active_small_candidate"] == 1
    assert strategy_state_path.read_text(encoding="utf-8") == before
    assert result["boundary"]["strategy_state_changed"] is False


def test_json_does_not_produce_forbidden_statuses(sim_paths: ProjectPaths) -> None:
    comparison = _write_comparison(
        sim_paths,
        {
            "comparison_id": "CMP-test",
            "items": [
                _item(current_recommendation="promising_shadow", metrics={"excess_return": 0.08, "max_drawdown": 0.02, "trade_count": 25, "score": 12.0, "cost_ratio": 0.002}),
                _item(item_id="RUN-002", metrics={"excess_return": 0.03, "max_drawdown": 0.04, "trade_count": 12, "score": 6.0}),
            ],
        },
    )

    result = run_promotion_simulation(comparison, paths=sim_paths)
    statuses = {item["simulated_status"] for item in result["items"]}
    json_text = Path(result["json_path"]).read_text(encoding="utf-8")

    assert "active" not in statuses
    assert "active_normal" not in statuses
    assert "live" not in statuses
    assert "active_normal" not in json_text
    assert "live" not in json_text
    assert "promoted" not in json_text
    assert "approved_for_trading" not in json_text


def test_ml_shadow_missing_comparable_metrics_is_at_most_watch() -> None:
    result = _evaluate(
        {
            "item_id": "ML-001",
            "source_type": "ml_shadow_leaderboard",
            "model_id": "MLSHADOW-test",
            "shadow_recommendation": "watch",
            "metrics": {
                "score": 20.0,
                "signal_count": 25,
            },
        }
    )

    assert result["simulated_status"] == "watch"
    assert "insufficient_data" in result["reason_codes"]


def test_unknown_source_type_warns_and_rejects() -> None:
    warnings: list[str] = []
    result = evaluate_simulation_item(
        _item(source_type="mystery", metrics={"excess_return": 0.05, "max_drawdown": 0.01, "trade_count": 30, "score": 20.0}),
        warnings=warnings,
    )

    assert result["simulated_status"] == "reject"
    assert "unknown_source_type" in result["reason_codes"]
    assert warnings


def test_comparison_without_items_generates_empty_report(sim_paths: ProjectPaths) -> None:
    comparison = _write_comparison(sim_paths, {"comparison_id": "CMP-empty"})

    result = run_promotion_simulation(comparison, paths=sim_paths)

    assert result["summary"]["total_items"] == 0
    assert result["warnings"] == ["comparison JSON has no items"]
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_outputs_json_and_markdown_with_required_boundary_text(sim_paths: ProjectPaths) -> None:
    comparison = _write_comparison(sim_paths, {"comparison_id": "CMP-test", "items": [_item()]})

    result = run_promotion_simulation(comparison, paths=sim_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert "This is a simulation only." in report
    assert "No strategy state was changed." in report
    assert "No active strategy was promoted." in report
    assert "This is not an admission gate." in report


def test_does_not_write_orders_trades_portfolio_or_accounts(sim_paths: ProjectPaths) -> None:
    comparison = _write_comparison(sim_paths, {"comparison_id": "CMP-test", "items": [_item()]})

    run_promotion_simulation(comparison, paths=sim_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = sim_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []


def test_does_not_modify_comparison_or_registry(sim_paths: ProjectPaths) -> None:
    comparison = _write_comparison(sim_paths, {"comparison_id": "CMP-test", "items": [_item()]})
    registry = sim_paths.data_dir / "experiments" / "experiment_registry.json"
    registry.write_text('{"experiments":[]}', encoding="utf-8")
    before_comparison = comparison.read_text(encoding="utf-8")
    before_registry = registry.read_text(encoding="utf-8")

    run_promotion_simulation(comparison, paths=sim_paths)

    assert comparison.read_text(encoding="utf-8") == before_comparison
    assert registry.read_text(encoding="utf-8") == before_registry


def test_cli_smoke_and_does_not_call_run_daily(
    sim_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    _write_comparison(sim_paths, {"comparison_id": "CMP-test", "items": [_item()]})
    monkeypatch.setattr(cli, "project_paths", lambda: sim_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(["simulate-promotion", "--comparison", "data/experiments/strategy_comparison-test.json"])

    captured = capsys.readouterr()
    assert result == 0
    assert "simulation_id" in captured.out
    assert "shadow_candidate" in captured.out


def test_missing_comparison_file_has_clear_error(sim_paths: ProjectPaths) -> None:
    with pytest.raises(PromotionSimulationInputError, match="comparison file not found"):
        run_promotion_simulation("data/experiments/missing.json", paths=sim_paths)


def test_cli_missing_comparison_returns_error(
    sim_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: sim_paths)

    result = cli.main(["simulate-promotion", "--comparison", "data/experiments/missing.json"])

    captured = capsys.readouterr()
    assert result == 1
    assert "comparison file not found" in captured.out
