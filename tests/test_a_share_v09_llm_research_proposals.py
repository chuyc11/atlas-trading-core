from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_v09_daily_platform


def test_v09_llm_research_proposals_use_deterministic_mock_and_pending_status(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    proposals = platform_json(paths, "v09_llm_research_proposal_register")

    assert proposals["engine"] == "deterministic_template_mock_no_external_api"
    assert proposals["external_llm_api_called"] is False
    assert proposals["trade_instructions_generated"] is False
    assert all(item["status"] == "pending_experiment" for item in proposals["proposals"])
