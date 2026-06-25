"""A-share and ETF tradability rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BLOCKED_STATUSES = {"suspended", "missing_price", "st_flagged", "new_listing_restricted", "delisting_risk", "unknown_status"}
SUPPORTED_STATUSES = ["tradable", "suspended", "missing_price", "limit_up", "limit_down", "st_flagged", "new_listing_restricted", "delisting_risk", "unknown_status"]


@dataclass(frozen=True)
class TradabilityDecision:
    allowed: bool
    reason: str
    status: str
    side: str

    def to_dict(self) -> dict[str, Any]:
        return {"allowed": self.allowed, "reason": self.reason, "status": self.status, "side": self.side}


def evaluate_tradability(status: str, side: str, *, price_available: bool = True, status_date: str | None = None, execution_date: str | None = None) -> TradabilityDecision:
    normalized = status if status in SUPPORTED_STATUSES else "unknown_status"
    side = side.upper()
    if status_date and execution_date and status_date > execution_date:
        return TradabilityDecision(False, "future_status_rejected", normalized, side)
    if not price_available or normalized == "missing_price":
        return TradabilityDecision(False, "missing_price_rejected", normalized, side)
    if normalized == "tradable":
        return TradabilityDecision(True, "tradable", normalized, side)
    if normalized == "limit_up" and side == "BUY":
        return TradabilityDecision(False, "limit_up_buy_rejected", normalized, side)
    if normalized == "limit_up" and side == "SELL":
        return TradabilityDecision(True, "limit_up_sell_allowed_with_valid_price", normalized, side)
    if normalized == "limit_down" and side == "SELL":
        return TradabilityDecision(False, "limit_down_sell_rejected", normalized, side)
    if normalized == "limit_down" and side == "BUY":
        return TradabilityDecision(True, "limit_down_buy_allowed_with_valid_price", normalized, side)
    if normalized == "suspended":
        return TradabilityDecision(False, "suspended_order_rejected", normalized, side)
    if normalized == "st_flagged":
        return TradabilityDecision(False, "st_flagged_requires_manual_acceptance", normalized, side)
    if normalized == "new_listing_restricted":
        return TradabilityDecision(False, "new_listing_restricted", normalized, side)
    if normalized == "delisting_risk":
        return TradabilityDecision(False, "delisting_risk_rejected", normalized, side)
    return TradabilityDecision(False, "unknown_status_fail_closed", normalized, side)

