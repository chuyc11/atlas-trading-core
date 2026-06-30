from trading_core.equity_owner_readiness_recovery_execution.audit_only_evidence import forbidden_verification_commands
from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_audit_only_verification_evidence_rejects_forbidden_commands(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    evidence = execution_data(paths, "audit_only_verification_evidence.json")
    assert evidence["does_not_execute_commands"] is True
    assert evidence["forbidden_verification_commands_detected"] == []
    assert forbidden_verification_commands(["python -m trading_core.cli run-daily"]) == ["python -m trading_core.cli run-daily"]
