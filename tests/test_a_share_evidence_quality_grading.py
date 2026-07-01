from trading_core.equity_owner_recovery_evidence.evidence_quality import build_evidence_quality_grading


def test_evidence_quality_grading_handles_enum_counts():
    quality = build_evidence_quality_grading(
        task_evidence={"items": [{"evidence_quality": "none"}, {"evidence_quality": "strong"}]},
        developer={"items": [{"evidence_quality": "partial"}]},
        owner={"items": [{"evidence_quality": "weak"}, {"evidence_quality": "audit_verified"}]},
    )
    assert quality["missing_evidence_count"] == 1
    assert quality["strong_evidence_count"] == 1
    assert quality["audit_verified_evidence_count"] == 1
    assert quality["evidence_ready_for_next_reevaluation_prep"] is False

