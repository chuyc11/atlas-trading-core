import json

from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core.equity_owner_daily_pack.portfolio_digest import build_virtual_portfolio_digest


def test_virtual_portfolio_digest_avoids_real_portfolio_claims(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)

    digest = build_virtual_portfolio_digest(paths=paths, as_of_date=AS_OF_DATE)
    text = json.dumps(digest, ensure_ascii=False)

    assert digest["digest_id"] == "A-SHARE-VIRTUAL-PORTFOLIO-DIGEST"
    assert digest["paper_ledger_only"] is True
    assert digest["not_real_portfolio"] is True
    assert "实盘组合" not in text
