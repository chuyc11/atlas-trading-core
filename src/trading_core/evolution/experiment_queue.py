"""Experiment queue generation from proposed rule memory."""

from __future__ import annotations

from datetime import date as Date, datetime
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_jsonl


def update_experiment_queue(
    date: str,
    rule_memory: dict[str, Any],
    paths: ProjectPaths | None = None,
    max_new_experiments_per_day: int | None = None,
    cooldown_days_per_rule: int = 0,
    cooldown_days_per_strategy: int = 0,
) -> list[dict[str, Any]]:
    paths = paths or project_paths()
    path = paths.data_dir / "experiments" / "experiment_queue.jsonl"
    existing_rows = read_jsonl(path)
    existing_rule_ids = {row.get("rule_id") for row in existing_rows}
    rows = list(existing_rows)
    new_today = len([row for row in rows if row.get("date") == date])
    for rule in rule_memory.get("rules", []):
        if rule.get("status") != "proposed" or rule.get("rule_id") in existing_rule_ids:
            continue
        if max_new_experiments_per_day is not None and new_today >= max_new_experiments_per_day:
            continue
        if _in_cooldown(rule["rule_id"], str(rule["strategy_id"]), date, rows, cooldown_days_per_rule, cooldown_days_per_strategy):
            continue
        rows.append(
            {
                "experiment_id": f"EXP-{date.replace('-', '')}-{len(rows) + 1:03d}",
                "date": date,
                "rule_id": rule["rule_id"],
                "strategy_id": rule["strategy_id"],
                "hypothesis": rule["hypothesis"],
                "test_mode": "shadow",
                "min_days": 20,
                "min_signals": 10,
                "success_criteria": {
                    "positive_excess_return": True,
                    "max_mistake_rate": 0.30,
                    "max_drawdown": 0.03,
                },
                "status": "queued",
            }
        )
        new_today += 1
    write_jsonl(path, rows)
    return rows


def _in_cooldown(
    rule_id: str,
    strategy_id: str,
    date: str,
    rows: list[dict[str, Any]],
    cooldown_days_per_rule: int,
    cooldown_days_per_strategy: int,
) -> bool:
    current = _parse_date(date)
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        age = (current - row_date).days
        if cooldown_days_per_rule and row.get("rule_id") == rule_id and age < cooldown_days_per_rule:
            return True
        if cooldown_days_per_strategy and row.get("strategy_id") == strategy_id and age < cooldown_days_per_strategy:
            return True
    return False


def _parse_date(value: str) -> Date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()
