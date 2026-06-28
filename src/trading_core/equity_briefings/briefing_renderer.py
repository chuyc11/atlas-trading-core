"""Markdown renderer for v0.7.7 A-share daily stock selection briefing."""

from __future__ import annotations

from typing import Any


def render_daily_stock_selection_briefing(payload: dict[str, Any]) -> str:
    lines = [
        f"# A 股全市场 AI 选股研究简报 - {payload['as_of_date']}",
        "",
        f"- as_of_date: {payload['as_of_date']}",
        f"- generated_at: {payload['generated_at']}",
        f"- current_version: {payload['target_version']}",
        "- input_chain: v0.7.3 features -> v0.7.4 scores -> v0.7.5 candidates -> v0.7.6 virtual portfolios -> v0.7.7 briefing",
        "- data_sources: existing score, candidate, virtual portfolio, exposure, risk/liquidity, and audit artifacts",
        "",
        "## 今日总体结论",
        "",
        *_bullet_lines(payload["executive_summary"]),
        "",
        "## 数据日期和覆盖状态",
        "",
        *_coverage_lines(payload),
        "",
        "## 长期研究候选 Top 10",
        "",
        *_candidate_table(payload["long_candidates_top10"], "LongScore", "LongRank", "FundamentalScore"),
        "",
        "## 中期研究候选 Top 10",
        "",
        *_candidate_table(payload["mid_candidates_top10"], "MidScore", "MidRank", "IndustryScore"),
        "",
        "## 短期研究候选 Top 10",
        "",
        *_candidate_table(payload["short_candidates_top10"], "ShortScore", "ShortRank", "IndustryScore"),
        "",
        "## 多周期共振候选",
        "",
        "多周期共振只是多周期评分靠前，不代表确定上涨；这里用于后续研究跟踪排序。",
        "",
        *_multi_horizon_table(payload["multi_horizon_candidates_top10"]),
        "",
        "## 风险降级股票摘要",
        "",
        f"- 风险降级数量: {payload['risk_downgraded_summary'].get('count', 0)}",
        "- 这些股票分数靠前，但由于风险、流动性或置信度问题，不应进入主虚拟组合。",
        "",
        *_risk_downgraded_table(payload["risk_downgraded_summary"].get("top10", [])),
        "",
        "## 长期虚拟组合摘要",
        "",
        *_portfolio_lines(payload["virtual_portfolios"]["long"]),
        "",
        "## 中期虚拟组合摘要",
        "",
        *_portfolio_lines(payload["virtual_portfolios"]["mid"]),
        "",
        "## 短期虚拟组合摘要",
        "",
        *_portfolio_lines(payload["virtual_portfolios"]["short"]),
        "",
        "## 行业分布和集中度",
        "",
        *_industry_lines(payload["industry_exposure_summary"]),
        "",
        "## 风险与流动性提示",
        "",
        *_risk_liquidity_lines(payload["risk_liquidity_summary"]),
        "",
        "## 数据与审计状态",
        "",
        *_audit_status_lines(payload["audit_status"]),
        "",
        "## 不要误读",
        "",
        *_bullet_lines(payload["do_not_misread"]),
        "",
        "## 下一步跟踪建议",
        "",
        *_bullet_lines(payload["next_tracking_actions"]),
        "",
        "## 明确免责声明",
        "",
        "- 本简报仅汇总既有研究 artifacts，面向人工阅读和后续虚拟跟踪。",
        "- 本简报不生成新的评分、候选或虚拟组合。",
        "- 本简报不构成投资建议、收益承诺或实盘操作依据。",
    ]
    return "\n".join(lines) + "\n"


def _bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def _coverage_lines(payload: dict[str, Any]) -> list[str]:
    versions = payload["input_versions"]
    return [
        f"- strict tradable universe: {versions.get('strict_tradable_count', 0)}",
        f"- scored symbols: {versions.get('scored_symbols', 0)}",
        f"- candidate version: {versions.get('candidate_version', '')}",
        f"- score version: {versions.get('score_version', '')}",
        f"- feature version: {versions.get('feature_version', '')}",
        f"- portfolio version: {versions.get('portfolio_version', '')}",
        f"- source_trace_complete: {str(payload.get('source_trace_complete', False)).lower()}",
    ]


def _candidate_table(rows: list[dict[str, Any]], score_key: str, rank_key: str, extra_key: str) -> list[str]:
    lines = [
        f"| Rank | Symbol | Name | Industry | {score_key} | {rank_key} | Risk | Liquidity | {extra_key} | Composite | Inclusion | Risk Notes |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('rank', '')} | {row.get('symbol', '')} | {row.get('name', '')} | {row.get('industry_level_1', '')} | {_num(row.get(score_key))} | {_num(row.get(rank_key), 0)} | {_num(row.get('RiskScore'))} | {_num(row.get('LiquidityScore'))} | {_num(row.get(extra_key))} | {_num(row.get('CompositeOpportunityScore'))} | {_join(row.get('primary_inclusion_reasons'))} | {_join(row.get('main_risk_reasons'))} |"
        )
    return lines


