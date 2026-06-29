"""Protected path dashboard card."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION


def build_protected_path_card(*, as_of_date: str, protected_check: dict) -> dict:
    return {
        "card_id": "BUILD_OUTPUT_PROTECTED_PATH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "preexisting_protected_paths_allowed": protected_check.get("preexisting_protected_paths_allowed", True),
        "preexisting_protected_paths": protected_check.get("preexisting_protected_paths", []),
        "protected_path_modifications_detected": protected_check.get("protected_path_modifications_detected", True),
        "new_protected_paths_created": protected_check.get("new_protected_paths_created", []),
        "protected_files_modified": protected_check.get("protected_files_modified", []),
        "protected_files_created": protected_check.get("protected_files_created", []),
        "protected_files_deleted": protected_check.get("protected_files_deleted", []),
        "overall_passed": protected_check.get("overall_passed", False),
    }

