"""Fail-closed promotion gate backed by verified out-of-sample evidence."""

from __future__ import annotations

from datetime import date as Date
from math import isfinite
from pathlib import Path
from typing import Any

from trading_core.evolution.promotion_gate import recommend_promotion
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json


REQUIRED_EVIDENCE_KIND = "out_of_sample_shadow"


def evaluate_verified_shadow_promotion(
    strategy_id: str,
    date: str,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    evidence_path = latest_verified_evidence(strategy_id, date, paths)
    if evidence_path is None:
        return insufficient_evidence(strategy_id, ["missing_verified_shadow_evaluation"])

    payload = read_json(evidence_path, default={})
    failures = validate_evidence(payload, strategy_id, date)
    if failures:
        result = insufficient_evidence(strategy_id, failures)
        result["evidence_path"] = str(evidence_path)
        return result

    metrics = {
        "days": int(payload["unique_days"]),
        "signals": int(payload["signal_count"]),
        "excess_return": float(payload["net_excess_return"]),
        "mistake_rate": float(payload["mistake_rate"]),
        "max_drawdown": abs(float(payload["max_drawdown"])),
    }
    result = recommend_promotion("shadow", metrics)
    result.update(
        {
            "strategy_id": strategy_id,
            "evidence_status": "verified",
            "evidence_path": str(evidence_path),
            "metrics": metrics,
        }
    )
    return result


def latest_verified_evidence(strategy_id: str, date: str, paths: ProjectPaths) -> Path | None:
    cutoff = Date.fromisoformat(date)
    candidates: list[tuple[Date, Path]] = []
    for path in (paths.data_dir / "experiments").glob(f"shadow_evaluation-{strategy_id}-*.json"):
        raw_date = path.stem.rsplit("-", 3)[-3:]
        try:
            evidence_date = Date.fromisoformat("-".join(raw_date))
        except ValueError:
            continue
        if evidence_date <= cutoff:
            candidates.append((evidence_date, path))
    return max(candidates, key=lambda item: item[0])[1] if candidates else None


def validate_evidence(payload: dict[str, Any], strategy_id: str, date: str) -> list[str]:
    if not isinstance(payload, dict):
        return ["evidence_not_object"]
    failures: list[str] = []
    if payload.get("evidence_kind") != REQUIRED_EVIDENCE_KIND:
        failures.append("invalid_evidence_kind")
    if payload.get("strategy_id") != strategy_id:
        failures.append("strategy_id_mismatch")
    try:
        as_of = Date.fromisoformat(str(payload.get("as_of_date", "")))
        if as_of > Date.fromisoformat(date):
            failures.append("future_dated_evidence")
    except ValueError:
        failures.append("invalid_as_of_date")
    for field, failure in (("unique_days", "invalid_unique_days"), ("signal_count", "invalid_signal_count")):
        try:
            value = int(payload.get(field, 0))
        except (TypeError, ValueError):
            failures.append(failure)
        else:
            if value < 1:
                failures.append(failure)
    for field in ("net_excess_return", "mistake_rate", "max_drawdown"):
        try:
            value = float(payload.get(field))
        except (TypeError, ValueError):
            failures.append(f"invalid_{field}")
        else:
            if not isfinite(value):
                failures.append(f"invalid_{field}")
            if field == "mistake_rate" and not 0.0 <= value <= 1.0:
                failures.append("mistake_rate_out_of_range")
    if payload.get("future_data_flag") is not False:
        failures.append("future_data_not_cleared")
    if payload.get("benchmark_comparison") is not True:
        failures.append("benchmark_comparison_missing")
    if payload.get("costs_included") is not True:
        failures.append("costs_not_included")
    source_hashes = payload.get("source_hashes")
    if not isinstance(source_hashes, list) or not source_hashes or not all(str(item).strip() for item in source_hashes):
        failures.append("source_lineage_missing")
    return failures


def insufficient_evidence(strategy_id: str, failures: list[str]) -> dict[str, Any]:
    return {
        "strategy_id": strategy_id,
        "current_state": "shadow",
        "recommended_state": "shadow",
        "recommendation": "keep_shadow_insufficient_verified_evidence",
        "auto_applied": False,
        "evidence_status": "insufficient",
        "failed_evidence_rules": failures,
    }
