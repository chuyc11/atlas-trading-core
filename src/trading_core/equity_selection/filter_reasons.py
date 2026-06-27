"""Reason taxonomy for the A-share tradable universe filter."""

from __future__ import annotations


BUCKET_STRICT = "strict_tradable_universe"
BUCKET_CAUTION = "caution_universe"
BUCKET_EXCLUDED = "excluded_universe"
BUCKET_UNKNOWN = "unknown_status_universe"

STAGE_ORDER = [
    "universe_eligibility",
    "st_risk_warning",
    "listing_age",
    "suspension_missing_price",
    "liquidity",
    "market_cap",
    "price",
    "price_sanity",
    "limit_status",
    "data_coverage",
]

REASON_STAGE = {
    "not_in_master": "universe_eligibility",
    "unsupported_exchange": "universe_eligibility",
    "inactive": "universe_eligibility",
    "delisted": "universe_eligibility",
    "not_yet_listed": "universe_eligibility",
    "missing_list_date": "universe_eligibility",
    "st_stock": "st_risk_warning",
    "risk_warning_stock": "st_risk_warning",
    "delisting_board": "st_risk_warning",
    "name_contains_st": "st_risk_warning",
    "st_status_unknown": "st_risk_warning",
    "new_listing_lt_120_trading_days": "listing_age",
    "listing_age_unknown": "listing_age",
    "missing_price_on_as_of_date": "suspension_missing_price",
    "insufficient_20d_trading_observations": "suspension_missing_price",
    "insufficient_60d_trading_observations": "suspension_missing_price",
    "possible_suspension": "suspension_missing_price",
    "avg_amount_20d_below_threshold": "liquidity",
    "avg_amount_60d_below_threshold": "liquidity",
    "amount_missing": "liquidity",
    "liquidity_unknown": "liquidity",
    "total_mv_below_threshold": "market_cap",
    "circ_mv_below_threshold": "market_cap",
    "market_cap_missing": "market_cap",
    "market_cap_unit_unknown": "market_cap",
    "close_price_below_threshold": "price",
    "close_price_missing": "price",
    "invalid_price_record": "price_sanity",
    "invalid_high_low": "price_sanity",
    "invalid_volume": "price_sanity",
    "invalid_amount": "price_sanity",
    "one_word_limit_up_risk": "limit_status",
    "one_word_limit_down_risk": "limit_status",
    "limit_status_unknown": "limit_status",
    "insufficient_20d_history": "data_coverage",
    "insufficient_60d_history": "data_coverage",
    "insufficient_120d_history": "data_coverage",
    "insufficient_250d_history": "data_coverage",
}

CAUTION_REASONS = {"st_status_unknown", "limit_status_unknown"}

UNKNOWN_REASONS = {
    "listing_age_unknown",
    "amount_missing",
    "liquidity_unknown",
    "market_cap_missing",
    "market_cap_unit_unknown",
}

HARD_EXCLUSION_REASONS = set(REASON_STAGE) - CAUTION_REASONS - UNKNOWN_REASONS


def stage_for_reason(reason: str) -> str:
    return REASON_STAGE.get(reason, "unknown")


def primary_reason(reasons: list[str]) -> str:
    if not reasons:
        return ""
    ordered = {stage: index for index, stage in enumerate(STAGE_ORDER)}
    return sorted(reasons, key=lambda item: (ordered.get(stage_for_reason(item), 999), reasons.index(item)))[0]


def bucket_for_reasons(reasons: list[str]) -> str:
    if any(reason in HARD_EXCLUSION_REASONS for reason in reasons):
        return BUCKET_EXCLUDED
    if any(reason in UNKNOWN_REASONS for reason in reasons):
        return BUCKET_UNKNOWN
    if any(reason in CAUTION_REASONS for reason in reasons):
        return BUCKET_CAUTION
    return BUCKET_STRICT

