from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.research_digest import build_research_output_digest


def test_research_output_digest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_research_output_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["digest_id"] == "A-SHARE-RESEARCH-OUTPUT-DIGEST"
    assert digest["source_workflow_mode"] == "build_from_existing_data"
    assert digest["candidate_summary_available"] is True
    assert digest["virtual_portfolio_summary_available"] is True
    assert digest["not_trade_instruction"] is True
