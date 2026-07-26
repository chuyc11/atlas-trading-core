from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths as make_paths, seed_controlled_gate_reevaluation_outputs
from trading_core.equity_owner_recovery_evidence.io import load_json


def seed_recovery_evidence_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_controlled_gate_reevaluation_outputs(paths, as_of_date)
    from trading_core.equity_owner_controlled_gate_reevaluation.controlled_reevaluation_audit import audit_a_share_owner_controlled_gate_reevaluation

    audit_a_share_owner_controlled_gate_reevaluation(as_of_date=as_of_date, paths=paths)


def seed_recovery_evidence_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_recovery_evidence_inputs(paths, as_of_date)
    from trading_core.equity_owner_recovery_evidence.evidence_builder import build_a_share_owner_recovery_evidence

    return build_a_share_owner_recovery_evidence(as_of_date=as_of_date, paths=paths)


def recovery_evidence_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_recovery_evidence" / "daily" / as_of_date / name)
