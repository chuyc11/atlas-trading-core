"""Protected path digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_protected_path_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    protected = load_json(paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "protected_path_modification_check.json")
    card = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_protected_path_card.json")
    return {
        "digest_id": "A-SHARE-PROTECTED-PATH-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "preexisting_protected_paths": card.get("preexisting_protected_paths", protected.get("preexisting_protected_paths", [])),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected", True),
        "protected_files_modified": protected.get("protected_files_modified", []),
        "protected_files_created": protected.get("protected_files_created", []),
        "protected_files_deleted": protected.get("protected_files_deleted", []),
        "overall_passed": protected.get("protected_path_modifications_detected", True) is False,
    }

