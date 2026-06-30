"""Quality gates for owner readiness gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def gate_payload(gate_id: str, as_of_date: str, threshold: Any, actual_value: Any, passed: bool, blocking: list[str], warnings: list[str], source_artifacts: list[str], text: str) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "threshold": threshold,
        "actual_value": actual_value,
        "passed": passed,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "source_artifacts": source_artifacts,
        "interpretation_zh": text,
    }


def build_daily_pack_completeness_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, completeness: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    passed = completeness.get("required_json_complete") is True and completeness.get("markdown_reports_complete") is True
    blocking = []
    if completeness.get("required_json_complete") is not True:
        blocking.append("required_json_artifacts_incomplete")
    if completeness.get("markdown_reports_complete") is not True:
        blocking.append("markdown_reports_incomplete")
    return gate_payload("A-SHARE-DAILY-PACK-COMPLETENESS-GATE", as_of_date, policy["minimum_required_artifact_completeness"], {"required_json_complete": completeness.get("required_json_complete"), "markdown_reports_complete": completeness.get("markdown_reports_complete")}, passed, blocking, [], ["daily_pack_completeness_trend.json"], "必需 JSON 与 Markdown artifacts 必须完整。")


def build_warning_issue_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, warning: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    blocking_count = int(warning.get("blocking_count") or 0)
    warning_count = int(warning.get("warning_count") or 0)
    passed = blocking_count == 0 and (warning_count == 0 or policy.get("allow_known_non_blocking_warnings") is True)
    blocking = ["warning_issue_blocking_count_exceeded"] if blocking_count > 0 else []
    warnings = ["warning_issue_items_present"] if warning_count > 0 else []
    return gate_payload("A-SHARE-WARNING-ISSUE-QUALITY-GATE", as_of_date, {"blocking_count_allowed": 0}, {"warning_count": warning_count, "blocking_count": blocking_count}, passed, blocking, warnings, ["warning_issue_trend_baseline.json"], "warning 可以存在，但 blocking issue 必须为 0，并且 warning 只能作为非交易质量事项解释。")


def build_safe_action_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, safe: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    automatic = int(safe.get("automatic_action_count") or 0)
    hits = list(safe.get("forbidden_safe_action_hits") or [])
    passed = automatic == 0 and not hits and safe.get("safe_actions_not_trade_related") is True
    blocking = []
    if automatic:
        blocking.append("automatic_action_count_exceeded")
    if hits or safe.get("safe_actions_not_trade_related") is not True:
        blocking.append("forbidden_safe_action_detected")
    return gate_payload("A-SHARE-SAFE-ACTION-QUALITY-GATE", as_of_date, {"automatic_action_count_allowed": 0}, {"automatic_action_count": automatic, "forbidden_safe_action_hits": hits}, passed, blocking, [], ["safe_action_trend_baseline.json"], "safe action 只能是人工检查与非交易动作。")


def build_protected_path_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, protected: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    modified = protected.get("protected_path_modifications_detected") is True
    passed = not modified and protected.get("protected_path_trend_clean") is True
    return gate_payload("A-SHARE-PROTECTED-PATH-QUALITY-GATE", as_of_date, {"allow_protected_path_modifications": False}, {"protected_path_modifications_detected": modified}, passed, ["protected_path_modifications_detected"] if not passed else [], [], ["protected_path_trend_baseline.json"], "受保护路径不得被本阶段修改。")


def build_boundary_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, boundary: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    passed = boundary.get("boundary_clean") is True and boundary.get("boundary_trend_clean") is True
    return gate_payload("A-SHARE-BOUNDARY-QUALITY-GATE", as_of_date, {"required_boundary_clean": True}, {"boundary_clean": boundary.get("boundary_clean")}, passed, [] if passed else ["boundary_not_clean"], [], ["boundary_trend_baseline.json"], "research-only / virtual-only 边界必须干净。")


def build_source_trace_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, trace: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    passed = trace.get("source_trace_complete") is True and not trace.get("missing_required_sources")
    return gate_payload("A-SHARE-SOURCE-TRACE-QUALITY-GATE", as_of_date, {"required_source_trace_complete": True}, {"source_trace_complete": trace.get("source_trace_complete"), "missing_required_sources": trace.get("missing_required_sources", [])}, passed, [] if passed else ["source_trace_incomplete"], [], ["source_trace_quality_trend.json"], "source trace 必须完整且可追踪。")


def build_trend_sufficiency_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, sufficiency: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    insufficient = sufficiency.get("trend_analysis_available") is False
    correctly_flagged = sufficiency.get("insufficient_history_correctly_flagged") is True
    passed = (not insufficient) or (policy.get("allow_insufficient_history_if_correctly_flagged") is True and correctly_flagged)
    blocking = [] if passed else ["insufficient_history_not_correctly_flagged"]
    warnings = ["insufficient_history_correctly_flagged"] if insufficient and correctly_flagged else []
    return gate_payload("A-SHARE-TREND-SUFFICIENCY-QUALITY-GATE", as_of_date, {"allow_insufficient_history_if_correctly_flagged": policy.get("allow_insufficient_history_if_correctly_flagged")}, {"trend_analysis_available": sufficiency.get("trend_analysis_available"), "insufficient_history_correctly_flagged": correctly_flagged}, passed, blocking, warnings, ["owner_readiness_trend_sufficiency.json"], "历史不足可接受的前提是明确标记，不得伪造趋势。")


def build_markdown_report_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, completeness: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    passed = completeness.get("markdown_reports_complete") is True
    return gate_payload("A-SHARE-MARKDOWN-REPORT-QUALITY-GATE", as_of_date, policy["minimum_markdown_report_completeness"], completeness.get("markdown_reports_complete"), passed, [] if passed else ["markdown_report_incomplete"], [], ["daily_pack_completeness_trend.json"], "owner-facing Markdown reports 必须完整。")


def build_artifact_navigation_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, manifest: dict[str, Any], source_trace: dict[str, Any]) -> dict[str, Any]:
    output_count = len(manifest.get("output_artifacts", {}) or {})
    source_count = len(source_trace.get("source_artifacts", []) or [])
    passed = output_count > 0 and source_count > 0
    return gate_payload("A-SHARE-ARTIFACT-NAVIGATION-QUALITY-GATE", as_of_date, {"required_output_and_source_navigation": True}, {"output_artifact_count": output_count, "source_artifact_count": source_count}, passed, [] if passed else ["artifact_navigation_incomplete"], [], ["daily_pack_history_manifest.json", "daily_pack_history_source_trace.json"], "manifest 和 source trace 必须能帮助 owner 定位 artifacts。")


def build_owner_next_step_quality_gate(*, as_of_date: str = DEFAULT_AS_OF_DATE, next_step: dict[str, Any]) -> dict[str, Any]:
    forbidden = list(next_step.get("forbidden_next_step_hits") or [])
    passed = not forbidden and next_step.get("owner_next_steps_not_trade_related", True) is True
    return gate_payload("A-SHARE-OWNER-NEXT-STEP-QUALITY-GATE", as_of_date, {"trade_related_next_steps_allowed": False}, {"forbidden_next_step_hits": forbidden}, passed, [] if passed else ["forbidden_owner_next_step_detected"], [], ["owner_next_step_trend.json"], "owner next step 只能指向非交易的查看、审计或开发跟进。")
