from __future__ import annotations

from pathlib import Path

from trading_core.evolution.experiment_queue import update_experiment_queue
from trading_core.evolution.rule_memory import update_rule_memory
from trading_core.storage.file_paths import project_paths


def _mistake(date: str, signal_id: str, strategy: str = "macro") -> dict[str, object]:
    return {
        "date": date,
        "signal_id": signal_id,
        "strategy_id": strategy,
        "mistake_type": "benchmark_underperformance",
    }


def test_same_day_duplicate_errors_do_not_generate_infinite_rules(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    mistakes = [_mistake("2026-06-23", "S1") for _ in range(10)]
    memory = update_rule_memory(
        "2026-06-23",
        mistakes,
        paths,
        min_evidence_count=5,
        min_unique_days_for_rule=3,
        min_unique_signals_for_rule=5,
    )
    assert memory["rules"] == []
    obs = next(iter(memory["observations"].values()))
    assert obs["evidence_count"] == 1


def test_unique_days_and_signals_required_for_rule(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    for index in range(5):
        memory = update_rule_memory(
            "2026-06-23",
            [_mistake("2026-06-23", f"S{index}")],
            paths,
            min_evidence_count=5,
            min_unique_days_for_rule=3,
            min_unique_signals_for_rule=5,
        )
    assert memory["rules"] == []

    for index, date in enumerate(["2026-06-24", "2026-06-25", "2026-06-26", "2026-06-27", "2026-06-28"], 10):
        memory = update_rule_memory(
            date,
            [_mistake(date, f"S{index}")],
            paths,
            min_evidence_count=5,
            min_unique_days_for_rule=3,
            min_unique_signals_for_rule=5,
        )
    assert len(memory["rules"]) == 1


def test_experiment_queue_cooldown_and_daily_limit(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    memory = {
        "rules": [
            {"rule_id": f"R{i}", "strategy_id": "macro", "hypothesis": "h", "status": "proposed"}
            for i in range(5)
        ]
    }
    first = update_experiment_queue(
        "2026-06-23",
        memory,
        paths,
        max_new_experiments_per_day=3,
        cooldown_days_per_rule=10,
        cooldown_days_per_strategy=0,
    )
    assert len(first) == 3

    second = update_experiment_queue(
        "2026-06-24",
        memory,
        paths,
        max_new_experiments_per_day=3,
        cooldown_days_per_rule=10,
        cooldown_days_per_strategy=10,
    )
    assert second == first
