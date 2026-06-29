"""Warning recurrence comparison for repeated builds."""

from __future__ import annotations

import json

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_repeatability_warning_comparison(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    execution_record: dict,
) -> dict:
    paths = default_paths(paths)
    first_path = paths.data_dir / "equity_current_day_builds" / "daily" / as_of_date / "gated_build_summary.json"
    first = _load(first_path).get("warnings", [])
    second = execution_record.get("warnings", [])
    return {
        "warning_comparison_id": "A-SHARE-REPEATABILITY-WARNING-COMPARISON",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "first_warning_count": len(first),
        "second_warning_count": len(second),
        "recurring_warnings": sorted(set(first) & set(second)),
        "new_warnings": sorted(set(second) - set(first)),
        "resolved_warnings": sorted(set(first) - set(second)),
        "warnings_stable": sorted(set(first)) == sorted(set(second)),
    }


def _load(path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

