from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_inputs
from trading_core.equity_owner_v090_rc.documentation_freeze import build_documentation_freeze_result


def test_v090_documentation_freeze_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_inputs(paths)
    docs = build_documentation_freeze_result(paths=paths, as_of_date=AS_OF_DATE)
    assert docs["documentation_freeze_run"] is True
    assert docs["known_blocked_owner_readiness_state_documented"] is True
