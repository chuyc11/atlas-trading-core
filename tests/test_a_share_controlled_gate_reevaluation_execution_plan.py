from trading_core.equity_owner_controlled_gate_reevaluation.execution_plan import build_reevaluation_execution_plan


def test_controlled_gate_reevaluation_execution_plan_not_executed():
    plan = build_reevaluation_execution_plan(prerequisite_validation={"reevaluation_prerequisites_met": False, "failed_prerequisites": ["x"]})
    assert plan["execution_status"] == "not_executed"
    assert plan["rerun_owner_readiness_gate"] is False
    assert plan["new_gate_decision_generated"] is False

