from pathlib import Path

from trading_core.equity_owner_remediation.remediation_manifest import build_remediation_manifest, build_remediation_summary


def test_remediation_manifest_generated():
    manifest = build_remediation_manifest(
        as_of_date="2026-06-26",
        generated_at="now",
        mode="build_remediation_runbook",
        issue_catalog={"issue_count": 0},
        priority_summary={"blocking_issue_count": 0, "warning_issue_count": 0, "known_non_blocking_issue_count": 0},
        checklist={"safe_action_count": 1, "automatic_action_count": 0},
        output_artifacts={"x": Path("x")},
        source_artifacts={"s": Path("s")},
        boundary={"overall_passed": True},
    )
    summary = build_remediation_summary(as_of_date="2026-06-26", mode="build_remediation_runbook", manifest=manifest, priority_summary={"status": "no_action_required"})
    assert manifest["manifest_id"] == "A-SHARE-OWNER-REMEDIATION-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-OWNER-REMEDIATION-SUMMARY"
