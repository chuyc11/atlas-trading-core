from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_to_gate_mapping import build_evidence_to_gate_mapping


def test_evidence_to_gate_mapping_generated():
    mapping = build_evidence_to_gate_mapping(gaps={"items": [{"gap_id": "G1", "blocks_next_reevaluation_prep": True}]}, sufficiency={"ready_for_controlled_gate_reevaluation": False})
    assert mapping["mapping_id"] == "A-SHARE-EVIDENCE-TO-GATE-MAPPING"
    assert mapping["mapping_count"] == 1
    assert mapping["items"][0]["blocks_controlled_reevaluation"] is True

