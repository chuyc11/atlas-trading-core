from __future__ import annotations

from trading_core.equity_portfolios.industry_constraints import industry_bucket, industry_cap_violations, industry_exposure


def test_industry_bucket_uses_auditable_fallback_for_unclassified() -> None:
    row = {"symbol": "688001.SH", "industry_level_1": "Unclassified", "industry_level_2": "STAR", "board": "STAR"}

    assert industry_bucket(row) == "Unclassified/STAR/688"


def test_industry_exposure_and_violations() -> None:
    records = [
        {"industry": "Finance", "industry_level_1": "Finance", "industry_level_2": "Bank", "target_weight": 0.7},
        {"industry": "Industrial", "industry_level_1": "Industrial", "industry_level_2": "Machinery", "target_weight": 0.3},
    ]

    exposure = industry_exposure(records)

    assert exposure["industry_weight_by_level_1"]["Finance"] == 0.7
    assert industry_cap_violations(records, 0.5)[0]["industry"] == "Finance"

