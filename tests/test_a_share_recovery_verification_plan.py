from trading_core.equity_owner_readiness_recovery.verification_plan import _forbidden_commands
from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_verification_plan_rejects_forbidden_commands(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    plan = recovery_data(paths, "recovery_verification_plan.json")
    assert plan["forbidden_verification_commands_detected"] == []
    assert _forbidden_commands(["python -m trading_core.cli run-daily"]) == ["python -m trading_core.cli run-daily"]
