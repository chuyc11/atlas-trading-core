"""Markdown renderer for v0.7.7 A-share daily stock selection briefing."""

from __future__ import annotations

import html
from typing import Any


def render_daily_stock_selection_briefing(payload: dict[str, Any]) -> str:
    quality = payload.get("quality_gate", {})
    snapshot_label = "历史研究快照" if (quality.get("data_age_days") or 0) > 3 else "研究简报"
    lines = [
        f"# A 股全市场多因子选股{snapshot_label} - {payload['as_of_date']}",
        "",
        f"> **流通状态：{quality.get('circulation_status', '未评估')}**  数据交易日：{payload['as_of_date']}｜生成时间（UTC）：{payload['generated_at']}｜数据年龄：{quality.get('data_age_days', '未知')} 个日历日",
        "",
        "## 决策摘要",
        "",
        *_bullet_lines(payload["executive_summary"]),
        "",
        "### 阻断项与限制",
        "",
        *_bullet_lines(quality.get("blocking_issues", []) or ["未发现阻断项。"]),
        "",
        "### 评分口径",
        "",
        *_score_definition_lines(payload.get("score_definitions", {})),
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
        f"- 原因分布：{_count_join(payload['risk_downgraded_summary'].get('reason_counts', {}))}",
        f"- 周期分布：{_count_join(payload['risk_downgraded_summary'].get('horizon_counts', {}))}",
        "- 这些股票分数靠前，但触发风险质量或流动性门槛，不应进入主虚拟组合。",
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
        f"- 严格可交易股票池：{versions.get('strict_tradable_count', 0)} 只；评分覆盖：{versions.get('scored_symbols', 0)} 只",
        f"- 输入版本链：特征 {versions.get('feature_version', '')} → 评分 {versions.get('score_version', '')} → 候选 {versions.get('candidate_version', '')} → 虚拟组合 {versions.get('portfolio_version', '')}",
        f"- 来源链路齐备且日期对齐：{'是' if payload.get('source_trace_complete', False) else '否'}（不代表数据正确或模型有效）",
    ]


def _candidate_table(rows: list[dict[str, Any]], score_key: str, rank_key: str, extra_key: str) -> list[str]:
    lines = [
        f"| 展示序号 | 代码 | 名称 | 行业 | {score_key} | 全市场排名 | 风险质量分↑ | 流动性质量分↑ | {extra_key} | 综合分 | 入选依据 | 已配置预警 |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('rank', '')} | {_cell(row.get('symbol'))} | {_cell(row.get('name'))} | {_industry(row.get('industry_level_1'))} | {_num(row.get(score_key), 2)} | {_num(row.get(rank_key), 0)} | {_num(row.get('RiskScore'), 2)} | {_num(row.get('LiquidityScore'), 2)} | {_num(row.get(extra_key), 2)} | {_num(row.get('CompositeOpportunityScore'), 2)} | {_labels(row.get('primary_inclusion_reasons'))} | {_labels(row.get('main_risk_reasons'))} |"
        )
    return lines


def _multi_horizon_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| 代码 | 名称 | 资格状态 | 周期覆盖 | 最强周期 | 长期分 | 中期分 | 短期分 | 综合分 | 优势 | 已配置预警 |",
        "|---|---|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {_cell(row.get('symbol'))} | {_cell(row.get('name'))} | {_labels(row.get('eligibility_status'))} | {_labels(row.get('horizon_overlap_type'))} | {_labels(row.get('best_horizon'))} | {_num(row.get('LongScore'), 2)} | {_num(row.get('MidScore'), 2)} | {_num(row.get('ShortScore'), 2)} | {_num(row.get('CompositeOpportunityScore'), 2)} | {_labels(row.get('primary_strengths'))} | {_labels(row.get('risk_notes'))} |"
        )
    return lines


def _risk_downgraded_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| 代码 | 名称 | 触发周期 | 触发分 | 降级原因 | 风险质量分↑ | 流动性质量分↑ | 置信度 |",
        "|---|---|---|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {_cell(row.get('symbol'))} | {_cell(row.get('name'))} | {_labels(row.get('trigger_horizon'))} | {_num(row.get('trigger_score'), 2)} | {_labels(row.get('downgrade_reason'))} | {_num(row.get('RiskScore'), 2)} | {_num(row.get('LiquidityScore'), 2)} | {_pct(row.get('confidence'))} |"
        )
    return lines


