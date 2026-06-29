"""Manifest and summary builders for owner monitoring."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_monitoring.monitoring_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_monitoring_manifest(
    *,
    as_of_date: str,
    generated_at: str,
    mode: str,
    monitoring_status_card: dict[str, Any],
    output_artifacts: dict[str, str],
    source_artifacts: dict[str, str],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-MONITORING-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "overall_monitoring_status": monitoring_status_card.get("overall_monitoring_status"),
        "run_history_observation_count": monitoring_status_card.get("run_history_observation_count"),
        "trend_analysis_available": monitoring_status_card.get("trend_analysis_available"),
        "critical_alert_count": monitoring_status_card.get("critical_alert_count"),
        "warning_alert_count": monitoring_status_card.get("warning_alert_count"),
        "blocking_count": monitoring_status_card.get("blocking_count"),
        "output_artifacts": output_artifacts,
        "source_artifacts": source_artifacts,
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_monitoring_summary(*, as_of_date: str, mode: str, manifest: dict[str, Any], warning_trend_snapshot: dict[str, Any], owner_alert_summary_card: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-MONITORING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "overall_monitoring_status": manifest.get("overall_monitoring_status"),
        "run_history_observation_count": manifest.get("run_history_observation_count"),
        "trend_analysis_available": manifest.get("trend_analysis_available"),
        "insufficient_history_for_trends": not bool(manifest.get("trend_analysis_available")),
        "warning_count_current": warning_trend_snapshot.get("warning_count_current"),
        "critical_alert_count": manifest.get("critical_alert_count"),
        "warning_alert_count": manifest.get("warning_alert_count"),
        "known_non_blocking_alert_count": len(owner_alert_summary_card.get("known_non_blocking_alerts", [])),
        "external_notifications_sent": False,
        "disclaimer": "本地监控和 alert 仅用于研究系统健康检查，不是交易指令，不连接券商，不下真实订单。",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
