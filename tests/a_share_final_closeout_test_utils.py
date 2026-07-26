from __future__ import annotations

from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, seed_research_evidence_inputs
from trading_core.equity_readiness_final_closeout import build_a_share_final_not_ready_closeout
from trading_core.equity_research_evidence_accumulation import (
    audit_a_share_research_evidence_accumulation_and_prep,
    build_a_share_research_evidence_accumulation_and_prep,
)


def seed_v095_and_build_v096(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)
    audit_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)
    result = build_a_share_final_not_ready_closeout(paths=paths, as_of_date=AS_OF_DATE)
    return paths, result


def final_json(paths, name: str) -> dict:
    return phase_json(paths, name)


def phase_json(paths, name: str) -> dict:
    from tests.a_share_research_evidence_test_utils import read_json

    return read_json(paths.data_dir / "equity_readiness_final_closeout" / "daily" / AS_OF_DATE / f"{name}.json")