def _portfolio_lines(portfolio: dict[str, Any]) -> list[str]:
    lines = [
        f"- 持仓数：{portfolio.get('holding_count', 0)}；已配置权重：{_pct(portfolio.get('weight_sum'))}；现金/未配置：{_pct(portfolio.get('cash_weight'))}",
        f"- 配置状态：{_labels(portfolio.get('allocation_status'))}；最大单票权重：{_pct(portfolio.get('max_single_weight'))}",
        f"- 最大代理桶权重：{_pct(portfolio.get('max_industry_weight'))}（行业缺失时为上市板/代码前缀代理，不代表真实行业）",
        "- 虚拟组合仅用于研究跟踪，不是实盘配置建议。",
        "",
        "| 权重排名 | 代码 | 名称 | 目标权重 | 周期分 | 风险质量分↑ | 流动性质量分↑ | 行业/代理桶 |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for row in portfolio.get("top10_holdings", []):
        lines.append(
            f"| {row.get('weight_rank', '')} | {_cell(row.get('symbol'))} | {_cell(row.get('name'))} | {_pct(row.get('target_weight'))} | {_num(row.get('horizon_score'), 2)} | {_num(row.get('RiskScore'), 2)} | {_num(row.get('LiquidityScore'), 2)} | {_cell(row.get('industry'))} |"
        )
    lines.extend(["", "主要风险说明：", *_bullet_lines(portfolio.get("risk_notes", []))])
    return lines


def _industry_lines(summary: dict[str, Any]) -> list[str]:
    lines = []
    if summary.get("unclassified_fallback_warning"):
        lines.append("- **行业结论不可验证：** 原始一级行业为 Unclassified；下列仅为上市板/证券代码前缀代理桶，不能据此认定行业上限合规。")
    for key in ["long", "mid", "short"]:
        record = summary.get(key, {})
        lines.append(f"- {_labels(key)}代理桶：{_industry_join(record.get('top_industries', []))}")
        assessment = "可评估" if record.get("true_industry_concentration_verifiable") else "不可评估"
        lines.append(f"- {_labels(key)}真实行业集中度：{assessment}")
    return lines


def _risk_liquidity_lines(summary: dict[str, Any]) -> list[str]:
    lines = []
    for key in ["long", "mid", "short"]:
        record = summary.get(key, {})
        lines.append(f"- {_labels(key)}平均风险质量分 / 流动性质量分：{_num(record.get('avg_risk_score'), 2)} / {_num(record.get('avg_liquidity_score'), 2)}")
        lines.append(f"- {_labels(key)}低流动性质量预警：{_join(record.get('low_liquidity_notes'))}")
        lines.append(f"- {_labels(key)}低风险质量预警：{_join(record.get('low_risk_quality_notes'))}")
        if key == "short":
            lines.append(f"- 短期过热预警标的：{_join(record.get('overheat_risk_notes'))}")
    return lines


def _audit_status_lines(status: dict[str, Any]) -> list[str]:
    lines = []
    for key in ["feature", "score", "candidate", "portfolio"]:
        record = status.get(key, {})
        state = "通过" if record.get("overall_passed") is True and record.get("as_of_date_matches") else ("过期" if record.get("overall_passed") is True else "未通过/缺失")
        lines.append(f"- {_labels(key)}审计：{state}；审计日期={record.get('as_of_date') or '缺失'}；阻断={_join(record.get('blocking_reasons')) or '无'}；警告={_join(record.get('warnings')) or '无'}")
    boundary = status.get("boundary", {})
    lines.extend(
        [
            "- 以下为本生成步骤的声明边界，不是对券商账户或外部系统的独立核验：",
            f"  - briefing_only: {str(boundary.get('briefing_only')).lower()}",
            f"  - scores_regenerated: {str(boundary.get('scores_regenerated')).lower()}",
            f"  - candidates_regenerated: {str(boundary.get('candidates_regenerated')).lower()}",
            f"  - virtual_portfolios_regenerated: {str(boundary.get('virtual_portfolios_regenerated')).lower()}",
            f"  - broker_connected: {str(boundary.get('broker_connected')).lower()}",
            f"  - real_orders_placed: {str(boundary.get('real_orders_placed')).lower()}",
        ]
    )
    return lines


def _industry_join(items: list[dict[str, Any]]) -> str:
    return "; ".join(f"{item.get('industry', '')} {_pct(item.get('weight'))}" for item in items)


def _count_join(items: dict[str, Any]) -> str:
    return "；".join(f"{_labels(key)} {value}" for key, value in sorted(items.items(), key=lambda item: (-int(item[1]), item[0]))) or "无"


def _join(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _score_definition_lines(definitions: dict[str, Any]) -> list[str]:
    return [f"- {key}：{value}" for key, value in definitions.items()]


_LABELS = {
    "long": "长期", "mid": "中期", "short": "短期", "Long": "长期", "Mid": "中期", "Short": "短期",
    "fully_allocated": "已完整配置", "underallocated": "未完整配置", "overallocated": "超额配置",
    "Long+Mid+Short": "长+中+短", "multi_horizon_overlap": "多周期重合",
    "high_long_percentile": "长期分位靠前", "high_mid_percentile": "中期分位靠前", "high_short_percentile": "短期分位靠前",
    "strong_composite_percentile": "综合分位靠前", "strong_industry_score": "行业因子较强", "strong_liquidity_score": "流动性质量较好",
    "acceptable_risk_score": "风险质量达标", "strong_fundamental_score": "基本面因子较强", "strong_trend_component": "趋势因子较强",
    "strong_momentum_component": "动量因子较强", "low_risk_score": "风险质量分偏低", "low_liquidity_score": "流动性质量分偏低",
    "overheat_risk": "过热预警", "no_major_risk_flag_detected": "未触发已配置的量化预警（不涵盖事件/基本面/监管风险）",
    "no_severe_overheat_flag_detected": "未触发过热预警",
    "feature": "特征", "score": "评分", "candidate": "候选", "portfolio": "组合",
    "risk_downgraded": "风险降级（不得进入主组合）", "research_eligible": "研究合格",
}


def _labels(value: Any) -> str:
    if isinstance(value, list):
        return _cell("；".join(_LABELS.get(str(item), str(item)) for item in value))
    text = "" if value is None else str(value)
    return _cell(_LABELS.get(text, text))


def _cell(value: Any) -> str:
    return html.escape(str(value or ""), quote=False).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _industry(value: Any) -> str:
    text = str(value or "").strip()
    return "未分类" if text.lower() in {"", "unclassified", "unknown", "none", "nan"} else _cell(text)


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
