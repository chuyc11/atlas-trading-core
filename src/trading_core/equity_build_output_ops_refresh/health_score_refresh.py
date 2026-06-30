"""Build-output health score refresh."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_health_score_refresh(*, paths: ProjectPaths, as_of_date: str) -> dict:
    original = load_json(paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_health_score_card.json")
    dashboard = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_summary.json")
    score = int(original.get("score", 0))
    return {
        "card_id": "A-SHARE-BUILD-OUTPUT-HEALTH-SCORE-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "score": score,
        "grade": original.get("grade", _grade(score)),
        "overall_status": original.get("overall_status", "passed" if score >= 80 else "passed_with_warnings"),
        "build_output_dashboard_overall_passed": dashboard.get("overall_passed", False),
        "business_output_drift_count": dashboard.get("business_output_drift_count"),
        "protected_path_modifications_detected": dashboard.get("protected_path_modifications_detected"),
        "score_explanation": original.get("score_explanation", []),
        "deterministic": True,
    }


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 60:
        return "C"
    return "D"

