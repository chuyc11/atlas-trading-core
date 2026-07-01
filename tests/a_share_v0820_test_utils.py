from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_outputs
from trading_core.equity_owner_v0820_gate_outcome.io import load_json


def seed_v0820_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_evidence_backed_prep_outputs(paths, as_of_date)
    from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_backed_prep_audit import audit_a_share_owner_evidence_backed_reevaluation_prep

    audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=as_of_date, paths=paths)


def seed_v0820_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_v0820_inputs(paths, as_of_date)
    from trading_core.equity_owner_v0820_gate_outcome.outcome_builder import build_a_share_owner_v0820_gate_outcome

    return build_a_share_owner_v0820_gate_outcome(as_of_date=as_of_date, paths=paths)


def v0820_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_v0820_gate_outcome" / "daily" / as_of_date / name)

