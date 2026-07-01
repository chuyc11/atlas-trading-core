"""Markdown reports for evidence-backed reevaluation prep."""

from __future__ import annotations

from trading_core.equity_owner_evidence_backed_reevaluation_prep.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_EVIDENCE_BACKED_GATE_REEVALUATION_PREP.md": render_prep(payloads),
        "A_SHARE_REEVALUATION_INPUT_PACKAGE.md": render_input_package(payloads),
        "A_SHARE_EVIDENCE_SUFFICIENCY_DECISION.md": render_sufficiency(payloads),
        "A_SHARE_NEXT_GATE_REEVALUATION_PLAN.md": render_plan(payloads),
        "A_SHARE_EVIDENCE_BACKED_PREP_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_prep(payloads: dict) -> str:
    summary = payloads["evidence_backed_prep_summary"]
    return "\n".join(
        [
            "# A Share Evidence Backed Gate Reevaluation Prep",
            "",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- source_readiness_score: {summary['source_readiness_score']}",
            f"- minimum_owner_readiness_score: {summary['minimum_owner_readiness_score']}",
            f"- overall_evidence_quality: {summary['overall_evidence_quality']}",
            f"- ready_for_controlled_gate_reevaluation: {summary['ready_for_controlled_gate_reevaluation']}",
            f"- eligibility_decision: {summary['eligibility_decision']}",
            "- v0.8.19 generates a reevaluation input package only; no owner-readiness gate reevaluation was executed.",
            "- No new formal gate score or formal gate decision was generated.",
            "- The source blocked gate decision and threshold are preserved.",
            "- This report is research-only, virtual-only, not investment advice, and not an order instruction.",
            "",
        ]
    )


def render_input_package(payloads: dict) -> str:
    package = payloads["reevaluation_input_package"]
    return "\n".join(
        [
            "# A Share Reevaluation Input Package",
            "",
            f"- reevaluation_input_package_generated: {package['reevaluation_input_package_generated']}",
            f"- ready_for_controlled_gate_reevaluation: {package['ready_for_controlled_gate_reevaluation']}",
            f"- eligibility_decision: {package['eligibility_decision']}",
            f"- reevaluation_executed: {package['reevaluation_executed']}",
            f"- new_gate_score_generated: {package['new_gate_score_generated']}",
            f"- new_gate_decision_generated: {package['new_gate_decision_generated']}",
            "",
        ]
    )


def render_sufficiency(payloads: dict) -> str:
    decision = payloads["evidence_sufficiency_for_reevaluation_decision"]
    return "\n".join(
        [
            "# A Share Evidence Sufficiency Decision",
            "",
            f"- evidence_sufficient_for_controlled_gate_reevaluation: {decision['evidence_sufficient_for_controlled_gate_reevaluation']}",
            f"- eligibility_decision: {decision['eligibility_decision']}",
            f"- overall_evidence_quality: {decision['overall_evidence_quality']}",
            f"- remaining_blocker_count: {decision['remaining_blocker_count']}",
            f"- blocking_reasons: {decision['blocking_reasons']}",
            "",
        ]
    )


def render_plan(payloads: dict) -> str:
    plan = payloads["next_gate_reevaluation_execution_plan"]
    return "\n".join(
        [
            "# A Share Next Gate Reevaluation Plan",
            "",
            f"- recommended_next_version: {plan['recommended_next_version']}",
            f"- next_action: {plan['next_action']}",
            f"- v0_8_19_executes_gate: {plan['v0_8_19_executes_gate']}",
            f"- ready_for_controlled_gate_reevaluation: {plan['ready_for_controlled_gate_reevaluation']}",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["evidence_backed_prep_source_trace"]
    return "\n".join(
        [
            "# A Share Evidence Backed Prep Source Trace",
            "",
            f"- source_trace_complete: {trace['source_trace_complete']}",
            f"- source_artifacts: {len(trace['source_artifacts'])}",
            f"- output_artifacts: {len(trace['output_artifacts'])}",
            "",
        ]
    )


def render_audit(audit: dict) -> str:
    return "\n".join(
        [
            "# A Share Owner Evidence Backed Reevaluation Prep Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- ready_for_controlled_gate_reevaluation: {audit['prep_checks']['ready_for_controlled_gate_reevaluation']}",
            f"- eligibility_decision: {audit['prep_checks']['eligibility_decision']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )

