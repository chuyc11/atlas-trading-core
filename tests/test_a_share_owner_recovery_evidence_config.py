from trading_core.equity_owner_recovery_evidence.evidence_config import RecoveryEvidenceConfig, TARGET_VERSION, validate_config


def test_recovery_evidence_config_defaults():
    config = RecoveryEvidenceConfig().to_dict(source_gate_decision="blocked", source_readiness_score=54, minimum_owner_readiness_score=75)
    assert config["target_version"] == TARGET_VERSION
    assert config["mode"] == "collect_recovery_evidence"
    assert config["rerun_owner_readiness_gate"] is False
    assert config["generate_new_gate_score"] is False
    assert config["does_not_auto_waive"] is True


def test_recovery_evidence_config_rejects_invalid_mode():
    assert validate_config(RecoveryEvidenceConfig(mode="bad"))

