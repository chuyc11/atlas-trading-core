"""Rule memory generated from repeated mistakes."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_json


def update_rule_memory(
    date: str,
    mistakes: list[dict[str, Any]],
    paths: ProjectPaths | None = None,
    min_evidence_count: int = 5,
    min_unique_days_for_rule: int = 1,
    min_unique_signals_for_rule: int = 1,
    max_new_rules_per_day: int | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    path = paths.data_dir / "evolution" / "rule_memory.json"
    payload = read_json(path, default={"rules": [], "observations": {}})
    existing = {rule["rule_id"]: rule for rule in payload.get("rules", [])}
    observations = dict(payload.get("observations", {}))

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for mistake in mistakes:
        grouped[(str(mistake.get("strategy_id")), str(mistake.get("mistake_type")))].append(mistake)

    new_rules_today = 0
    for (strategy_id, mistake_type), rows in grouped.items():
        rule_id = f"RULE-{strategy_id}-{mistake_type}".replace("_", "-").upper()
        obs = observations.get(
            rule_id,
            {
                "rule_id": rule_id,
                "strategy_id": strategy_id,
                "mistake_type": mistake_type,
                "evidence_count": 0,
                "first_seen": date,
                "last_seen": date,
                "dates": [],
                "signal_ids": [],
                "evidence_keys": [],
            },
        )
        evidence_keys = set(obs.get("evidence_keys", []))
        dates = set(obs.get("dates", []))
        signal_ids = set(obs.get("signal_ids", []))
        for row in rows:
            row_date = str(row.get("date") or date)
            signal_id = str(row.get("signal_id"))
            key = f"{row_date}:{signal_id}:{row.get('mistake_type')}"
            if key in evidence_keys:
                continue
            evidence_keys.add(key)
            dates.add(row_date)
            signal_ids.add(signal_id)
        obs["evidence_keys"] = sorted(evidence_keys)
        obs["dates"] = sorted(dates)
        obs["signal_ids"] = sorted(signal_ids)
        obs["evidence_count"] = len(evidence_keys)
        obs["last_seen"] = date
        observations[rule_id] = obs
        if int(obs["evidence_count"]) < min_evidence_count:
            continue
        if len(dates) < min_unique_days_for_rule:
            continue
        if len(signal_ids) < min_unique_signals_for_rule:
            continue
        if max_new_rules_per_day is not None and rule_id not in existing and new_rules_today >= max_new_rules_per_day:
            continue
        if rule_id in existing:
            existing[rule_id]["evidence_count"] = int(obs["evidence_count"])
            existing[rule_id]["unique_days"] = len(dates)
            existing[rule_id]["unique_signals"] = len(signal_ids)
            existing[rule_id]["last_seen"] = date
            continue
        existing[rule_id] = {
            "rule_id": rule_id,
            "strategy_id": strategy_id,
            "mistake_type": mistake_type,
            "hypothesis": f"When {strategy_id} produces {mistake_type}, reduce confidence or keep in shadow.",
            "evidence_count": int(obs["evidence_count"]),
            "unique_days": len(dates),
            "unique_signals": len(signal_ids),
            "first_seen": obs["first_seen"],
            "last_seen": date,
            "status": "proposed",
        }
        new_rules_today += 1

    output = {"rules": list(existing.values()), "observations": observations}
    write_json(path, output)
    return output
