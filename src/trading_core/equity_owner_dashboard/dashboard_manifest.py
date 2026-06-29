"""Manifest and summary builders for owner dashboard."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_dashboard_manifest(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    generated_at: str,
    mode: str,
    executive_status_card: dict[str, Any],
    required_cards_present: bool,
    optional_cards_present: bool,
    warning_and_blocker_card: dict[str, Any],
    output_artifacts: dict[str, str],
    source_artifacts: dict[str, str],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-DASHBOARD-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "overall_status": executive_status_card["overall_status"],
        "required_cards_present": required_cards_present,
        "optional_cards_present": optional_cards_present,
        "blocking_count": warning_and_blocker_card.get("blocking_count", 0),
        "warning_count": warning_and_blocker_card.get("warning_count", 0),
        "output_artifacts": output_artifacts,
        "source_artifacts": source_artifacts,
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_dashboard_summary(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    mode: str,
    cards: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-DASHBOARD-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "mode": mode,
        "overall_status": manifest.get("overall_status"),
        "blocking_count": manifest.get("blocking_count"),
        "warning_count": manifest.get("warning_count"),
        "cards": {key: card.get("card_id") for key, card in cards.items()},
        "disclaimer": "本 dashboard 仅用于研究运行监控，不是交易指令，不连接券商，不下真实订单。",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

