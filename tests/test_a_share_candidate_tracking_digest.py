import json

from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.candidate_digest import build_candidate_tracking_digest


def test_candidate_tracking_digest_avoids_buy_list_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_candidate_tracking_digest(paths=paths, as_of_date=AS_OF_DATE)
    text = json.dumps(digest, ensure_ascii=False)

    assert digest["digest_id"] == "A-SHARE-CANDIDATE-TRACKING-DIGEST"
    assert digest["not_trade_instruction"] is True
    assert "买入建议" not in text
    assert "推荐买入" not in text
    assert "买入信号" not in text
