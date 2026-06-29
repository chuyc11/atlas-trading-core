"""Deterministic operations health score."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


def build_ops_health_score_card(*, as_of_date: str, required_modules_passed: bool, issue_summary: dict[str, Any], critical_alert_count: int = 0) -> dict[str, Any]:
    blocking = int(issue_summary.get("blocking_issue_count", 0))
    warnings = int(issue_summary.get("warning_issue_count", 0))
    known = int(issue_summary.get("known_non_blocking_issue_count", 0))
    score = 100
    explanation = ["base score=100"]
    if blocking:
        score -= 40
        explanation.append("minus 40 for blocking issues")
    if not required_modules_passed:
        score -= 25
        explanation.append("minus 25 for failed required module audit")
    critical_penalty = 10 * critical_alert_count
    score -= critical_penalty
    if critical_penalty:
        explanation.append(f"minus {critical_penalty} for critical alerts")
    warning_penalty = min(warnings * 3, 30)
    score -= warning_penalty
    if warning_penalty:
        explanation.append(f"minus {warning_penalty} for warning issues")
    known_penalty = min(known, 10)
    score -= known_penalty
    if known_penalty:
        explanation.append(f"minus {known_penalty} for known non-blocking issues")
    score = max(0, score)
    return {
        "card_id": "OPS_HEALTH_SCORE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "score": score,
        "grade": grade_for_score(score),
        "overall_status": "failed" if blocking or not required_modules_passed else ("passed_with_warnings" if warnings or known else "passed"),
        "required_modules_passed": required_modules_passed,
        "blocking_issue_count": blocking,
        "warning_issue_count": warnings,
        "known_non_blocking_issue_count": known,
        "critical_alert_count": critical_alert_count,
        "score_explanation": explanation,
    }


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"
