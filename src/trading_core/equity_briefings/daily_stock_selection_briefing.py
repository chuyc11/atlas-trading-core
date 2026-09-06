"""Build v0.7.7 A-share daily stock selection briefing artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import cast, Any

from trading_core.equity_briefings.briefing_config import BRIEFING_BOUNDARY, BRIEFING_FILES, BRIEFING_REPORTS, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.equity_briefings.briefing_inputs import BriefingInputs, briefing_data_dir, briefing_output_dir, load_briefing_inputs
from trading_core.equity_briefings.briefing_manifest import build_briefing_manifest
from trading_core.equity_briefings.briefing_renderer import render_daily_stock_selection_briefing
from trading_core.equity_briefings.source_trace import build_briefing_source_trace, write_briefing_source_trace
from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_daily_stock_selection_briefing(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_artifact_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    inputs = load_briefing_inputs(paths=paths, as_of_date=as_of_date, allow_latest_artifact_date=allow_latest_artifact_date)
    generated_at = utc_now()
    data_dir = briefing_data_dir(paths, inputs.as_of_date)
    output_dir = briefing_output_dir(paths, inputs.as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(data_dir, output_dir)
    source_trace = build_briefing_source_trace(paths, inputs, generated_at)
    source_trace_paths = write_briefing_source_trace(paths, inputs.as_of_date, source_trace)
    artifacts["briefing_source_trace"] = Path(source_trace_paths["briefing_source_trace"])
    artifacts["briefing_source_trace_report"] = Path(source_trace_paths["briefing_source_trace_report"])
    payload = _briefing_payload(paths, inputs, generated_at, source_trace, artifacts)
    payload["manifest_ref"] = relative(artifacts["briefing_manifest"], paths.project_root)
    payload["reports"] = {
        "daily_stock_selection_briefing_report": relative(artifacts["daily_stock_selection_briefing_report"], paths.project_root),
        "briefing_source_trace_report": relative(artifacts["briefing_source_trace_report"], paths.project_root),
    }
    report = render_daily_stock_selection_briefing(payload)
    write_json(artifacts["daily_stock_selection_briefing"], payload)
    artifacts["daily_stock_selection_briefing_report"].write_text(report, encoding="utf-8")
    write_json(artifacts["briefing_boundary_check"], _boundary_check(inputs, generated_at))
    manifest = build_briefing_manifest(paths=paths, inputs=inputs, artifacts=artifacts, generated_at=generated_at)
    write_json(artifacts["briefing_manifest"], manifest)
    return json_safe(payload)


def _artifact_paths(data_dir: Path, output_dir: Path) -> dict[str, Path]:
    return {
        "daily_stock_selection_briefing": data_dir / BRIEFING_FILES["daily_stock_selection_briefing"],
        "briefing_manifest": data_dir / BRIEFING_FILES["briefing_manifest"],
        "briefing_source_trace": data_dir / BRIEFING_FILES["briefing_source_trace"],
        "briefing_boundary_check": data_dir / BRIEFING_FILES["briefing_boundary_check"],
        "daily_stock_selection_briefing_report": output_dir / BRIEFING_REPORTS["daily_stock_selection_briefing_report"],
        "briefing_source_trace_report": output_dir / BRIEFING_REPORTS["briefing_source_trace_report"],
    }


def _briefing_payload(
    paths: ProjectPaths,
    inputs: BriefingInputs,
    generated_at: str,
    source_trace: dict[str, Any],
    artifacts: dict[str, Path],
) -> dict[str, Any]:
    long_top = _candidate_top(inputs.long_candidates, "Long")
    mid_top = _candidate_top(inputs.mid_candidates, "Mid")
    short_top = _candidate_top(inputs.short_candidates, "Short")
    risk_downgraded_symbols = {str(row.get("symbol")) for row in inputs.risk_downgraded_candidates if row.get("symbol")}
    multi_top = _multi_horizon_top(inputs.multi_horizon_candidates, risk_downgraded_symbols)
    risk_summary = _risk_downgraded_summary(inputs.risk_downgraded_candidates)
    portfolios = {
        "long": _portfolio_summary(inputs, "long", inputs.long_virtual_portfolio, "LongScore"),
        "mid": _portfolio_summary(inputs, "mid", inputs.mid_virtual_portfolio, "MidScore"),
        "short": _portfolio_summary(inputs, "short", inputs.short_virtual_portfolio, "ShortScore"),
    }
    industry_summary = _industry_summary(inputs)
    risk_liquidity = _risk_liquidity_summary(inputs)
    audit_status = _audit_status(inputs)
    input_versions = _input_versions(inputs)
    quality_gate = _quality_gate(inputs, portfolios, industry_summary, audit_status, generated_at)
    executive_summary = _executive_summary(input_versions, long_top, mid_top, short_top, multi_top, risk_summary, portfolios, industry_summary, quality_gate)
    payload = {
        "briefing_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "input_versions": input_versions,
        "executive_summary": executive_summary,
        "long_candidates_top10": long_top,
        "mid_candidates_top10": mid_top,
        "short_candidates_top10": short_top,
        "multi_horizon_candidates_top10": multi_top,
        "risk_downgraded_summary": risk_summary,
        "virtual_portfolios": portfolios,
        "industry_exposure_summary": industry_summary,
        "risk_liquidity_summary": risk_liquidity,
        "audit_status": audit_status,
        "quality_gate": quality_gate,
        "score_definitions": {
            "RiskScore": "风险质量分（0-100，越高代表模型内风险质量越好；不是损失概率）",
            "LiquidityScore": "流动性质量分（0-100，越高代表模型内流动性越好）",
            "horizon_scores": "长期/中期/短期分均为横截面相对研究分，不是目标价、收益率或上涨概率",
        },
        "do_not_misread": _do_not_misread(),
        "next_tracking_actions": _next_tracking_actions(),
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "boundary": dict(BRIEFING_BOUNDARY),
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    cast(dict[str, Any], payload["audit_status"])["boundary"] = dict(BRIEFING_BOUNDARY)
    return payload


def _candidate_top(rows: list[dict[str, Any]], horizon: str) -> list[dict[str, Any]]:
    score_key = f"{horizon}Score"
    rank_key = f"{horizon}Rank"
    ranked = sorted(rows, key=lambda row: (_sort_value(row.get(rank_key) or row.get("candidate_rank")), str(row.get("symbol") or "")))
    result = []
    for index, row in enumerate(ranked[:10], start=1):
        result.append(
            {
                "rank": index,
                "symbol": row.get("symbol"),
                "name": row.get("name"),
                "industry_level_1": row.get("industry_level_1"),
                score_key: _value(row.get(score_key)),
                rank_key: _value(row.get(rank_key) or row.get("candidate_rank")),
                "RiskScore": _value(row.get("RiskScore")),
                "LiquidityScore": _value(row.get("LiquidityScore")),
                "IndustryScore": _value(row.get("IndustryScore")),
                "FundamentalScore": _value(row.get("FundamentalScore")),
                "CompositeOpportunityScore": _value(row.get("CompositeOpportunityScore")),
                "primary_inclusion_reasons": _listish(row.get("primary_inclusion_reasons")),
                "main_risk_reasons": _listish(row.get("main_risk_reasons")),
            }
        )
    return result


def _multi_horizon_top(rows: list[dict[str, Any]], risk_downgraded_symbols: set[str]) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: (_sort_value(row.get("CompositeRank")), str(row.get("symbol") or "")))
    return [
        {
            "symbol": row.get("symbol"),
            "name": row.get("name"),
            "horizon_overlap_type": row.get("horizon_overlap_type"),
            "best_horizon": row.get("best_horizon"),
            "eligibility_status": "risk_downgraded" if str(row.get("symbol")) in risk_downgraded_symbols else "research_eligible",
            "LongScore": _value(row.get("LongScore")),
            "MidScore": _value(row.get("MidScore")),
            "ShortScore": _value(row.get("ShortScore")),
            "CompositeOpportunityScore": _value(row.get("CompositeOpportunityScore")),
            "primary_strengths": _listish(row.get("primary_strengths")),
            "risk_notes": _listish(row.get("risk_notes")),
        }
        for row in ranked[:10]
    ]


def _risk_downgraded_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(rows, key=lambda row: (-float(row.get("trigger_score") or 0.0), str(row.get("symbol") or "")))
    top10 = [
        {
            "symbol": row.get("symbol"),
            "name": row.get("name"),
            "trigger_horizon": row.get("trigger_horizon"),
            "trigger_score": _value(row.get("trigger_score")),
            "downgrade_reason": row.get("downgrade_reason"),
            "RiskScore": _value(row.get("RiskScore")),
            "LiquidityScore": _value(row.get("LiquidityScore")),
            "confidence": _value(row.get("confidence")),
        }
        for row in ranked[:10]
    ]
    reason_counts: Counter[str] = Counter()
    horizon_counts: Counter[str] = Counter()
    for row in rows:
        reasons = _listish(row.get("downgrade_reason"))
        for reason in reasons or ["unspecified"]:
            for item in re.split(r"[;,]", str(reason)):
                reason_counts[item.strip()] += 1
        horizon_counts[str(row.get("trigger_horizon") or "unspecified")] += 1
    return {"count": len(rows), "reason_counts": dict(reason_counts), "horizon_counts": dict(horizon_counts), "top10": top10}


def _portfolio_summary(inputs: BriefingInputs, key: str, rows: list[dict[str, Any]], score_key: str) -> dict[str, Any]:
    portfolio_id = f"{key}_virtual_portfolio"
    weight_summary = inputs.portfolio_weight_summary.get(portfolio_id, {})
    exposure = inputs.portfolio_industry_exposure.get(portfolio_id, {})
    top_holdings = []
    for row in sorted(rows, key=lambda item: (-float(item.get("target_weight") or 0.0), int(item.get("weight_rank") or 9999)))[:10]:
        top_holdings.append(
            {
                "weight_rank": row.get("weight_rank"),
                "symbol": row.get("symbol"),
                "name": row.get("name"),
                "target_weight": _value(row.get("target_weight")),
                "horizon_score": _value(row.get(score_key)),
                "RiskScore": _value(row.get("RiskScore")),
                "LiquidityScore": _value(row.get("LiquidityScore")),
                "industry": row.get("industry") or row.get("industry_level_1"),
                "risk_notes": _listish(row.get("risk_notes")),
            }
        )
    weight_sum = float(weight_summary.get("weight_sum") or _sum(rows, "target_weight") or 0.0)
    cash_weight = max(0.0, 1.0 - weight_sum)
    return {
        "portfolio_id": portfolio_id,
        "holding_count": int(weight_summary.get("holdings", len(rows)) or 0),
        "weight_sum": _value(weight_sum),
        "cash_weight": _value(cash_weight),
        "allocation_status": "fully_allocated" if abs(weight_sum - 1.0) <= 0.001 else ("underallocated" if weight_sum < 1.0 else "overallocated"),
        "max_single_weight": _value(weight_summary.get("max_single_weight") or _max(rows, "target_weight")),
        "max_industry_weight": _value(weight_summary.get("max_industry_weight") or 0.0),
        "top10_holdings": top_holdings,
        "top_industries": exposure.get("top_industry_exposures", [])[:5],
        "risk_notes": _portfolio_risk_notes(inputs, key),
    }


def _industry_summary(inputs: BriefingInputs) -> dict[str, Any]:
    result: dict[str, Any] = {}
    unclassified = False
    for key in ["long", "mid", "short"]:
        portfolio_id = f"{key}_virtual_portfolio"
        exposure = inputs.portfolio_industry_exposure.get(portfolio_id, {})
        raw = exposure.get("raw_industry_weight_by_level_1", {})
        top = exposure.get("top_industry_exposures", [])[:5]
        violations = exposure.get("industry_cap_violations", [])
        unclassified = unclassified or float(raw.get("Unclassified", 0.0) or 0.0) > 0.0
        unclassified_weight = float(raw.get("Unclassified", 0.0) or 0.0)
        result[key] = {
            "top_industries": top,
            "raw_industry_weight_by_level_1": raw,
            "unclassified_weight": _value(unclassified_weight),
            "exposure_basis": "proxy_listing_bucket" if unclassified_weight > 0 else "industry_level_1",
            "true_industry_concentration_verifiable": unclassified_weight <= 0,
            "industry_concentration_warning": bool(violations),
            "industry_cap_violations": violations,
        }
    result["unclassified_fallback_warning"] = unclassified
    return result


def _risk_liquidity_summary(inputs: BriefingInputs) -> dict[str, Any]:
    result = {}
    rows_by_key = {
        "long": inputs.long_virtual_portfolio,
        "mid": inputs.mid_virtual_portfolio,
        "short": inputs.short_virtual_portfolio,
    }
    for key, rows in rows_by_key.items():
        portfolio_id = f"{key}_virtual_portfolio"
        summary = inputs.portfolio_risk_liquidity_summary.get(portfolio_id, {})
        low_liquidity = [row for row in rows if float(row.get("LiquidityScore") or 0.0) < 55.0]
        low_risk_quality = [row for row in rows if float(row.get("RiskScore") or 0.0) < 50.0]
        record = {
            "avg_risk_score": _value(_weighted_average(rows, "RiskScore")),
            "avg_liquidity_score": _value(_weighted_average(rows, "LiquidityScore")),
            "average_basis": "target_weight_normalized",
            "min_risk_score": _value(summary.get("min_risk_score")),
            "min_liquidity_score": _value(summary.get("min_liquidity_score")),
            "low_liquidity_notes": _risk_note_symbols(low_liquidity, "LiquidityScore"),
            "low_risk_quality_notes": _risk_note_symbols(low_risk_quality, "RiskScore"),
            "overheat_risk_notes": [],
        }
        if key == "short":
            flagged = [row for row in rows if "overheat_risk" in _listish(row.get("overheat_risk_notes"))]
            record["overheat_risk_notes"] = [f"{row.get('symbol')} {row.get('name')}" for row in flagged] or ["未触发 overheat_risk 标记。"]
        result[key] = record
    return result


def _audit_status(inputs: BriefingInputs) -> dict[str, Any]:
    records = {
        "feature": _audit_record(inputs.feature_audit, inputs.as_of_date),
        "score": _audit_record(inputs.score_audit, inputs.as_of_date),
        "candidate": _audit_record(inputs.candidate_audit, inputs.as_of_date),
        "portfolio": _audit_record(inputs.portfolio_audit, inputs.as_of_date),
    }
    return {
        **records,
        "all_audits_current": all(record.get("as_of_date_matches") is True for record in records.values()),
        "warnings": _combined_warnings(inputs),
        "blocking_reasons": _combined_blocking(inputs),
    }


def _audit_record(payload: dict[str, Any], briefing_as_of_date: str) -> dict[str, Any]:
    if not payload:
        return {"audit_id": "", "target_version": "", "as_of_date": None, "as_of_date_matches": False, "overall_passed": None, "blocking_reasons": ["audit artifact missing"], "warnings": ["audit artifact missing"]}
    audit_date = payload.get("as_of_date")
    return {
        "audit_id": payload.get("audit_id"),
        "target_version": payload.get("target_version"),
        "as_of_date": payload.get("as_of_date"),
        "as_of_date_matches": audit_date == briefing_as_of_date,
        "overall_passed": payload.get("overall_passed"),
        "blocking_reasons": payload.get("blocking_reasons", []),
        "warnings": payload.get("warnings", []),
        "recommended_next_version": payload.get("recommended_next_version"),
    }


def _input_versions(inputs: BriefingInputs) -> dict[str, Any]:
    counts = inputs.candidate_manifest.get("candidate_counts", {})
    return {
        "feature_version": inputs.feature_manifest.get("target_version"),
        "score_version": inputs.score_manifest.get("target_version"),
        "candidate_version": inputs.candidate_manifest.get("target_version"),
        "portfolio_version": inputs.portfolio_manifest.get("target_version"),
        "strict_tradable_count": inputs.candidate_manifest.get("strict_tradable_count") or inputs.candidate_summary.get("strict_tradable_count"),
        "scored_symbols": inputs.candidate_manifest.get("scored_symbols") or inputs.candidate_summary.get("scored_symbols"),
        "long_candidates": counts.get("long_candidates", len(inputs.long_candidates)),
        "mid_candidates": counts.get("mid_candidates", len(inputs.mid_candidates)),
        "short_candidates": counts.get("short_candidates", len(inputs.short_candidates)),
        "multi_horizon_candidates": counts.get("multi_horizon_candidates", len(inputs.multi_horizon_candidates)),
        "risk_downgraded_candidates": counts.get("risk_downgraded_candidates", len(inputs.risk_downgraded_candidates)),
    }


def _executive_summary(
    versions: dict[str, Any],
    long_top: list[dict[str, Any]],
    mid_top: list[dict[str, Any]],
    short_top: list[dict[str, Any]],
    multi_top: list[dict[str, Any]],
    risk_summary: dict[str, Any],
    portfolios: dict[str, Any],
    industry_summary: dict[str, Any],
    quality_gate: dict[str, Any],
) -> list[str]:
    long_industry = _top_industry(industry_summary.get("long", {}))
    mid_industry = _top_industry(industry_summary.get("mid", {}))
    short_industry = _top_industry(industry_summary.get("short", {}))
    downgrade_rate = float(risk_summary.get("count", 0) or 0) / max(float(versions.get("scored_symbols", 0) or 0), 1.0)
    return [
        f"流通结论：{quality_gate['circulation_status']}；{quality_gate['decision_summary']}",
        f"严格可交易股票池覆盖 {versions.get('strict_tradable_count', 0)} 只，评分覆盖 {versions.get('scored_symbols', 0)} 只。",
        f"长期/中期/短期研究候选数量分别为 {versions.get('long_candidates', 0)} / {versions.get('mid_candidates', 0)} / {versions.get('short_candidates', 0)}，本简报各展示前 {len(long_top)} / {len(mid_top)} / {len(short_top)} 只。",
        f"多周期共振候选 {versions.get('multi_horizon_candidates', 0)} 只，本简报展示前 {len(multi_top)} 只；这只是多周期相对评分靠前。",
        f"风险降级股票 {risk_summary.get('count', 0)} 只（占评分覆盖 {downgrade_rate:.1%}），说明部分高分股票被风险质量或流动性门槛排除。",
        f"长期/中期/短期虚拟组合持仓数量为 {portfolios['long'].get('holding_count')} / {portfolios['mid'].get('holding_count')} / {portfolios['short'].get('holding_count')}。",
        f"代码板块代理桶集中方向：长期 {long_industry}，中期 {mid_industry}，短期 {short_industry}；该口径不能替代真实行业暴露。",
        "本阶段只做每日中文信息简报，不重新生成评分、候选股或虚拟组合。",
    ]


def _quality_gate(
    inputs: BriefingInputs,
    portfolios: dict[str, Any],
    industry_summary: dict[str, Any],
    audit_status: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    try:
        data_age_days = (date.fromisoformat(generated_at[:10]) - date.fromisoformat(inputs.as_of_date)).days
    except ValueError:
        data_age_days = None
    if data_age_days is None:
        warnings.append("无法计算数据时效")
    elif data_age_days > 3:
        blockers.append(f"数据已陈旧：交易日距生成日 {data_age_days} 个日历日")
    manifest_dates = {
        "feature": inputs.feature_manifest.get("as_of_date"),
        "score": inputs.score_manifest.get("as_of_date"),
        "candidate": inputs.candidate_manifest.get("as_of_date"),
        "portfolio": inputs.portfolio_manifest.get("as_of_date"),
    }
    mismatched_manifests = [f"{key}={value or 'missing'}" for key, value in manifest_dates.items() if value != inputs.as_of_date]
    if mismatched_manifests:
        blockers.append(f"输入清单日期不一致（{', '.join(mismatched_manifests)}）")
    if not audit_status.get("all_audits_current"):
        names = {"feature": "特征", "score": "评分", "candidate": "候选", "portfolio": "组合"}
        stale = [f"{names.get(key, key)}={record.get('as_of_date') or '缺失'}" for key, record in audit_status.items() if isinstance(record, dict) and "as_of_date_matches" in record and not record.get("as_of_date_matches")]
        blockers.append(f"上游审计日期与简报 {inputs.as_of_date} 不一致（{', '.join(stale)}）")
    failed = [key for key in ["feature", "score", "candidate", "portfolio"] if audit_status.get(key, {}).get("overall_passed") is not True]
    if failed:
        blockers.append(f"上游审计未通过或缺失：{', '.join(failed)}")
    underallocated = [f"{key}={float(record.get('weight_sum') or 0.0):.2%}" for key, record in portfolios.items() if record.get("allocation_status") != "fully_allocated"]
    if underallocated:
        blockers.append(f"虚拟组合未按 100% 目标完成配置（{', '.join(underallocated)}）")
    unverifiable = [key for key in ["long", "mid", "short"] if not industry_summary.get(key, {}).get("true_industry_concentration_verifiable")]
    if unverifiable:
        horizon_names = {"long": "长期", "mid": "中期", "short": "短期"}
        blockers.append(f"真实行业集中度不可验证：{', '.join(horizon_names[key] for key in unverifiable)}组合行业字段为 Unclassified")
    if audit_status.get("warnings"):
        warnings.extend(str(item) for item in audit_status["warnings"])
    status = "不可对外流通" if blockers else ("仅限高级复核" if warnings else "可供内部研究复核")
    decision_summary = "；".join(blockers[:3]) if blockers else ("仍需复核上游警告。" if warnings else "未发现阻断项。")
    return {"circulation_status": status, "decision_summary": decision_summary, "data_age_days": data_age_days, "input_manifest_dates_match": not mismatched_manifests, "blocking_issues": blockers, "warnings": sorted(set(warnings))}


def _portfolio_risk_notes(inputs: BriefingInputs, key: str) -> list[str]:
    summary = inputs.portfolio_risk_liquidity_summary.get(f"{key}_virtual_portfolio", {})
    rows = getattr(inputs, f"{key}_virtual_portfolio")
    notes = [
        f"目标权重归一后的平均风险质量分={_weighted_average(rows, 'RiskScore'):.2f}，平均流动性质量分={_weighted_average(rows, 'LiquidityScore'):.2f}",
        f"最低风险质量分={float(summary.get('min_risk_score') or 0.0):.2f}，最低流动性质量分={float(summary.get('min_liquidity_score') or 0.0):.2f}",
    ]
    if key == "short":
        notes.append("短期组合需要重点观察过热风险、短期波动和流动性变化。")
    return notes


def _risk_note_symbols(rows: list[dict[str, Any]], field: str) -> list[str]:
    if not rows:
        return ["未触发显著提示。"]
    ranked = sorted(rows, key=lambda row: float(row.get(field) or 0.0))[:5]
    return [f"{row.get('symbol')} {row.get('name')} {field}={_value(row.get(field))}" for row in ranked]


def _combined_warnings(inputs: BriefingInputs) -> list[str]:
    warnings: list[str] = []
    for payload in [inputs.feature_audit, inputs.score_audit, inputs.candidate_audit, inputs.portfolio_audit]:
        warnings.extend(str(item) for item in payload.get("warnings", []) if item)
    return warnings


def _combined_blocking(inputs: BriefingInputs) -> list[str]:
    blocking: list[str] = []
    for payload in [inputs.feature_audit, inputs.score_audit, inputs.candidate_audit, inputs.portfolio_audit]:
        blocking.extend(str(item) for item in payload.get("blocking_reasons", []) if item)
    return blocking


def _do_not_misread() -> list[str]:
    return [
        "候选股不是买入建议。",
        "虚拟组合不是实盘组合。",
        "目标权重不是下单指令。",
        "评分是相对评分，不代表确定盈利。",
        "当前还没有真实交易验证。",
        "当前没有 broker 连接。",
        "当前没有真实订单。",
    ]


def _next_tracking_actions() -> list[str]:
    return [
        "下一步应进入虚拟组合跟踪和纸面账本。",
        "跟踪每日涨跌、组合收益、回撤、行业暴露变化。",
        "比较长期/中期/短期组合与基准指数。",
        "持续记录风险降级股票是否改善风险质量或流动性状态。",
    ]


def _boundary_check(inputs: BriefingInputs, generated_at: str) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "generated_at": generated_at,
        "briefing_only": True,
        "source_artifacts_read_only": True,
        "boundary": dict(BRIEFING_BOUNDARY),
    }


def _top_industry(summary: dict[str, Any]) -> str:
    top = summary.get("top_industries", [])
    if not top:
        return "无可用行业摘要"
    first = top[0]
    return f"{first.get('industry', '')} ({float(first.get('weight') or 0.0):.2%})"


def _listish(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return [text]
        return [text]
    return [str(value)]


def _value(value: Any) -> Any:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return value


def _sum(rows: list[dict[str, Any]], field: str) -> float:
    return round(sum(float(row.get(field) or 0.0) for row in rows), 6)


def _max(rows: list[dict[str, Any]], field: str) -> float:
    return round(max([float(row.get(field) or 0.0) for row in rows] or [0.0]), 6)


def _weighted_average(rows: list[dict[str, Any]], field: str) -> float | None:
    pairs = [(float(row.get("target_weight") or 0.0), float(row.get(field) or 0.0)) for row in rows if row.get(field) is not None]
    denominator = sum(weight for weight, _ in pairs)
    if denominator <= 0:
        return None
    return sum(weight * value for weight, value in pairs) / denominator


def _sort_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 999999.0
