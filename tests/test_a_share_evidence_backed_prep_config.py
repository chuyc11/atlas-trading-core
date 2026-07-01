from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import EVALUATE_SUFFICIENCY, EvidenceBackedPrepConfig, validate_config


def test_evidence_backed_prep_config_defaults_and_mode_validation():
    config = EvidenceBackedPrepConfig()
    payload = config.to_dict(source_gate_decision="blocked", source_readiness_score=54, minimum_owner_readiness_score=75)
    assert config.mode == EVALUATE_SUFFICIENCY
    assert payload["generate_new_gate_score"] is False
    assert payload["does_not_lower_threshold"] is True
    assert validate_config(config) == []
    assert validate_config(EvidenceBackedPrepConfig(mode="bad_mode"))

