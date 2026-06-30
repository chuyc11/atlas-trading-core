"""Boundary digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import BOUNDARY, TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_boundary_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    ops_boundary = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_boundary_check.json")
    return {
        "digest_id": "A-SHARE-BOUNDARY-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY,
        "upstream_ops_boundary_passed": ops_boundary.get("overall_passed", False),
        "forbidden_artifacts_present": ops_boundary.get("forbidden_artifacts_present", []),
        "forbidden_wording_positive_hits": ops_boundary.get("forbidden_wording_positive_hits", []),
    }

