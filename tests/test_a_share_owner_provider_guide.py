from trading_core.equity_owner_remediation.provider_guide import build_provider_remediation_guide


def test_provider_guide_generated():
    guide = build_provider_remediation_guide("2026-06-26")
    assert "provider_issue" in guide["applicable_issue_categories"]
    assert guide["manual_review_required"] is True
    assert "This guide does not connect broker." in guide["disclaimer"]
