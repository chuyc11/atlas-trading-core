from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths as make_paths, seed_recovery_evidence_outputs
from trading_core.equity_owner_evidence_backed_reevaluation_prep.io import load_json


def seed_evidence_backed_prep_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_recovery_evidence_outputs(paths, as_of_date)
    from trading_core.equity_owner_recovery_evidence.recovery_evidence_audit import audit_a_share_owner_recovery_evidence

    audit_a_share_owner_recovery_evidence(as_of_date=as_of_date, paths=paths)


def seed_evidence_backed_prep_outputs(paths, as_of_date: str = AS_OF_DATE):
    seed_evidence_backed_prep_inputs(paths, as_of_date)
    from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_builder import build_a_share_owner_evidence_backed_reevaluation_prep

    return build_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=as_of_date, paths=paths)


def prep_data(paths, name: str, as_of_date: str = AS_OF_DATE):
    return load_json(paths.data_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date / name)
