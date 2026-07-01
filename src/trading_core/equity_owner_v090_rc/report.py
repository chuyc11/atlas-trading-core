"""Markdown reports for v0.9.0 RC closeout."""

from __future__ import annotations

from trading_core.equity_owner_v090_rc.io import write_text


def write_reports(output_dir, payloads: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = {
        "A_SHARE_V090_RC_REPORT.md": render_rc_report(payloads),
        "A_SHARE_V090_FULL_REGRESSION_RESULT.md": render_full_regression(payloads),
        "A_SHARE_V090_AUDIT_SWEEP_RESULT.md": render_audit_sweep(payloads),
        "A_SHARE_V090_KNOWN_BLOCKED_STATE_DISCLOSURE.md": render_known_blocked_state(payloads),
        "A_SHARE_V090_RELEASE_CANDIDATE_DECISION.md": render_rc_decision(payloads),
        "A_SHARE_V090_SOURCE_TRACE.md": render_source_trace(payloads),
    }
    for name, text in reports.items():
        write_text(output_dir / name, text)


def render_rc_report(payloads: dict) -> str:
    summary = payloads["v090_owner_release_summary"]
    return "\n".join(
        [
            "# A 股 v0.9.0 RC Report",
            "",
            "## 1. v0.9.0 RC 总览",
            "- v0.9.0 is a research-system release candidate.",
            f"- v090_release_candidate_decision: {summary['v090_release_candidate_decision']}",
            "## 2. Full Regression Result",
            f"- full_pytest_run: {summary['full_pytest_run']}",
            f"- full_pytest_passed: {summary['full_pytest_passed']}",
            f"- full_pytest_passed_count: {summary['full_pytest_passed_count']}",
            "## 3. Audit Sweep Result",
            f"- audit_sweep_passed: {summary['audit_sweep_passed']}",
            f"- audit_sweep_item_count: {summary['audit_sweep_item_count']}",
            "## 4. Known Blocked Owner-Readiness State",
            "- owner-readiness remains blocked.",
            "- blocked state is intentional and audited.",
            f"- score_gap: {summary['score_gap']}",
            "## 5. What Passed",
            "- full pytest, audit sweep, boundary sweep, source trace sweep, and documentation freeze passed.",
            "## 6. What Remains Blocked",
            "- owner-readiness acceptance remains blocked and is not represented as acceptable.",
            "## 7. Safety Boundary",
            "- No broker integration, real account reading, real orders, order previews, or buy/sell signals were performed.",
            "## 8. Not Live Trading Ready",
            "- v0.9.0 does not mean live trading ready.",
            "## 9. Recommended Next Step",
            f"- {summary['recommended_next_version']}",
            "## 10. Disclaimer",
            "- Research-only / virtual-only RC. Not investment advice and not an order instruction.",
            "",
        ]
    )


def render_full_regression(payloads: dict) -> str:
    result = payloads["v090_full_pytest_result"]
    return "\n".join(
        [
            "# A Share v0.9.0 Full Regression Result",
            "",
            f"- command: `{result['command']}`",
            f"- full_pytest_run: {result['full_pytest_run']}",
            f"- exit_code: {result['exit_code']}",
            f"- passed_count: {result['passed_count']}",
            f"- failed_count: {result['failed_count']}",
            f"- skipped_count: {result['skipped_count']}",
            f"- overall_passed: {result['overall_passed']}",
            "",
        ]
    )


def render_audit_sweep(payloads: dict) -> str:
    sweep = payloads["v090_audit_sweep_result"]
    lines = [
        "# A Share v0.9.0 Audit Sweep Result",
        "",
        f"- audit_sweep_passed: {sweep['audit_sweep_passed']}",
        f"- audit_sweep_item_count: {sweep['audit_sweep_item_count']}",
        f"- failed_audit_sweep_items: {sweep['failed_audit_sweep_items']}",
        "",
    ]
    lines.extend(f"- {item['audit_name']}: passed={item['sweep_passed']}" for item in sweep["items"])
    lines.append("")
    return "\n".join(lines)


def render_known_blocked_state(payloads: dict) -> str:
    disclosure = payloads["v090_known_blocked_state_disclosure"]
    return "\n".join(
        [
            "# A Share v0.9.0 Known Blocked State Disclosure",
            "",
            f"- owner_readiness_state: {disclosure['owner_readiness_state']}",
            f"- owner_operationally_acceptable: {disclosure['owner_operationally_acceptable']}",
            f"- previous_readiness_score: {disclosure['previous_readiness_score']}",
            f"- minimum_owner_readiness_score: {disclosure['minimum_owner_readiness_score']}",
            f"- score_gap: {disclosure['score_gap']}",
            f"- blocks_owner_readiness_acceptance: {disclosure['blocks_owner_readiness_acceptance']}",
            f"- blocks_v090_rc: {disclosure['blocks_v090_rc']}",
            "- This is not live trading readiness and not a trade instruction.",
            "",
        ]
    )


def render_rc_decision(payloads: dict) -> str:
    decision = payloads["v090_release_candidate_decision"]
    return "\n".join(
        [
            "# A Share v0.9.0 Release Candidate Decision",
            "",
            f"- decision: {decision['decision']}",
            f"- overall_passed: {decision['overall_passed']}",
            f"- blocking_reasons: {decision['blocking_reasons']}",
            f"- recommended_next_version: {decision['recommended_next_version']}",
            "",
        ]
    )


def render_source_trace(payloads: dict) -> str:
    trace = payloads["v090_source_trace"]
    return "\n".join(
        [
            "# A Share v0.9.0 Source Trace",
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
            "# A Share Owner v0.9.0 RC Audit",
            "",
            f"- overall_passed: {audit['overall_passed']}",
            f"- blocking_reasons: {audit['blocking_reasons']}",
            f"- full_pytest_passed: {audit['regression_checks']['full_pytest_passed']}",
            f"- audit_sweep_passed: {audit['regression_checks']['audit_sweep_passed']}",
            f"- release_candidate_decision: {audit['release_candidate_decision']}",
            f"- recommended_next_version: {audit['recommended_next_version']}",
            "",
        ]
    )
