from pathlib import Path

from trading_core.equity_ops_center.ops_manifest import build_ops_manifest, build_ops_summary


def test_ops_manifest_generated():
    manifest = build_ops_manifest(
        as_of_date="2026-06-26",
        generated_at="now",
        mode="aggregate_existing_ops_artifacts",
        health_score={"overall_status": "passed", "score": 100, "required_modules_passed": True},
        issue_summary={},
        action_summary={},
        execution_record={"commands_executed": []},
        output_artifacts={"x": Path("x")},
        source_artifacts={"s": Path("s")},
        boundary={"overall_passed": True},
    )
    summary = build_ops_summary(as_of_date="2026-06-26", mode="aggregate_existing_ops_artifacts", manifest=manifest, health_score={"score": 100, "grade": "A"})
    assert manifest["manifest_id"] == "A-SHARE-DAILY-OPS-CENTER-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-DAILY-OPS-CENTER-SUMMARY"
