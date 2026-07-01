from trading_core.equity_owner_evidence_backed_reevaluation_prep.gap_decision import build_remaining_evidence_gap_decision


def test_remaining_evidence_gap_decision_blocks_when_blockers_exist():
    decision = build_remaining_evidence_gap_decision(
        gaps={"gap_count": 1, "items": [{"gap_id": "G1"}]},
        blockers={"blocker_count": 1, "items": [{"gap_id": "G1"}]},
        sufficiency={"ready_for_controlled_gate_reevaluation": False},
    )
    assert decision["blocking_gap_count"] == 1
    assert decision["blocks_controlled_gate_reevaluation"] is True

