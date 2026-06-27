"""Audit feature readiness after A-share historical backfill."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import HISTORICAL_BOUNDARY, HISTORICAL_DATA_SOURCE_UPGRADE_VERSION, HISTORICAL_TARGET_VERSION, RECOMMENDED_NEXT_VERSION, data_quality_dir, markdown_boundary, read_json, write_report
from trading_core.equity_data_quality.historical_coverage_audit import audit_a_share_historical_panel_coverage
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


FORBIDDEN_WORDING = [
    "guaranteed profit",
    "model can make money",
    "AI selected profitable stocks",
    "live trading ready",
    "real orders placed",
    "broker connected",
    "official forward dry-run day2 executed",
    "scores generated",
    "candidates generated",
    "virtual portfolio generated",
    "保证盈利",
    "一定赚钱",
    "实盘就绪",
    "真实下单",
    "已连接券商",
    "已生成股票推荐",
    "已生成候选股",
    "已生成评分",
]


def audit_a_share_feature_readiness(
    *,
    paths: ProjectPaths | None = None,
    minimum_filter_symbols: int = 3000,
    minimum_mid_symbols: int = 2500,
) -> dict[str, Any]:
    paths = default_paths(paths)
    coverage_audit = read_json(data_quality_dir(paths) / "a_share_historical_panel_coverage_audit.json")
    if not coverage_audit:
        coverage_audit = audit_a_share_historical_panel_coverage(paths=paths)
    coverage = coverage_audit.get("coverage", {})
    minimum_requirements = {
        "has_20d_history": coverage.get("symbols_with_20d_history", 0) >= minimum_filter_symbols,
        "has_60d_history": coverage.get("symbols_with_60d_history", 0) >= minimum_filter_symbols,
        "has_120d_history": coverage.get("symbols_with_120d_history", 0) >= minimum_filter_symbols,
        "has_250d_history": coverage.get("symbols_with_250d_history", 0) >= minimum_mid_symbols,
        "has_adjusted_prices": coverage.get("adjusted_price_coverage_ratio", 0.0) > 0,
        "has_daily_basic_history": coverage.get("daily_basic_history_coverage_ratio", 0.0) > 0,
        "has_financial_quarters": coverage.get("financial_quarter_coverage_ratio", 0.0) > 0,
    }
    readiness = {
        "tradable_universe_filter_ready": minimum_requirements["has_20d_history"] and minimum_requirements["has_60d_history"] and minimum_requirements["has_120d_history"],
        "short_horizon_feature_ready": minimum_requirements["has_60d_history"],
        "mid_horizon_feature_ready": minimum_requirements["has_250d_history"],
        "long_horizon_feature_ready": minimum_requirements["has_250d_history"] and minimum_requirements["has_adjusted_prices"] and minimum_requirements["has_financial_quarters"],
        "walk_forward_validation_ready": False,
    }
    forbidden_hits = _forbidden_hits(readiness, minimum_requirements)
    blocking = list(coverage_audit.get("blocking_reasons", []))
    if not readiness["tradable_universe_filter_ready"]:
        blocking.append("tradable_universe_filter_ready=false")
    if not readiness["short_horizon_feature_ready"]:
        blocking.append("short_horizon_feature_ready=false")
    if not readiness["mid_horizon_feature_ready"]:
        blocking.append("mid_horizon_feature_ready=false")
    if forbidden_hits:
        blocking.append("forbidden_wording_detected")
    long_horizon_gap_reasons = []
    if not minimum_requirements["has_250d_history"]:
        long_horizon_gap_reasons.append("insufficient symbols with 250d history")
    if not minimum_requirements["has_adjusted_prices"]:
        long_horizon_gap_reasons.append("adjusted price coverage unavailable")
    if not minimum_requirements["has_financial_quarters"]:
        long_horizon_gap_reasons.append("financial quarter coverage unavailable")
    recommended_next_version = RECOMMENDED_NEXT_VERSION if not blocking and readiness["tradable_universe_filter_ready"] else HISTORICAL_DATA_SOURCE_UPGRADE_VERSION
    payload: dict[str, Any] = {
        "audit_id": "A-SHARE-FEATURE-READINESS-AUDIT",
        "target_version": HISTORICAL_TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["walk-forward validation remains deferred"] + ([] if readiness["long_horizon_feature_ready"] else ["long-horizon features have partial readiness"]),
        "readiness": readiness,
        "minimum_requirements": minimum_requirements,
        "long_horizon_gap_reasons": long_horizon_gap_reasons,
        "financial_coverage_gap": coverage.get("financial_quarter_coverage_ratio", 0.0) < 1.0,
        "recommended_future_data_source": "paid or authorized historical A-share data source with bulk full-market OHLCV and adjustment coverage",
        "forbidden_wording_hits": forbidden_hits,
        "boundary": dict(HISTORICAL_BOUNDARY),
        "recommended_next_version": recommended_next_version,
    }
    json_path = data_quality_dir(paths) / "a_share_feature_readiness_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_FEATURE_READINESS_AUDIT.md"
    lines = [
        "# A-Share Feature Readiness Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- readiness: {readiness}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def _forbidden_hits(*texts: Any) -> list[str]:
    combined = " ".join(str(text) for text in texts)
    return [term for term in FORBIDDEN_WORDING if term.lower() in combined.lower()]
