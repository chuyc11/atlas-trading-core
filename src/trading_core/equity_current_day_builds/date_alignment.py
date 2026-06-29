"""Date alignment checks for v0.8.7 gated build."""

from __future__ import annotations

import json

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_gated_build_date_alignment(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    allow_date_mismatch: bool = False,
) -> dict:
    paths = default_paths(paths)

    audits = {
        "ops_history_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
        ),
        "ops_center_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json"
        ),
        "current_day_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
        ),
        "data_refresh_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json"
        ),
    }

    resolved_dates = {}
    misaligned = []
    for key, path in audits.items():
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                resolved = payload.get("as_of_date", payload.get("resolved_as_of_date", None))
                resolved_dates[key] = resolved
                if resolved and resolved != as_of_date:
                    misaligned.append({"source": key, "expected": as_of_date, "found": resolved})
            except Exception:
                resolved_dates[key] = None
        else:
            resolved_dates[key] = None

    blocking = []
    warnings = []
    if misaligned:
        if allow_date_mismatch:
            warnings.extend(f"{m['source']}: expected {m['expected']}, found {m['found']}" for m in misaligned)
        else:
            blocking.extend(f"{m['source']}: expected {m['expected']}, found {m['found']}" for m in misaligned)

    return {
        "alignment_id": "A-SHARE-GATED-BUILD-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_dates": resolved_dates,
        "misaligned": misaligned,
        "allow_date_mismatch": allow_date_mismatch,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(blocking),
        "warnings": sorted(warnings),
    }
