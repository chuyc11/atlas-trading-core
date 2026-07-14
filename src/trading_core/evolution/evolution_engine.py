"""Run the first-stage evolution workflow."""

from __future__ import annotations

from typing import Any

from trading_core.evolution.experiment_queue import update_experiment_queue
from trading_core.evolution.mistake_classifier import classify_mistakes
from trading_core.evolution.promotion_evidence import evaluate_verified_shadow_promotion
from trading_core.evolution.rule_memory import update_rule_memory
from trading_core.evolution.signal_scorecard import score_signals
from trading_core.evolution.strategy_scorecard import score_strategies
from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


def run_evolution(
    date: str,
    signals: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    valuation: dict[str, Any],
    benchmark: dict[str, Any],
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    signal_scorecard = score_signals(date, signals, trades, valuation, benchmark, paths)
    mistakes = classify_mistakes(date, signal_scorecard, paths)
    strategy_scorecard = score_strategies(date, signal_scorecard, trades, paths)
    evolution_config = load_config("evolution.yaml")["evolution"]
    rule_config = evolution_config["rule_memory"]
    queue_config = evolution_config["experiment_queue"]
    rule_memory = update_rule_memory(
        date,
        mistakes,
        paths,
        min_evidence_count=int(rule_config["min_evidence_count"]),
        min_unique_days_for_rule=int(rule_config["min_unique_days_for_rule"]),
        min_unique_signals_for_rule=int(rule_config["min_unique_signals_for_rule"]),
        max_new_rules_per_day=int(rule_config["max_new_rules_per_day"]),
    )
    experiment_queue = update_experiment_queue(
        date,
        rule_memory,
        paths,
        max_new_experiments_per_day=int(queue_config["max_new_experiments_per_day"]),
        cooldown_days_per_rule=int(queue_config["cooldown_days_per_rule"]),
        cooldown_days_per_strategy=int(queue_config["cooldown_days_per_strategy"]),
    )
    promotion = evaluate_verified_shadow_promotion("momentum_shadow_v1", date, paths)
    summary = {
        "date": date,
        "signal_scorecard": signal_scorecard,
        "mistakes": mistakes,
        "strategy_scorecard": strategy_scorecard,
        "rule_memory": rule_memory,
        "experiment_queue_count": len(experiment_queue),
        "promotion_recommendation": promotion,
    }
    write_json(paths.data_dir / "evolution" / f"evolution-summary-{date}.json", summary)
    return summary
