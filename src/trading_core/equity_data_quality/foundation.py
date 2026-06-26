"""One-command A-share data foundation builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices
from trading_core.equity_data.daily_basic import ingest_a_share_daily_basic
from trading_core.equity_data.daily_price import ingest_a_share_daily_prices
from trading_core.equity_data_quality.coverage_audit import audit_a_share_data_coverage
from trading_core.equity_data_quality.schema_audit import audit_a_share_data_schema
from trading_core.equity_data_quality.source_manifest import build_a_share_data_source_manifest
from trading_core.equity_fundamental.basic_financials import ingest_a_share_basic_financials
from trading_core.equity_industry.classification import ingest_a_share_industry_classification
from trading_core.equity_universe.calendar import build_a_share_trading_calendar
from trading_core.equity_universe.master import build_a_share_equity_master
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_a_share_data_foundation(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    source_manifest = build_a_share_data_source_manifest(paths=paths)
    master = build_a_share_equity_master(paths=paths)
    calendar = build_a_share_trading_calendar(paths=paths)
    daily_price = ingest_a_share_daily_prices(paths=paths)
    adjusted = ingest_a_share_adjusted_prices(paths=paths)
    daily_basic = ingest_a_share_daily_basic(paths=paths)
    industry = ingest_a_share_industry_classification(paths=paths)
    financials = ingest_a_share_basic_financials(paths=paths)
    coverage = audit_a_share_data_coverage(paths=paths)
    schema = audit_a_share_data_schema(paths=paths)
    source_manifest = build_a_share_data_source_manifest(paths=paths)
    return {
        "foundation_id": "A-SHARE-DATA-FOUNDATION",
        "source_manifest": source_manifest,
        "equity_master": master,
        "trading_calendar": calendar,
        "daily_price": daily_price,
        "adjusted_price": adjusted,
        "daily_basic": daily_basic,
        "industry": industry,
        "financials": financials,
        "coverage_audit": coverage,
        "schema_audit": schema,
        "overall_passed": coverage["overall_passed"] and schema["overall_passed"],
    }
