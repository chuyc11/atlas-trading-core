from trading_core.equity_owner_remediation.data_guide import build_data_freshness_remediation_guide, build_schema_coverage_remediation_guide


def test_data_guides_generated():
    freshness = build_data_freshness_remediation_guide("2026-06-26")
    schema = build_schema_coverage_remediation_guide("2026-06-26")
    assert "freshness_issue" in freshness["applicable_issue_categories"]
    assert "schema_issue" in schema["applicable_issue_categories"]
    assert "coverage_issue" in schema["applicable_issue_categories"]