def _multi_horizon_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Symbol | Name | Overlap | Best Horizon | Long | Mid | Short | Composite | Strengths | Risk Notes |",
        "|---|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('symbol', '')} | {row.get('name', '')} | {row.get('horizon_overlap_type', '')} | {row.get('best_horizon', '')} | {_num(row.get('LongScore'))} | {_num(row.get('MidScore'))} | {_num(row.get('ShortScore'))} | {_num(row.get('CompositeOpportunityScore'))} | {_join(row.get('primary_strengths'))} | {_join(row.get('risk_notes'))} |"
        )
    return lines


def _risk_downgraded_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Symbol | Name | Trigger | Score | Downgrade Reason | Risk | Liquidity | Confidence |",
        "|---|---|---|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('symbol', '')} | {row.get('name', '')} | {row.get('trigger_horizon', '')} | {_num(row.get('trigger_score'))} | {row.get('downgrade_reason', '')} | {_num(row.get('RiskScore'))} | {_num(row.get('LiquidityScore'))} | {_num(row.get('confidence'))} |"
        )
    return lines


def _portfolio_lines(portfolio: dict[str, Any]) -> list[str]:
    lines = [
        f"- holding_count: {portfolio.get('holding_count', 0)}",
        f"- weight_sum: {_num(portfolio.get('weight_sum'))}",
        f"- max_single_weight: {_pct(portfolio.get('max_single_weight'))}",
        f"- max_industry_weight: {_pct(portfolio.get('max_industry_weight'))}",
        "- 虚拟组合仅用于研究跟踪，不是实盘配置建议。",
        "",
        "| Weight Rank | Symbol | Name | Target Weight | Score | Risk | Liquidity | Industry |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for row in portfolio.get("top10_holdings", []):
        lines.append(
            f"| {row.get('weight_rank', '')} | {row.get('symbol', '')} | {row.get('name', '')} | {_pct(row.get('target_weight'))} | {_num(row.get('horizon_score'))} | {_num(row.get('RiskScore'))} | {_num(row.get('LiquidityScore'))} | {row.get('industry', '')} |"
        )
    lines.extend(["", "主要风险说明：", *_bullet_lines(portfolio.get("risk_notes", []))])
    return lines


def _industry_lines(summary: dict[str, Any]) -> list[str]:
    lines = []
    if summary.get("unclassified_fallback_warning"):
        lines.append("- 部分股票原始行业字段为 Unclassified，系统已使用 fallback industry buckets 做集中度校验；后续仍需提升行业分类质量。")
    for key in ["long", "mid", "short"]:
        record = summary.get(key, {})
        lines.append(f"- {key} top industries: {_industry_join(record.get('top_industries', []))}")
        lines.append(f"- {key} industry concentration warning: {str(record.get('industry_concentration_warning', False)).lower()}")
    return lines


def _risk_liquidity_lines(summary: dict[str, Any]) -> list[str]:
    lines = []
    for key in ["long", "mid", "short"]:
        record = summary.get(key, {})
        lines.append(f"- {key} avg RiskScore / LiquidityScore: {_num(record.get('avg_risk_score'))} / {_num(record.get('avg_liquidity_score'))}")
        lines.append(f"- {key} low liquidity notes: {_join(record.get('low_liquidity_notes'))}")
        lines.append(f"- {key} high risk notes: {_join(record.get('high_risk_notes'))}")
        if key == "short":
            lines.append(f"- short overheat notes: {_join(record.get('overheat_risk_notes'))}")
    return lines


def _audit_status_lines(status: dict[str, Any]) -> list[str]:
    lines = []
    for key in ["feature", "score", "candidate", "portfolio"]:
        record = status.get(key, {})
        lines.append(
            f"- {key}: overall_passed={str(record.get('overall_passed')).lower()}, blocking={record.get('blocking_reasons', [])}, warnings={len(record.get('warnings', []))}"
        )
    boundary = status.get("boundary", {})
    lines.extend(
        [
            f"- briefing_only: {str(boundary.get('briefing_only')).lower()}",
            f"- scores_regenerated: {str(boundary.get('scores_regenerated')).lower()}",
            f"- candidates_regenerated: {str(boundary.get('candidates_regenerated')).lower()}",
            f"- virtual_portfolios_regenerated: {str(boundary.get('virtual_portfolios_regenerated')).lower()}",
            f"- broker_connected: {str(boundary.get('broker_connected')).lower()}",
            f"- real_orders_placed: {str(boundary.get('real_orders_placed')).lower()}",
        ]
    )
    return lines


def _industry_join(items: list[dict[str, Any]]) -> str:
    return "; ".join(f"{item.get('industry', '')} {_pct(item.get('weight'))}" for item in items)


def _join(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _num(value: Any, digits: int = 6) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return ""


def _pct(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return ""
