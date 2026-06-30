import json

from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.daily_pack_history_audit import audit_a_share_owner_daily_pack_history


def test_owner_daily_pack_history_audit_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    audit = audit_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []


def test_owner_daily_pack_history_audit_blocks_invalid_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    score_path = paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "owner_readiness_score.json"
    score = json.loads(score_path.read_text(encoding="utf-8"))
    score["score"] = 101
    score_path.write_text(json.dumps(score, ensure_ascii=False), encoding="utf-8")
    audit = audit_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert "owner_readiness_score_valid" in audit["blocking_reasons"]
