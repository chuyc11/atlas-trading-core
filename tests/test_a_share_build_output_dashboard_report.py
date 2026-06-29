from trading_core.equity_build_output_dashboard.build_output_report import render_compact_dashboard


def test_build_output_compact_report_length():
    text = render_compact_dashboard(as_of_date="2026-06-26", summary={"source_workflow_mode": "build_from_existing_data", "overall_status": "passed", "recommended_next_version": "v0.8.10"})
    assert len(text) <= 1200

