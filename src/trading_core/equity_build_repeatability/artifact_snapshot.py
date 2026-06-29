"""Artifact snapshots for repeat build comparisons."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from trading_core.equity_build_repeatability.deterministic_normalization import normalized_json_hash
from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


SNAPSHOT_ROOTS = [
    ("workflow", "data/equity_workflows/daily/{as_of_date}"),
    ("current_day", "data/equity_current_day_runs/daily/{as_of_date}"),
    ("features", "data/equity_features/daily/{as_of_date}"),
    ("scores", "data/equity_scores/daily/{as_of_date}"),
    ("selection", "data/equity_selection/daily/{as_of_date}"),
    ("portfolios", "data/equity_portfolios/daily/{as_of_date}"),
    ("briefing", "data/equity_briefings/daily/{as_of_date}"),
    ("tracking", "data/equity_portfolio_tracking/daily/{as_of_date}"),
    ("benchmarks", "data/equity_benchmarks/daily/{as_of_date}"),
    ("performance", "data/equity_performance/daily/{as_of_date}"),
    ("attribution", "data/equity_attribution/daily/{as_of_date}"),
    ("gated_build", "data/equity_current_day_builds/daily/{as_of_date}"),
    ("repeatability", "data/equity_build_repeatability/daily/{as_of_date}"),
    ("audits", "data/equity_data_quality"),
    ("workflow_reports", "outputs/equity_workflows/daily/{as_of_date}"),
    ("current_day_reports", "outputs/equity_current_day_runs/daily/{as_of_date}"),
    ("briefing_reports", "outputs/equity_briefings/daily/{as_of_date}"),
    ("repeatability_reports", "outputs/equity_build_repeatability/daily/{as_of_date}"),
    ("audit_reports", "outputs/audit"),
]


def build_artifact_snapshot(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    snapshot_id: str,
) -> dict:
    paths = default_paths(paths)
    entries = []
    for stage, template in SNAPSHOT_ROOTS:
        root = paths.project_root / template.format(as_of_date=as_of_date)
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            entries.append(_entry(paths, path, stage, as_of_date))
    return {
        "snapshot_id": snapshot_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "artifact_count": len(entries),
        "entries": entries,
    }


def _entry(paths: ProjectPaths, path: Path, stage: str, as_of_date: str) -> dict:
    stat = path.stat()
    rel = relative(path, paths.project_root)
    return {
        "artifact_id": _artifact_id(rel, as_of_date),
        "path": rel,
        "exists": path.exists(),
        "required": _is_required(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "normalized_sha256": _normalized_hash(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
        "artifact_type": path.suffix.lower().lstrip(".") or "file",
        "stage": stage,
    }


def _artifact_id(path: str, as_of_date: str) -> str:
    return path.replace(as_of_date, "{as_of_date}").replace("\\", "/")


def _is_required(path: Path) -> bool:
    name = path.name
    return name.endswith(".json") or name.endswith(".md") or name.endswith(".parquet")


def _normalized_hash(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return normalized_json_hash(path.read_text(encoding="utf-8", errors="ignore"))
    if suffix == ".parquet":
        try:
            import pandas as pd

            frame = pd.read_parquet(path)
            generated_columns = [
                col
                for col in frame.columns
                if str(col) in {"created_at", "generated_at", "updated_at"}
                or str(col).endswith("_created_at")
                or str(col).endswith("_generated_at")
                or str(col).endswith("_updated_at")
            ]
            if generated_columns:
                frame = frame.drop(columns=generated_columns)
            payload = {
                "columns": [str(col) for col in frame.columns],
                "index": [str(value) for value in frame.index.tolist()],
                "data": frame.astype(object).where(pd.notna(frame), None).values.tolist(),
            }
            encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
            return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        except Exception:
            return None
    return None
