"""Tests for mistake pattern library v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.mistake_pattern_library import (
    SUGGESTED_ACTIONS,
    MistakePatternLibraryInputError,
    update_mistake_pattern_library,
)
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def library_paths(tmp_path: Path) -> ProjectPaths:
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


def _comparison(paths: ProjectPaths, items: list[dict[str, Any]]) -> Path:
    return _write_json(paths.data_dir / "experiments" / "strategy_comparison-test.json", {"comparison_id": "CMP-test", "items": items})


def _sweep(paths: ProjectPaths, runs: list[dict[str, Any]], warnings: list[str] | None = None) -> Path:
    return _write_json(
        paths.data_dir / "experiments" / "parameter_sweep-EXP-test.json",
        {
            "experiment_id": "EXP-test",
            "strategy_id": "momentum_strategy_v1",
            "runs": runs,
            "warnings": warnings or [],
        },
    )


def _promotion(paths: ProjectPaths, items: list[dict[str, Any]]) -> Path:
    return _write_json(paths.data_dir / "experiments" / "promotion_simulation-test.json", {"simulation_id": "PROMOSIM-test", "items": items})


def _leaderboard(paths: ProjectPaths, payload: dict[str, Any]) -> Path:
    return _write_json(paths.data_dir / "shadow" / "ml_shadow_leaderboard-test.json", payload)


def _types(result: dict[str, Any]) -> set[str]:
    return {pattern["pattern_type"] for pattern in result["patterns"]}


def _pattern(result: dict[str, Any], pattern_type: str) -> dict[str, Any]:
    return next(pattern for pattern in result["patterns"] if pattern["pattern_type"] == pattern_type)


def test_generates_benchmark_underperformance_from_comparison(library_paths: ProjectPaths) -> None:
    path = _comparison(
        library_paths,
        [
            {"item_id": "A", "source_type": "parameter_sweep", "strategy_id": "s1", "metrics": {"excess_return": -0.01, "trade_count": 20}},
            {"item_id": "B", "source_type": "parameter_sweep", "strategy_id": "s2", "metrics": {"excess_return": -0.02, "trade_count": 20}},
        ],
    )

    result = update_mistake_pattern_library([path], paths=library_paths)

    pattern = _pattern(result, "benchmark_underperformance")
    assert pattern["evidence_count"] == 2
    assert pattern["suggested_action"] == "compare_benchmark"


def test_generates_high_turnover_low_excess_from_sweep(library_paths: ProjectPaths) -> None:
    path = _sweep(
        library_paths,
        [
            {"run_id": "R1", "turnover": 0.6, "excess_return_vs_equal_etf": -0.01, "cost_ratio": 0.001, "score": -1},
            {"run_id": "R2", "turnover": 0.7, "excess_return_vs_equal_etf": -0.02, "cost_ratio": 0.001, "score": -2},
        ],
    )

    result = update_mistake_pattern_library([path], paths=library_paths)

    pattern = _pattern(result, "high_turnover_low_excess")
    assert pattern["severity"] == "medium"
    assert pattern["suggested_action"] == "reduce_turnover"


def test_generates_unstable_rank_ic_from_ml_leaderboard(library_paths: ProjectPaths) -> None:
    path = _leaderboard(
        library_paths,
        {
            "model_id": "ML-test",
            "shadow_recommendation": "watch",
            "mean_rank_ic": 0.01,
            "prediction_count": 100,
            "rank_ic_by_date": {"d1": 0.8, "d2": -0.8},
        },
    )

    result = update_mistake_pattern_library([path], paths=library_paths)

    pattern = _pattern(result, "unstable_rank_ic")
    assert pattern["status"] == "monitoring"
    assert pattern["affected_models"] == ["ML-test"]


def test_generates_low_sample_size_from_promotion_simulation(library_paths: ProjectPaths) -> None:
    path = _promotion(
        library_paths,
        [
            {"item_id": "A", "source_type": "parameter_sweep", "simulated_status": "watch", "reason_codes": ["insufficient_data"], "metrics": {"trade_count": 20}},
            {"item_id": "B", "source_type": "parameter_sweep", "simulated_status": "watch", "reason_codes": ["missing_trade_count"], "metrics": {"trade_count": 20}},
        ],
    )

    result = update_mistake_pattern_library([path], paths=library_paths)

    pattern = _pattern(result, "low_sample_size")
    assert pattern["suggested_action"] == "require_more_data"
    assert pattern["evidence_count"] == 2


def test_generates_data_quality_sensitive_from_warnings_and_reason_codes(library_paths: ProjectPaths) -> None:
    sweep = _sweep(library_paths, [], warnings=["missing_price fallback used"])
    promo = _promotion(
        library_paths,
        [
            {"item_id": "A", "source_type": "parameter_sweep", "reason_codes": ["data_quality_gap"], "metrics": {}},
        ],
    )

    result = update_mistake_pattern_library([sweep, promo], paths=library_paths)

    pattern = _pattern(result, "data_quality_sensitive")
    assert pattern["suggested_action"] == "inspect_data_quality"
    assert pattern["evidence_count"] == 2


def test_insufficient_evidence_does_not_create_formal_pattern(library_paths: ProjectPaths) -> None:
    path = _comparison(
        library_paths,
        [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}],
    )

    result = update_mistake_pattern_library([path], min_evidence=2, paths=library_paths)

    assert result["patterns"] == []
    assert any("insufficient evidence for pattern_type=benchmark_underperformance" in warning for warning in result["warnings"])


def test_unknown_json_is_warned_and_skipped(library_paths: ProjectPaths) -> None:
    path = _write_json(library_paths.data_dir / "experiments" / "unknown.json", {"hello": "world"})

    result = update_mistake_pattern_library([path], paths=library_paths)

    assert result["patterns"] == []
    assert any("unknown input skipped" in warning for warning in result["warnings"])


def test_malformed_json_is_clear_warning(library_paths: ProjectPaths) -> None:
    path = library_paths.data_dir / "experiments" / "bad.json"
    path.write_text("{not-json", encoding="utf-8")

    result = update_mistake_pattern_library([path], paths=library_paths)

    assert result["patterns"] == []
    assert any("malformed input skipped" in warning for warning in result["warnings"])


def test_empty_inputs_error_is_clear(library_paths: ProjectPaths) -> None:
    with pytest.raises(MistakePatternLibraryInputError, match="at least one input artifact is required"):
        update_mistake_pattern_library([], paths=library_paths)


def test_missing_input_error_is_clear(library_paths: ProjectPaths) -> None:
    with pytest.raises(MistakePatternLibraryInputError, match="input artifact not found"):
        update_mistake_pattern_library(["data/experiments/missing.json"], paths=library_paths)


def test_empty_but_legal_input_generates_empty_library_and_report(library_paths: ProjectPaths) -> None:
    path = _comparison(library_paths, [])

    result = update_mistake_pattern_library([path], paths=library_paths)

    assert result["patterns"] == []
    assert Path(result["json_path"]).exists()
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "No formal mistake patterns detected." in report


def test_pattern_ids_and_sorting_are_stable(library_paths: ProjectPaths) -> None:
    comparison = _comparison(
        library_paths,
        [{"item_id": f"C{i}", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}} for i in range(10)],
    )
    promo = _promotion(
        library_paths,
        [
            {"item_id": "P1", "source_type": "parameter_sweep", "simulated_status": "watch", "reason_codes": ["insufficient_data"], "metrics": {}},
            {"item_id": "P2", "source_type": "parameter_sweep", "simulated_status": "watch", "reason_codes": ["missing_score"], "metrics": {}},
        ],
    )

    result = update_mistake_pattern_library([comparison, promo], paths=library_paths)

    assert [pattern["pattern_id"] for pattern in result["patterns"]] == ["PATTERN-0001", "PATTERN-0002"]
    assert result["patterns"][0]["pattern_type"] == "benchmark_underperformance"
    assert result["patterns"][0]["severity"] == "high"


def test_affected_entities_are_deduped_and_sorted(library_paths: ProjectPaths) -> None:
    path = _comparison(
        library_paths,
        [
            {"item_id": "A", "source_type": "parameter_sweep", "strategy_id": "z", "model_id": "m2", "metrics": {"excess_return": -0.01}},
            {"item_id": "B", "source_type": "parameter_sweep", "strategy_id": "a", "model_id": "m1", "metrics": {"excess_return": -0.02}},
            {"item_id": "C", "source_type": "parameter_sweep", "strategy_id": "a", "model_id": "m1", "metrics": {"excess_return": -0.03}},
        ],
    )

    result = update_mistake_pattern_library([path], paths=library_paths)
    pattern = _pattern(result, "benchmark_underperformance")

    assert pattern["affected_strategies"] == ["a", "z"]
    assert pattern["affected_models"] == ["m1", "m2"]


def test_affected_experiments_are_deduped_and_sorted(library_paths: ProjectPaths) -> None:
    first = _sweep(library_paths, [{"run_id": "A", "excess_return_vs_equal_etf": -0.01}, {"run_id": "B", "excess_return_vs_equal_etf": -0.02}])
    second = _write_json(
        library_paths.data_dir / "experiments" / "parameter_sweep-EXP-b.json",
        {"experiment_id": "EXP-b", "strategy_id": "s", "runs": [{"run_id": "C", "excess_return_vs_equal_etf": -0.03}, {"run_id": "D", "excess_return_vs_equal_etf": -0.04}]},
    )

    result = update_mistake_pattern_library([second, first], paths=library_paths)
    pattern = _pattern(result, "benchmark_underperformance")

    assert pattern["affected_experiments"] == ["EXP-b", "EXP-test"]


def test_evidence_examples_are_limited_to_20(library_paths: ProjectPaths) -> None:
    path = _comparison(
        library_paths,
        [{"item_id": f"C{i}", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}} for i in range(25)],
    )

    result = update_mistake_pattern_library([path], paths=library_paths)
    pattern = _pattern(result, "benchmark_underperformance")

    assert pattern["evidence_count"] == 25
    assert len(pattern["evidence"]) == 20


def test_markdown_contains_required_diagnostic_boundary(library_paths: ProjectPaths) -> None:
    path = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])

    result = update_mistake_pattern_library([path], paths=library_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This pattern library is diagnostic only." in report
    assert "No strategy was modified." in report
    assert "No parameter was modified." in report
    assert "No promotion was triggered." in report
    assert "This is not an admission gate." in report


def test_does_not_write_trading_or_account_files(library_paths: ProjectPaths) -> None:
    path = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])

    result = update_mistake_pattern_library([path], paths=library_paths)

    for bucket in ["orders", "trades", "portfolio", "portfolios", "accounts"]:
        directory = library_paths.data_dir / bucket
        assert not directory.exists() or list(directory.iterdir()) == []
    assert result["boundary"]["strategy_modified"] is False
    assert result["boundary"]["parameters_modified"] is False
    assert result["boundary"]["promotion_triggered"] is False


def test_does_not_modify_inputs_registry_or_strategy_state(library_paths: ProjectPaths) -> None:
    path = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])
    registry = library_paths.data_dir / "experiments" / "experiment_registry.json"
    state = library_paths.data_dir / "strategy_versions" / "state.json"
    registry.write_text('{"experiments":[]}', encoding="utf-8")
    state.parent.mkdir(parents=True)
    state.write_text('{"s":"shadow"}', encoding="utf-8")
    before_input = path.read_text(encoding="utf-8")
    before_registry = registry.read_text(encoding="utf-8")
    before_state = state.read_text(encoding="utf-8")

    update_mistake_pattern_library([path], paths=library_paths)

    assert path.read_text(encoding="utf-8") == before_input
    assert registry.read_text(encoding="utf-8") == before_registry
    assert state.read_text(encoding="utf-8") == before_state


def test_cli_smoke_and_does_not_call_run_daily(
    library_paths: ProjectPaths,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from trading_core import cli

    path = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])
    monkeypatch.setattr(cli, "project_paths", lambda: library_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    result = cli.main(["update-mistake-patterns", "--inputs", str(path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "library_id" in captured.out
    assert "benchmark_underperformance" in captured.out


def test_multi_input_generates_multiple_patterns(library_paths: ProjectPaths) -> None:
    comparison = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])
    sweep = _sweep(library_paths, [{"run_id": "R1", "turnover": 0.6, "excess_return_vs_equal_etf": -0.01}, {"run_id": "R2", "turnover": 0.7, "excess_return_vs_equal_etf": -0.02}])
    ml = _leaderboard(library_paths, {"model_id": "ML", "shadow_recommendation": "weak", "rank_ic_by_date": {"a": -0.1, "b": 0.2}})

    result = update_mistake_pattern_library([comparison, sweep, ml], paths=library_paths)

    assert {"benchmark_underperformance", "high_turnover_low_excess", "unstable_rank_ic"}.issubset(_types(result))


def test_suggested_actions_are_from_allowed_set(library_paths: ProjectPaths) -> None:
    comparison = _comparison(library_paths, [{"item_id": "A", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.01}}, {"item_id": "B", "source_type": "parameter_sweep", "metrics": {"excess_return": -0.02}}])

    result = update_mistake_pattern_library([comparison], paths=library_paths)

    assert all(pattern["suggested_action"] in SUGGESTED_ACTIONS for pattern in result["patterns"])

