"""Markdown reports for owner recovery evidence."""

from __future__ import annotations

from trading_core.equity_owner_recovery_evidence.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_RECOVERY_EVIDENCE_COLLECTION.md": render_collection(payloads),
        "A_SHARE_READINESS_IMPROVEMENT_EVIDENCE.md": render_improvement(payloads),
        "A_SHARE_RECOVERY_EVIDENCE_GAPS.md": render_gaps(payloads),
        "A_SHARE_NEXT_REEVALUATION_PREP.md": render_prep(payloads),
        "A_SHARE_RECOVERY_EVIDENCE_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_collection(payloads: dict) -> str:
    summary = payloads["recovery_evidence_summary"]
    task = payloads["recovery_task_evidence_collection"]
    return "\n".join(
        [
            "# A Share Recovery Evidence Collection",
            "",
            "## 1. Recovery Evidence 总览",
            f"- evidence_record_count: {summary['evidence_record_count']}",
            f"- overall_evidence_quality: {summary['overall_evidence_quality']}",
            f"- evidence_ready_for_next_reevaluation_prep: {summary['evidence_ready_for_next_reevaluation_prep']}",
            "## 2. 当前 Gate 状态",
            f"- source_gate_decision: {summary['source_gate_decision']}",
            f"- source_readiness_score: {summary['source_readiness_score']}",
            f"- minimum_owner_readiness_score: {summary['minimum_owner_readiness_score']}",
            "## 3. Recovery Task Evidence",
            f"- task_count: {task['task_count']}",
            f"- completion_claim_allowed_count: {task['completion_claim_allowed_count']}",
            "## 4. Developer Follow-up Evidence",
            f"- follow_up_count: {payloads['developer_follow_up_evidence_package']['follow_up_count']}",
            "## 5. Owner Follow-up Evidence",
            f"- owner_evidence_available: {payloads['owner_follow_up_evidence_package']['owner_evidence_available']}",
            "## 6. Quality Issue Evidence",
            f"- quality_issue_count: {payloads['quality_issue_evidence_package']['quality_issue_count']}",
            "## 7. Evidence Quality",
            f"- missing_evidence_count: {summary['missing_evidence_count']}",
            "## 8. Evidence Gaps",
            f"- evidence_gap_count: {summary['evidence_gap_count']}",
            "## 9. 下一阶段 Reevaluation Prep",
            f"- ready_for_evidence_backed_gate_prep: {summary['evidence_ready_for_next_reevaluation_prep']}",
            "## 10. Boundary 状态",
            "- no owner-readiness gate reevaluation occurred.",
            "## 11. 免责声明",
            "- 本报告仅为 recovery evidence 与 readiness improvement evidence 汇总，不是投资建议，也不是订单指令。",
            "",
        ]
    )


def render_improvement(payloads: dict) -> str:
    score = payloads["evidence_backed_score_impact_estimate"]
    return "\n".join(
        [
            "# A Share Readiness Improvement Evidence",
            "",
            "- 本阶段不生成新的 owner-readiness gate score。",
            "- 本阶段不生成新的 gate decision。",
            "- 任何 score impact 都只是 evidence-backed estimate，不是正式 gate score。",
            f"- source_readiness_score: {score['source_readiness_score']}",
            f"- evidence_supported_score_delta_estimate: {score['evidence_supported_score_delta_estimate']}",
            f"- projected_score_if_evidence_accepted: {score['projected_score_if_evidence_accepted']}",
            f"- actual_audited_score_changed: {score['actual_audited_score_changed']}",
            "",
        ]
    )


def render_gaps(payloads: dict) -> str:
    gaps = payloads["evidence_gap_register"]
    lines = ["# A Share Recovery Evidence Gaps", "", f"- gap_count: {gaps['gap_count']}"]
    for item in gaps["items"]:
        lines.extend(["", f"## {item['gap_id']}", f"- missing_evidence: {item['missing_evidence']}", f"- blocks_next_reevaluation_prep: {item['blocks_next_reevaluation_prep']}"])
    lines.append("")
    return "\n".join(lines)


def render_prep(payloads: dict) -> str:
    prep = payloads["next_reevaluation_prep_checklist"]
    return "\n".join(
        [
            "# A Share Next Reevaluation Prep",
            "",
            f"- recovery_evidence_collected: {prep['recovery_evidence_collected']}",
            f"- audit_verified_evidence_available: {prep['audit_verified_evidence_available']}",
            f"- readiness_score_gap_addressed: {prep['readiness_score_gap_addressed']}",
            f"- ready_for_evidence_backed_gate_prep: {prep['ready_for_evidence_backed_gate_prep']}",
            "- No gate reevaluation was executed in v0.8.18.",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["recovery_evidence_source_trace"]
    return "\n".join(
        [
            "# A Share Recovery Evidence Source Trace",
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
            "# A Share Owner Recovery Evidence Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- source_gate_decision: {audit['input_checks']['source_gate_decision']}",
            f"- no_fabricated_evidence: {audit['evidence_checks']['no_fabricated_evidence']}",
            f"- evidence_ready_for_next_reevaluation_prep: {audit['evidence_checks']['evidence_ready_for_next_reevaluation_prep']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )

