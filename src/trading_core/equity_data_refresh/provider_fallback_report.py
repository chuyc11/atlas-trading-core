"""Provider fallback report builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION


def build_provider_fallback_report(*, as_of_date: str, provider_execution_log: dict[str, Any]) -> dict[str, Any]:
    fallbacks = [row for row in provider_execution_log.get("records", []) if row.get("fallback_used")]
    return {
        "fallback_report_id": "A-SHARE-DATA-REFRESH-PROVIDER-FALLBACK-REPORT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "fallback_used": bool(fallbacks),
        "fallback_count": len(fallbacks),
        "fallbacks": fallbacks,
        "policy": {
            "never_silent_fallback": True,
            "fallback_must_preserve_schema": True,
            "fallback_to_stale_data_requires_warning_or_blocking": True,
        },
    }
